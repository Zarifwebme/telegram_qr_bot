import logging
import qrcode
import tempfile
import os
from telegram import Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# Logger sozlamalari
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

user_ids = set()

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

def generate_qr(data):
    try:
        qr = qrcode.make(data)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        qr.save(temp_file.name)
        return temp_file.name
    except Exception as e:
        logger.error(f"QR kod yaratishda xatolik: {e}")
        raise e

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_ids.add(update.message.from_user.id)
        await update.message.reply_text("Assalomu alaykum! Matn yoki URL yuboring (200 belgidan oshmasin).")
    except Exception as e:
        logger.error(f"/start komandasida xatolik: {e}")
        await update.message.reply_text("Xatolik yuz berdi! Qayta urinib ko'ring.")

async def generate_qr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_ids.add(update.message.from_user.id)
        text = update.message.text
        if len(text) > 200:
            await update.message.reply_text("Xatolik: Matn 200 belgidan oshmasligi kerak!")
            return
        file_path = generate_qr(text)
        with open(file_path, "rb") as photo:
            await update.message.reply_photo(photo=photo)
        await update.message.reply_text("QR kodingiz tayyor!")
        os.remove(file_path)
    except Exception as e:
        logger.error(f"QR kod generatsiyasida xatolik: {e}")
        await update.message.reply_text("Xatolik yuz berdi! Qayta urinib ko'ring.")

async def user_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(f"Foydalanuvchilar soni: {len(user_ids)}")
    except Exception as e:
        logger.error(f"/usercount komandasida xatolik: {e}")
        await update.message.reply_text("Xatolik yuz berdi! Qayta urinib ko'ring.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.error(f"Global xatolik: {context.error}")
        if update and update.effective_user:
            await context.bot.send_message(chat_id=update.effective_user.id, text="Xatolik yuz berdi! Admin bilan bog'laning.")
    except Exception as e:
        logger.error(f"Xatolik haqida xabar yuborishda muammo: {e}")

def main():
    try:
        application = ApplicationBuilder().token(TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("usercount", user_count))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_qr_handler))

        application.add_error_handler(error_handler)

        application.run_polling()
    except Exception as e:
        logger.critical(f"Botni ishga tushirishda xatolik: {e}")

if __name__ == "__main__":
    main()
