import asyncio
import ipaddress
import os
import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from aiogram import Bot, Dispatcher, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, Message
from dotenv import load_dotenv
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "49"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_FILES_PER_LINK = 10

dp = Dispatcher()
URL_RE = re.compile(r"https?://[^\s<>()\"']+", re.IGNORECASE)


def extract_url(text: str) -> str | None:
    match = URL_RE.search(text or "")
    if not match:
        return None
    return match.group(0).strip(".,;:!?)]}")


def is_valid_public_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False

    host = (parsed.hostname or "").lower()
    if host in {"localhost"} or host.endswith(".local"):
        return False

    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return True

    return not (ip.is_private or ip.is_loopback or ip.is_link_local)


def download_with_ytdlp(url: str, folder: Path) -> list[Path]:
    options = {
        "outtmpl": str(folder / "%(extractor)s_%(id)s_%(title).80s.%(ext)s"),
        "format": f"best[filesize<={MAX_FILE_SIZE_MB}M][ext=mp4]/best[filesize<={MAX_FILE_SIZE_MB}M]/best[ext=mp4]/best",
        "max_filesize": MAX_FILE_SIZE_BYTES,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
        "retries": 3,
        "fragment_retries": 3,
        "socket_timeout": 30,
    }

    with YoutubeDL(options) as ydl:
        ydl.extract_info(url, download=True)

    files = [
        path
        for path in folder.rglob("*")
        if path.is_file() and path.suffix not in {".part", ".ytdl", ".tmp"}
    ]
    return sorted(files, key=lambda path: path.stat().st_size, reverse=True)


def error_text(error: Exception) -> str:
    text = str(error).lower()

    if "larger than max-filesize" in text or "file is too large" in text:
        return f"Файл слишком большой. Максимум для этого бота: {MAX_FILE_SIZE_MB} МБ."

    if "unsupported url" in text or "no suitable extractor" in text:
        return "Этот сайт или формат ссылки не поддерживается yt-dlp."

    if any(word in text for word in ("login", "private", "cookies", "403", "forbidden")):
        return "Не удалось скачать файл. Бот работает только с публичным контентом без авторизации."

    return "Не удалось скачать файл. Проверьте ссылку или попробуйте другой публичный пост."


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "Пришлите публичную ссылку на фото или видео из TikTok, Instagram, YouTube Shorts, X/Twitter, VK или другого сайта. "
        "Я попробую скачать файл и отправить его обратно."
    )


@dp.message(F.text)
async def handle_text(message: Message) -> None:
    url = extract_url(message.text or "")

    if not url or not is_valid_public_url(url):
        await message.answer("Пожалуйста, отправьте корректную публичную ссылку, начинающуюся с http:// или https://.")
        return

    status = await message.answer("Скачиваю файл...")
    temp_dir = Path(tempfile.mkdtemp(prefix="telegram_download_"))

    try:
        files = await asyncio.to_thread(download_with_ytdlp, url, temp_dir)

        if not files:
            await status.edit_text("Файл не найден. Возможно, сайт не поддерживается или контент закрыт.")
            return

        files = files[:MAX_FILES_PER_LINK]

        for file_path in files:
            if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
                await message.answer(f"Файл слишком большой. Максимум для этого бота: {MAX_FILE_SIZE_MB} МБ.")
                continue

            try:
                await message.answer_document(FSInputFile(file_path), caption="Готово")
            except TelegramBadRequest:
                await message.answer(f"Telegram не принял файл. Возможно, он больше {MAX_FILE_SIZE_MB} МБ.")

        await status.delete()

    except DownloadError as error:
        await status.edit_text(error_text(error))
    except Exception:
        await status.edit_text("Произошла ошибка при обработке ссылки. Попробуйте позже.")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@dp.message()
async def handle_other(message: Message) -> None:
    await message.answer("Отправьте текстовое сообщение с публичной ссылкой на фото или видео.")


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не найден. Добавьте его в .env или в переменные окружения сервера.")

    bot = Bot(token=BOT_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
