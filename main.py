import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from keep_alive import keep_alive

# هنا الكود يروح يبحث في Render عن اسم "TELEGRAM_TOKEN"
TOKEN = os.environ.get("TELEGRAM_TOKEN")

async def start(update, context):
    await update.message.reply_text("✅ أهلاً بك! البوت شغال الآن بأمان من الخزنة السرية.")

def main():
    if not TOKEN:
        print("❌ خطأ: لم يتم العثور على التوكن في الخزنة السرية (TELEGRAM_TOKEN)")
        return

    keep_alive()
    
    # بناء البوت باستخدام التوكن المسحوب من الخزنة
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    
    print("🚀 البوت انطلق بنجاح...")
    application.run_polling()

if __name__ == '__main__':
    main()
