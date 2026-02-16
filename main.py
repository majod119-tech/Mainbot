import os
import uuid
import qrcode
import openpyxl
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
from keep_alive import keep_alive

# جلب التوكن من إعدادات Render
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# إنشاء مجلد للتظلمات إذا لم يكن موجوداً
if not os.path.exists("complaints"):
    os.makedirs("complaints")

# دالة البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear() # تنظيف أي عمليات سابقة
    keyboard = [["✅ ابدأ"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "مرحباً بك في البوت الرسمي للمعهد الصناعي الثانوي ببريدة 🤖\nنسعد بخدمتكم وتسهيل وصولكم للمعلومات والخدمات التدريبية.\n\nاضغط على الزر أدناه للبدء:",
        reply_markup=reply_markup)

# دالة معالجة الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # ================== (1. معالجة حالات الانتظار والبحث) ==================
    
    # حالة البحث عن الرقم التدريبي (متدرب)
    if context.user_data.get("awaiting_id"):
        id_number = text.strip()
        context.user_data["awaiting_id"] = False
        
        try:
            file_path = "data/students.xlsx"
            if not os.path.exists(file_path):
                await update.message.reply_text("⚠️ عذراً، ملف البيانات غير موجود حالياً.")
                return

            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active
            
            headers = [str(cell.value).strip() if cell.value else "" for cell in sheet[1]]
            id_col = headers.index("رقم الهوية") if "رقم الهوية" in headers else -1
            trainee_col = headers.index("رقم المتدرب") if "رقم المتدرب" in headers else -1

            found = False
            if id_col != -1 and trainee_col != -1:
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    current_id = str(row[id_col]).strip().replace('.0', '')
                    if current_id == id_number:
                        trainee_id = str(row[trainee_col]).strip().replace('.0', '')
                        await update.message.reply_text(f"✅ تم العثور على بياناتك:\n\n🔢 الرقم التدريبي: `{trainee_id}`\n\nيمكنك استخدامه لتسجيل الدخول في أنظمة المؤسسة.", parse_mode="Markdown")
                        found = True
                        break
            
            if not found:
                await update.message.reply_text("🔍 عذراً، لم يتم العثور على بيانات مرتبطة بهذا الرقم. يرجى التأكد أو مراجعة القبول والتسجيل.")
        except Exception as e:
            await update.message.reply_text("⚠️ حدث خطأ تقني أثناء قراءة ملف البيانات.")
        return

    # حالة إنشاء باركود التظلم
    if context.user_data.get("complaint_state"):
        complaint_id = str(uuid.uuid4())[:8]
        file_path = f"complaints/{complaint_id}.txt"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)

        qr = qrcode.make(f"رقم التظلم: {complaint_id}")
        qr_path = f"complaints/{complaint_id}.png"
        qr.save(qr_path)

        try:
            with open(qr_path, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=f"✅ تم استلام تظلمك\n🔢 رقم التظلم: {complaint_id}\nاحتفظ بالـ QR Code للمتابعة"
                )
        except Exception:
            await update.message.reply_text(f"✅ تم استلام تظلمك برقم: {complaint_id}")
            
        context.user_data["complaint_state"] = False
        return

    # ================== (2. القوائم الرئيسية والتنقل) ==================

    if text == "✅ ابدأ" or text == "🔙 عودة":
        context.user_data.clear()
        keyboard = [["👨‍🏫 مدرب"], ["👨‍🎓 متدرب"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("يرجى اختيار المستخدم:", reply_markup=reply_markup)
        return

    # === واجهة المدرب ===
    elif text == "👨‍🏫 مدرب":
        keyboard = [["تظلم المدرب"], ["وصف المقررات"], ["المراجع التدريبية"], ["🔙 عودة"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("مرحباً بك عزيزي المدرب في بوت خدمات المعهد الصناعي الثانوي ببريدة.", reply_markup=reply_markup)
        return

    elif text == "تظلم المدرب":
        try:
            with open("assets/trainer_complaint_guide.pdf", "rb") as file:
                await update.message.reply_document(document=file, filename="ضوابط_تظلم_المدربين.pdf", caption="📝 ضوابط وإجراءات التظلم أعضاء هيئة التدريب")
        except FileNotFoundError:
            await update.message.reply_text("⚠️ عذراً، الملف غير متوفر في النظام حالياً (assets/trainer_complaint_guide.pdf).")
        return

    elif text == "وصف المقررات":
        await update.message.reply_text("📚 وصف المقررات (المعاهد الصناعية):\n\nيمكنك الوصول لوصف المقررات والخطط من خلال الرابط التالي:\nhttps://tvtc.gov.sa/ar/Departments/tvtcdepartments/cdd/Pages/plans.aspx?RootFolder=/ar/Departments/tvtcdepartments/cdd/DocLib/%D8%A7%D9%84%D9%85%D8%B9%D8%A7%D9%87%D8%AF+%D8%A7%D9%84%D8%B5%D9%86%D8%A7%D8%B9%D9%8A%D8%A9/%D8%A7%D9%84%D8%AB%D8%A7%D9%86%D9%88%D9%8A+%D8%A7%D9%84%D8%B5%D9%86%D8%A7%D8%B9%D9%8A")
        return

    # === واجهة المتدرب ===
    elif text == "👨‍🎓 متدرب":
        keyboard = [["المراجع التدريبية"], ["📕 دليل المتدرب"],
                    ["📅 التقويم التدريبي"], ["🚩 الخط الزمني لرايات"],
                    ["📚 أدلة رايات"], ["📝 رفع تظلم"],
                    ["🔍 معرفة رقمي التدريبي"], ["🔙 عودة"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("خدمات المتدربين:", reply_markup=reply_markup)
        return

    elif text == "🔍 معرفة رقمي التدريبي":
        context.user_data["awaiting_id"] = True
        await update.message.reply_text("🔢 من فضلك أرسل رقم الهوية لمعرفة رقمك التدريبي:")
        return

    elif text == "📕 دليل المتدرب":
        try:
            with open("assets/trainee_guide.pdf", "rb") as file:
                await update.message.reply_document(document=file, filename="دليل_المتدرب_١٤٤٧هـ.pdf", caption="📕 دليل المتدرب للعام التدريبي 1447هـ - 1448هـ")
        except FileNotFoundError:
            await update.message.reply_text("⚠️ عذراً، دليل المتدرب غير متوفر حالياً.")
        return

    elif text == "📅 التقويم التدريبي":
        try:
            with open("assets/calendar.jpg", "rb") as photo:
                await update.message.reply_photo(photo=photo, caption="📅 التقويم التدريبي للفصل الثاني 1447هـ - 1448هـ")
        except FileNotFoundError:
            await update.message.reply_text("⚠️ عذراً، صورة التقويم غير متوفرة حالياً.")
        return

    elif text == "🚩 الخط الزمني لرايات":
        try:
            with open("assets/timeline.pdf", "rb") as file:
                await update.message.reply_document(document=file, filename="الخط_الزمني_لرايات_١٤٤٧هـ.pdf", caption="🚩 الخط الزمني لأعمال الفصل التدريبي الثاني 1447هـ")
        except FileNotFoundError:
            await update.message.reply_text("⚠️ عذراً، الخط الزمني غير متوفر حالياً.")
        return

    elif text == "📚 أدلة رايات":
        await update.message.reply_text("📚 أدلة مستخدم نظام رايات:\n\nيمكنك الوصول لجميع الأدلة التعليمية والمصورة لنظام رايات عبر الرابط التالي:\nhttps://rayat.tvtc.gov.sa/Static/Guide.aspx")
        return

    elif text == "📝 رفع تظلم":
        await update.message.reply_text("📝 لرفع تظلمك، اضغط الرابط التالي:\nhttps://forms.gle/CvY7KBuJA66suK1D8")
        return

    # === المراجع التدريبية (مشتركة للمدرب والمتدرب) ===
    elif text == "المراجع التدريبية":
        keyboard = [["💻 الحاسب الآلي", "⚡ الكهرباء الانشائية"],
                    ["📚 الدراسات العامة", "❄️ التبريد والتكييف"],
                    ["🚗 ميكانيكا السيارات"], ["🔙 عودة"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("اختر القسم التدريبي المستهدف:", reply_markup=reply_markup)
        return

    elif text == "💻 الحاسب الآلي":
        await update.message.reply_text("💻 المراجع التدريبية لقسم الحاسب الآلي:\n\nيمكنك الوصول للحقائب التدريبية من خلال الرابط التالي:\nhttps://tvtc.gov.sa/ar/Departments/tvtcdepartments/cdd/Pages/packages.aspx?RootFolder=/ar/Departments/tvtcdepartments/cdd/DocLib1/%D8%A7%D9%84%D9%85%D8%B9%D8%A7%D9%87%D8%AF%20%D8%A7%D9%84%D8%B5%D9%86%D8%A7%D8%B9%D9%8A%D8%A9/%D8%A7%D9%84%D8%AD%D8%A7%D8%B3%D8%A8%20%D8%A7%D9%84%D8%A2%D9%84%D9%8A")
        return

    elif text == "⚡ الكهرباء الانشائية":
        await update.message.reply_text("⚡ المراجع التدريبية لقسم الكهرباء الانشائية:\n\nيمكنك الوصول للحقائب التدريبية من خلال الرابط التالي:\nhttps://tvtc.gov.sa/ar/Departments/tvtcdepartments/cdd/Pages/packages.aspx?RootFolder=/ar/Departments/tvtcdepartments/cdd/DocLib1/%D8%A7%D9%84%D9%85%D8%B9%D8%A7%D9%87%D8%AF%20%D8%A7%D9%84%D8%B5%D9%86%D8%A7%D8%B9%D9%8A%D8%A9/%D8%A7%D9%84%D9%83%D9%87%D8%B1%D8%A8%D8%A7%D8%A1/%D8%A7%D9%84%D9%83%D9%87%D8%B1%D8%A8%D8%A7%D8%A1%20%D8%A7%D9%84%D8%A5%D9%86%D8%B4%D8%A7%D8%A6%D9%8A%D8%A9")
        return

    elif text == "🚗 ميكانيكا السيارات":
        await update.message.reply_text("🚗 المراجع التدريبية لقسم ميكانيكا السيارات:\n\nيمكنك الوصول للحقائب التدريبية من خلال الرابط التالي:\nhttps://tvtc.gov.sa/ar/Departments/tvtcdepartments/cdd/Pages/packages.aspx?RootFolder=/ar/Departments/tvtcdepartments/cdd/DocLib1/%D8%A7%D9%84%D9%85%D8%B9%D8%A7%D9%87%D8%AF+%D8%A7%D9%84%D8%B5%D9%86%D8%A7%D8%B9%D9%8A%D8%A9/%D8%A7%D9%84%D9%85%D9%82%D8%B1%D8%B1%D8%A7%D8%AA+%D8%A7%D9%84%D9%85%D8%B4%D8%AA%D8%B1%D9%83%D8%A9+%D9%81%D9%8A+%D8%A7%D9%84%D9%85%D8%AC%D8%A7%D9%84/%D9%85%D9%8A%D9%83%D8%A7")
        return

    elif text in ["📚 الدراسات العامة", "❄️ التبريد والتكييف"]:
        await update.message.reply_text(f"📘 سيتم إضافة المراجع الخاصة بقسم ({text}) قريباً.")
        return

    # === رد افتراضي لأي نص غير متوقع ===
    else:
        await update.message.reply_text("يرجى اختيار خدمة من القائمة أسفل الشاشة ⬇️")

# ================== (3. تشغيل البوت) ==================
def main():
    if not TOKEN:
        print("❌ خطأ: التوكن غير موجود في إعدادات Render!")
        return

    keep_alive()
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 يعمل البوت الآن بكافة خدماته الأساسية...")
    app.run_polling()

if __name__ == "__main__":
    main()
