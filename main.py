import os
import openpyxl
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from keep_alive import keep_alive

# جلب التوكن من الخزنة السرية بـ Render
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# 1. دالة الترحيب والواجهة الرئيسية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["👨‍🎓 متدرب"], ["👨‍🏫 مدرب"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "مرحباً بك في بوت المعهد الصناعي الثانوي ببريدة 🤖\nنسعد بخدمتكم وتسهيل وصولكم للمعلومات.",
        reply_markup=reply_markup
    )

# 2. دالة معالجة الرسائل والبحث
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "👨‍🎓 متدرب":
        keyboard = [["🔍 معرفة رقمي التدريبي"], ["🔙 عودة"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("خدمات المتدربين:", reply_markup=reply_markup)
        return

    if text == "🔍 معرفة رقمي التدريبي":
        context.user_data["awaiting_id"] = True
        await update.message.reply_text("🔢 من فضلك أرسل رقم الهوية للاستعلام:")
        return

    if text == "🔙 عودة":
        await start(update, context)
        return

    # تنفيذ عملية البحث في الإكسيل
    if context.user_data.get("awaiting_id"):
        id_number = text.strip()
        context.user_data["awaiting_id"] = False
        
        try:
            # مسار الملف في مجلد data كما في صورتك
            file_path = "data/students.xlsx"
            if not os.path.exists(file_path):
                await update.message.reply_text("⚠️ عذراً، ملف البيانات غير موجود حالياً.")
                return

            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active
            
            # البحث عن العناوين تلقائياً
            headers = [str(cell.value).strip() if cell.value else "" for cell in sheet[1]]
            id_col = headers.index("رقم الهوية") if "رقم الهوية" in headers else 0
            trainee_col = headers.index("رقم المتدرب") if "رقم المتدرب" in headers else 1

            found = False
            for row in sheet.iter_rows(min_row=2, values_only=True):
                # تنظيف البيانات المقروءة
                current_id = str(row[id_col]).strip().replace('.0', '')
                if current_id == id_number:
                    trainee_id = str(row[trainee_col]).strip().replace('.0', '')
                    await update.message.reply_text(f"✅ تم العثور على بياناتك:\n\n🔢 الرقم التدريبي: `{trainee_id}`", parse_mode="Markdown")
                    found = True
                    break
            
            if not found:
                await update.message.reply_text("🔍 عذراً، لم يتم العثور على بيانات لهذا الرقم.")

        except Exception as e:
            await update.message.reply_text(f"⚠️ خطأ فني أثناء البحث: {e}")
        return

# 3. تشغيل البوت
def main():
    if not TOKEN:
        print("❌ خطأ: التوكن مفقود في إعدادات Render!")
        return

    keep_alive() # لتشغيل السيرفر الموضح في صورتك رقم 5
    
    # بناء البوت (استخدام الطريقة المتوافقة مع 3.11)
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 البوت يعمل بكامل طاقته الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
