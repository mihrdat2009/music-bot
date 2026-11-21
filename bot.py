import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import yt_dlp

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне название трека или ссылку.")

async def download_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text("🔍 Ищу и скачиваю трек...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'ytsearch1',
        'noplaylist': True,
        'extract_flat': False,
        'outtmpl': 'song.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as audio:
            await update.message.reply_audio(audio)

        os.remove(filename)

    except Exception as e:
        logging.error(f"Ошибка скачивания: {e}")
        await update.message.reply_text("❌ Ошибка при скачивании трека.")

def main():
    if not TOKEN:
        logging.error("9209775991:AAF6UA6h_CClMQhi3d09ECQzLlK04TRkCLw")
        return

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_music))
    application.run_polling()

if __name__ == '__main__':
    main()
