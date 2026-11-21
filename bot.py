import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import yt_dlp

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Загружаем токен из переменных окружения Render
TOKEN = os.getenv("BOT_TOKEN")

# Заглушка, чтобы Render видел открытый порт и не выдавал ошибку Timeout
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

# Запускаем сервер в фоновом потоке
threading.Thread(target=run_dummy_server, daemon=True).start()

async def start(update: Update, context):
    await update.message.reply_text("Привет! Отправь мне название песни или ссылку, и я скачаю её для тебя.")

async def download_music(update: Update, context):
    query = update.message.text
    await update.message.reply_text("🔍 Ищу и скачиваю трек...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'ytsearch1',
        'outtmpl': 'song.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            filename = ydl.prepare_filename(info)
            filename = filename.rsplit('.', 1)[0] + '.mp3'

        with open(filename, 'rb') as audio:
            await update.message.reply_audio(audio)

        os.remove(filename)

    except Exception as e:
        logging.error(f"Ошибка скачивания: {e}")
        await update.message.reply_text("❌ Произошла ошибка при скачивании трека.")

def main():
    if not TOKEN:
        logging.error("Токен BOT_TOKEN не найден в переменных окружения!")
        return

    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_music))

    application.run_polling()

if __name__ == '__main__':
    main()
    
