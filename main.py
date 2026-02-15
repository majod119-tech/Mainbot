import os
import openpyxl
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from keep_alive import keep_alive  # لضمان بقاء السيرفر حياً في Render

# جلب التوكن من الخزنة السرية بـ Render (المفتاح: TELEGRAM_TOKEN)
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# دالة الترحيب عند الضغط على /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["👨‍🎓 متدرب"], ["👨‍🏫 مدرب"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "مرحباً بك في بوت المعهد الصناعي الثانوي ببريدة 🤖\nنسعد بخدمتكم وتسهيل وصولكم للمعلومات.",
        reply_markup=reply_markup
    )

# دالة معالجة الرسائل والبحث في الإكسيل
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

    # معالجة البحث إذا كان البوت ينتظر رقم هوية
    if context.user_data.get("awaiting_id"):
        id_number = text.strip()
        context.user_data["awaiting_id"] = False
        found = False
        
        try:
            # فتح ملف الطلاب من مجلد data
            file_path = "data/students.xlsx"
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active
            
            # تحديد أعمدة البحث بناءً على العناوين في الصف الأول
            headers = [str(cell.value).strip() if cell.value else "" for cell in sheet[1]]
            id_col = headers.index("رقم الهوية") if "رقم الهوية" in headers else -1
            trainee_col = headers.index("رقم المتدرب") if "رقم المتدرب" in headers else -1

            if id_col == -1:
                await update.message.reply_text("⚠️ خطأ: عمود 'رقم الهوية' غير موجود في ملف الإكسيل.")
                return

            for row in sheet.iter_rows(min_row=2, values_only=True):
                # تنظيف رقم الهوية من أي فواصل عشرية قد يضيفها الإكسيل
                current_id = str(row[id_col]).strip().replace('.0', '')
                
                if current_id == id_number:
                    trainee_id = str(row[trainee_col]).strip().replace('.0', '') if trainee_col != -1 else "غير متوفر"
                    await update.message.reply_text(
                        f"✅ تم العثور على بياناتك:\n\n🔢 الرقم التدريبي: `{trainee_id}`",
                        parse_mode="Markdown"
                    )
                    found = True
                    break
                    
        except FileNotFoundError:
            await update.message.reply_text("⚠️ ملف الطلاب (students.xlsx) غير موجود في مجلد data.")
            return
        except Exception as e:
            await update.message.reply_text(f"⚠️ حدث خطأ أثناء القراءة: {e}")
            return

        if not found:
            await update.message.reply_text("🔍 عذراً، لم يتم العثور على بيانات لهذا الرقم.")
        return

def main():
    if not TOKEN:
        print("❌ خطأ: التوكن غير موجود في إعدادات Render!")
        return

    # تشغيل نظام البقاء حياً
    keep_alive()
    
    # بناء وتشغيل البوت
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 البوت يعمل الآن بنجاح...")
    application.run_polling()

if __name__ == "__main__":
    main()
