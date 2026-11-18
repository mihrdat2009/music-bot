import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import yt_dlp

TOKEN = "9209775991:AAF6UA6h_CClMQhi3d09ECQzLlK04TRkCLw"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 **Mihrdat Music Bot**\n\n"
        "Отправь мне ссылку на YouTube, и я скачаю трек!"
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.startswith(("https://", "http://")):
        await update.message.reply_text("❌ Неверная ссылка.")
        return

    await update.message.reply_text("⏳ Скачиваю трек с YouTube, подожди немного...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'restrictfilenames': True,
    }

    audio_filename = None
    try:
        os.makedirs("downloads", exist_ok=True)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_filename = ydl.prepare_filename(info)
            
            duration = int(info.get('duration', 0))
            title = info.get('title', 'Трек с YouTube')
            uploader = info.get('uploader', 'Неизвестен автор')

        with open(audio_filename, 'rb') as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                performer=uploader,
                title=title,
                duration=duration,
                caption=f"🎵 **{title}**\n👤 Автор: {uploader}\n⏱ Длительность: {duration // 60}:{(duration % 60):02d}"
            )

    except Exception as e:
        print(e)
        await update.message.reply_text("❌ Ошибка при скачивании трека.")

    finally:
        if audio_filename and os.path.exists(audio_filename):
            try:
                os.remove(audio_filename)
            except:
                pass

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    print("Mihrdat Music Bot запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
          
