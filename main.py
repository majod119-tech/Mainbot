import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from keep_alive import keep_alive

# جلب التوكن من الخزنة السرية بـ Render (المفتاح: TELEGRAM_TOKEN)
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# دالة الترحيب والواجهة الرئيسية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["👨‍🎓 متدرب"], ["👨‍🏫 مدرب"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "مرحباً بك في بوت المعهد الصناعي الثانوي ببريدة 🤖\nالآن البوت في وضع التشغيل التجريبي (بدون ميزة البحث).",
        reply_markup=reply_markup
    )

# دالة معالجة الرسائل والأزرار
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "👨‍🎓 متدرب":
        keyboard = [["🔍 معرفة رقمي التدريبي (قيد الصيانة)"], ["🔙 عودة"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("خدمات المتدربين متاحة، لكن ميزة البحث تحت الصيانة حالياً.", reply_markup=reply_markup)
        return

    if text == "👨‍🏫 مدرب":
        keyboard = [["📋 خدمات المدربين"], ["🔙 عودة"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("أهلاً بك يا مهندس، هذه الواجهة مخصصة للمدربين.", reply_markup=reply_markup)
        return

    if text == "🔙 عودة":
        await start(update, context)
        return

    # رسالة افتراضية لأي نص آخر
    await update.message.reply_text("أنا استلمت رسالتك: " + text + "\nالبوت يعمل والاتصال ممتاز! ✅")

def main():
    if not TOKEN:
        print("❌ خطأ: لم يتم العثور على التوكن (TELEGRAM_TOKEN) في الإعدادات.")
        return

    # تشغيل نظام البقاء حياً للبوت
    keep_alive()
    
    # بناء البوت باستخدام التوكن الجديد
    application = ApplicationBuilder().token(TOKEN).build()
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 البوت يعمل الآن بجميع الخدمات الأساسية...")
    application.run_polling()

if __name__ == "__main__":
    main()
