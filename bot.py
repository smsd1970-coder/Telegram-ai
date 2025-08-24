from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode
import os, io, logging
from dotenv import load_dotenv
from utils import (
    get_signal_report,
    set_default_symbol, get_default_symbol,
    analyze_photo_optional
)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_SYMBOL = os.getenv("SYMBOL", "XAUUSD=X")

def start(update, context):
    update.message.reply_text(
        "أهلاً 👋\n"
        "/signal (1m & 5m)\n/signal_1m\n/signal_5m\n/trend\n/zones\n/setpair SYMBOL\n"
        "أرسل صورة للشارت لأحللها (إذا مفعّل OPENAI_API_KEY)."
    )

def help_cmd(update, context): return start(update, context)

def signal(update, context):
    text = get_signal_report(get_default_symbol(), intervals=["1m","5m"])
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

def signal_1m(update, context):
    text = get_signal_report(get_default_symbol(), intervals=["1m"])
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

def signal_5m(update, context):
    text = get_signal_report(get_default_symbol(), intervals=["5m"])
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

def trend(update, context):
    text = get_signal_report(get_default_symbol(), intervals=["1m"], only="trend")
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

def zones(update, context):
    text = get_signal_report(get_default_symbol(), intervals=["5m"], only="zones")
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

def setpair(update, context):
    if not context.args:
        update.message.reply_text("اكتب: /setpair XAUUSD=X أو GC=F أو EURUSD=X …"); return
    sym = context.args[0].strip(); set_default_symbol(sym)
    update.message.reply_text(f"تم ضبط الزوج: `{sym}`", parse_mode=ParseMode.MARKDOWN)

def photo_handler(update, context):
    if not OPENAI_API_KEY:
        update.message.reply_text("فعّل OPENAI_API_KEY لتحليل الصور."); return
    photo = update.message.photo[-1]; file = context.bot.get_file(photo.file_id)
    bio = io.BytesIO(); file.download(out=bio); bio.seek(0)
    try:
        result = analyze_photo_optional(bio.getvalue(), api_key=OPENAI_API_KEY)
        update.message.reply_text(result, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.exception(e); update.message.reply_text("تعذر تحليل الصورة حالياً.")

def main():
    if not BOT_TOKEN: raise RuntimeError("BOT_TOKEN غير موجود (أضفه بالـ Secrets أو .env)")
    updater = Updater(BOT_TOKEN, use_context=True); dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start)); dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("signal", signal)); dp.add_handler(CommandHandler("signal_1m", signal_1m))
    dp.add_handler(CommandHandler("signal_5m", signal_5m)); dp.add_handler(CommandHandler("trend", trend))
    dp.add_handler(CommandHandler("zones", zones)); dp.add_handler(CommandHandler("setpair", setpair))
    dp.add_handler(MessageHandler(Filters.photo, photo_handler))
    updater.start_polling(); updater.idle()

if __name__ == "__main__": main()
