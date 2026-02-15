import os
import openpyxl
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from keep_alive import keep_alive

# جلب التوكن من الخزنة السرية بـ Render (المفتاح: TELEGRAM_TOKEN)
TOKEN = os.environ.get("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["👨‍🎓 متدرب"], ["🔙 عودة"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "مرحباً بك في بوت المعهد الصناعي الثانوي ببريدة 🤖\nنسعد بخدمتكم وتسهيل وصولكم للمعلومات.",
        reply_markup=reply_markup
    )

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

    if context.user_data.get("awaiting_id"):
        id_number = text.strip()
        context.user_data["awaiting_id"] = False
        
        try:
            # مسار الملف كما يظهر في صورتك رقم 7
            file_path = "data/students.xlsx"
            if not os.path.exists(file_path):
                await update.message.reply_text("⚠️ ملف البيانات غير موجود في مجلد data.")
                return

            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active
            
            headers = [str(cell.value).strip() if cell.value else "" for cell in sheet[1]]
            id_col = headers.index("رقم الهوية") if "رقم الهوية" in headers else -1
            trainee_col = headers.index("رقم المتدرب") if "رقم المتدرب" in headers else -1

            found = False
            for row in sheet.iter_rows(min_row=2, values_only=True):
                current_id = str(row[id_col]).strip().replace('.0', '') if id_col != -1 else ""
                if current_id == id_number:
                    trainee_id = str(row[trainee_col]).strip().replace('.0', '') if trainee_col != -1 else "غير متوفر"
                    await update.message.reply_text(f"✅ تم العثور على بياناتك:\n\n🔢 الرقم التدريبي: `{trainee_id}`", parse_mode="Markdown")
                    found = True
                    break
            
            if not found:
                await update.message.reply_text("🔍 عذراً، لم يتم العثور على بيانات لهذا الرقم.")

        except Exception as e:
            await update.message.reply_text(f"⚠️ خطأ تقني: {e}")
        return

def main():
    if not TOKEN:
        print("❌ خطأ: التوكن مفقود في إعدادات Render!")
        return

    # تشغيل السيرفر الوهمي الموضح في صورتك رقم 5
    keep_alive() 
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 البوت يعمل الآن بنجاح...")
    app.run_polling()

if __name__ == "__main__":
    main()
