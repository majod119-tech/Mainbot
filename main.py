from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import qrcode
import uuid
import os
from keep_alive import keep_alive  # استدعاء دالة التشغيل المستمر لمنصة Render

# جلب التوكن من متغيرات البيئة (أمان أفضل) أو استخدام التوكن الحالي
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8315603096:AAGo9OSSZ1GTToWMsYBS04tLH5tL4_9ww4c")

# إنشاء المجلدات الضرورية لتجنب تعطل الكود إذا لم تكن موجودة
for folder in ["complaints", "assets", "data"]:
    if not os.path.exists(folder):
        os.makedirs(folder)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["✅ ابدأ"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "مرحباً بك في البوت الرسمي للمعهد الصناعي الثانوي ببريدة 🤖\nنسعد بخدمتكم وتسهيل وصولكم للمعلومات والخدمات التدريبية.\n\nاضغط على الزر أدناه للبدء:",
        reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "✅ ابدأ":
        keyboard = [["👨‍🏫 مدرب"], ["👨‍🎓 متدرب"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("يرجى اختيار المستخدم:", reply_markup=reply_markup)
        return

    if text == "👨‍🏫 مدرب":
        keyboard = [["تظلم المدرب"], ["وصف المقررات"], ["المراجع التدريبية"], ["🔙 عودة"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "مرحباً بك عزيزي المدرب في بوت خدمات المعهد الصناعي الثانوي ببريدة.",
            reply_markup=reply_markup)
        return

    if text == "🔙 عودة":
        if context.user_data.get("awaiting_id"):
            context.user_data["awaiting_id"] = False
            keyboard = [["المراجع التدريبية"], ["📕 دليل المتدرب"],
                        ["📅 التقويم التدريبي"], ["🚩 الخط الزمني لرايات"],
                        ["📚 أدلة رايات"], ["📝 رفع تظلم"],
                        ["🔍 معرفة رقمي التدريبي"], ["🔙 عودة"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text("خدمات المتدربين:", reply_markup=reply_markup)
            return

        keyboard = [["👨‍🏫 مدرب"], ["👨‍🎓 متدرب"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("يرجى اختيار المستخدم:", reply_markup=reply_markup)
        return

    if text == "تظلم المدرب":
        try:
            with open("assets/trainer_complaint_guide.pdf", "rb") as file:
                await update.message.reply_document(
                    document=file,
                    filename="ضوابط_تظلم_المدربين.pdf",
                    caption="📝 ضوابط وإجراءات التظلم ألعضاء هيئة التدريب")
        except FileNotFoundError:
            await update.message.reply_text("⚠️ عذراً، ملف ضوابط التظلم غير متوفر حالياً.")
        return

    if text == "وصف المقررات":
        await update.message.reply_text(
            "📚 وصف المقررات (المعاهد الصناعية):\n\n"
            "يمكنك الوصول لوصف المقررات والخطط من خلال الرابط التالي:\n"
            "https://tvtc.gov.sa/ar/Departments/tvtcdepartments/cdd/Pages/plans.aspx?RootFolder=/ar/Departments/tvtcdepartments/cdd/DocLib/%D8%A7%D9%84%D9%85%D8%B9%D8%A7%D9%87%D8%AF+%D8%A7%D9%84%D8%B5%D9%86%D8%A7%D8%B9%D9%8A%D8%A9/%D8%A7%D9%84%D8%AB%D8%A7%D9%86%D9%88%D9%8A+%D8%A7%D9%84%D8%B5%D9%86%D8%A7%D8%B9%D9%8A"
        )
        return

    if text == "👨‍🎓 متدرب":
        keyboard = [["المراجع التدريبية"], ["📕 دليل المتدرب"],
                    ["📅 التقويم التدريبي"], ["🚩 الخط الزمني لرايات"],
                    ["📚 أدلة رايات"], ["📝 رفع تظلم"],
                    ["🔍 معرفة رقمي التدريبي"], ["🔙 عودة"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("خدمات المتدربين:", reply_markup=reply_markup)
        return

    if text == "📚 أدلة رايات":
        await update.message.reply_text(
            "📚 أدلة مستخدم نظام رايات:\n\n"
            "يمكنك الوصول لجميع الأدلة التعليمية والمصورة لنظام رايات عبر الرابط التالي:\n"
            "https://rayat.tvtc.gov.sa/Static/Guide.aspx")
        return

    if text == "🔍 معرفة رقمي التدريبي":
        context.user_data["awaiting_id"] = True
        await update.message.reply_text("🔢 من فضلك أرسل رقم الهوية لمعرفة رقمك التدريبي:")
        return

    if context.user_data.get("awaiting_id"):
        id_number = text.strip()
        context.user_data["awaiting_id"] = False
        found = False
        try:
            import openpyxl
            # قراءة ملف الإكسيل
            wb = openpyxl.load_workbook("data/هويات المتدربين.xlsx", data_only=True)
            sheet = wb.active
            
            # جلب أسماء الأعمدة من الصف الأول
            headers = [str(cell.value).strip() if cell.value else "" for cell in sheet[1]]
            
            # تحديد أماكن الأعمدة
            id_col_idx = headers.index("رقم الهوية") if "رقم الهوية" in headers else -1
            student_id_col_idx = headers.index("رقم المتدرب") if "رقم المتدرب" in headers else -1
            email_col_idx = headers.index("البريد الالكتروني") if "البريد الالكتروني" in headers else -1
            
            if id_col_idx == -1:
                await update.message.reply_text("⚠️ تنبيه للمسؤول: عمود 'رقم الهوية' غير موجود في ملف الإكسيل.")
                return

            for row in sheet.iter_rows(min_row=2, values_only=True):
                current_id = str(row[id_col_idx]).strip() if row[id_col_idx] is not None else ""
                
                # إزالة أي أصفار عشرية تظهر عند قراءة الإكسيل للأرقام (مثل 100.0)
                if current_id.endswith('.0'):
                    current_id = current_id[:-2]
                
                if current_id == id_number:
                    student_id = "غير متوفر"
                    email = "غير متوفر"
                    
                    if student_id_col_idx != -1 and row[student_id_col_idx] is not None:
                        student_id = str(row[student_id_col_idx]).strip()
                        if student_id.endswith('.0'): student_id = student_id[:-2]
                        
                    if email_col_idx != -1 and row[email_col_idx] is not None:
                        email = str(row[email_col_idx]).strip()
                        
                    await update.message.reply_text(
                        f"✅ تم العثور على بياناتك:\n\n"
                        f"🔢 الرقم التدريبي: `{student_id}`\n"
                        f"📧 البريد الإلكتروني: `{email}`\n\n"
                        f"يمكنك استخدامه لتسجيل الدخول في أنظمة المؤسسة.",
                        parse_mode="Markdown")
                    found = True
                    break
        except FileNotFoundError:
            await update.message.reply_text("⚠️ قاعدة بيانات المتدربين غير متوفرة حالياً.")
            return
        except Exception as e:
            print(f"Error reading Excel: {e}")
            await update.message.reply_text("⚠️ عذراً، حدث خطأ أثناء البحث في البيانات. يرجى المحاولة لاحقاً.")
            return

        if not found:
            keyboard = [["🔙 عودة"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                f"🔍 بحثنا عن الهوية: {id_number}\n\n⚠️ عذراً، لم يتم العثور على بيانات مرتبطة بهذا الرقم. يرجى التأكد من الرقم أو مراجعة قسم القبول والتسجيل.",
                reply_markup=reply_markup)
        return

    if text == "المراجع التدريبية":
        keyboard = [["💻 الحاسب الآلي", "⚡ الكهرباء الانشائية"],
                    ["📚 الدراسات العامة", "❄️ التبريد والتكييف"],
                    ["🚗 ميكانيكا السيارات"], ["🔙 عودة"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("اختر القسم التدريبي المستهدف:", reply_markup=reply_markup)
        return

    if text == "💻 الحاسب الآلي":
        await update.message.reply_text(
            "💻 المراجع التدريبية لقسم الحاسب الآلي:\n\n"
            "يمكنك الوصول للحقائب التدريبية من خلال الرابط التالي:\n"
            "https://tvtc.gov.sa/ar/Departments/tvtcdepartments/cdd/Pages/packages.aspx?RootFolder=/ar/Departments/tvtcdepartments/cdd/DocLib1/%D8%A7%D9%84%D9%85%D8%B9%D8%A7%D9%87%D8%AF%20%D8%A7%D9%84%D8%B5%D9%86%D8%A7%D8%B9%D9%8A%D8%A9/%D8%A7%D9%84%D8%AD%D8%A7%D8%B3%D8%A8%20%D8%A7%D9%84%D8%A2%D9%84%D9%8A"
        )
        return

    if text == "⚡ الكهرباء الانشائية":
        await update.message.reply_text(
            "⚡ المراجع التدريبية لقسم الكهرباء الانشائية:\n\n"
            "يمكنك الوصول للحقائب التدريبية من خلال الرابط التالي:\n"
            "https://tvtc.gov.sa/ar/Departments/tvtcdepartments/cdd/Pages/packages.aspx?RootFolder=/ar/Departments/tvtcdepartments/cdd/DocLib1/%D8%A7%D9%84%D9%85%D8%B9%D8%A7%D9%87%D8%AF%20%D8%A7%D9%84%D8%B5%D9%86%D8%A7%D8%B9%D9%8A%D8%A9/%D8%A7%D9%84%D9%83%D9%87%D8%B1%D8%A8%D8%A7%D8%A1/%D8%A7%D9%84%D9%83%D9%87%D8%B1%D8%A8%D8%A7%D8%A1%20%D8%A7%D9%84%D8%A5%D9%86%D8%B4%D8%A7%D8%A6%D9%8A%D8%A9"
        )
        return

    if text == "🚗 ميكانيكا السيارات":
        await update.message.reply_text(
            "🚗 المراجع التدريبية لقسم ميكانيكا السيارات:\n\n"
            "يمكنك الوصول للحقائب التدريبية من خلال الرابط التالي:\n"
            "https://tvtc.gov.sa/ar/Departments/tvtcdepartments/cdd/Pages/packages.aspx?RootFolder=/ar/Departments/tvtcdepartments/cdd/DocLib1/%D8%A7%D9%84%D9%85%D8%B9%D8%A7%D9%87%D8%AF+%D8%A7%D9%84%D8%B5%D9%86%D8%A7%D8%B9%D9%8A%D8%A9/%D8%A7%D9%84%D9%85%D9%82%D8%B1%D8%B1%D8%A7%D8%AA+%D8%A7%D9%84%D9%85%D8%B4%D8%AA%D8%B1%D9%83%D8%A9+%D9%81%D9%8A+%D8%A7%D9%84%D9%85%D8%AC%D8%A7%D9%84/%D9%85%D9%8A%D9%83%D8%A7"
        )
        return

    if text in ["📚 الدراسات العامة", "❄️ التبريد والتكييف"]:
        await update.message.reply_text(f"📘 سيتم إضافة المراجع الخاصة بقسم ({text}) قريباً.")
        return

    if text == "📕 دليل المتدرب":
        try:
            with open("assets/trainee_guide.pdf", "rb") as file:
                await update.message.reply_document(
                    document=file,
                    filename="دليل_المتدرب_١٤٤٧هـ.pdf",
                    caption="📕 دليل المتدرب للعام التدريبي 1447هـ - 1448هـ")
        except FileNotFoundError:
            await update.message.reply_text("⚠️ عذراً، دليل المتدرب غير متوفر حالياً.")
        return

    if text == "📅 التقويم التدريبي":
        try:
            with open("assets/calendar.jpg", "rb") as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption="📅 التقويم التدريبي للفصل الثاني 1447هـ - 1448هـ")
        except FileNotFoundError:
            await update.message.reply_text("⚠️ عذراً، صورة التقويم التدريبي غير متوفرة حالياً.")
        return

    if text == "🚩 الخط الزمني لرايات":
        try:
            with open("assets/timeline.pdf", "rb") as file:
                await update.message.reply_document(
                    document=file,
                    filename="الخط_الزمني_لرايات_١٤٤٧هـ.pdf",
                    caption="🚩 الخط الزمني لأعمال الفصل التدريبي الثاني 1447هـ")
        except FileNotFoundError:
            await update.message.reply_text("⚠️ عذراً، ملف الخط الزمني غير متوفر حالياً.")
        return

    if text == "📝 رفع تظلم":
        await update.message.reply_text("📝 لرفع تظلمك، اضغط الرابط التالي:\nhttps://forms.gle/CvY7KBuJA66suK1D8")
        return

    if context.user_data.get("complaint_state"):
        complaint_id = str(uuid.uuid4())[:8]
        file_path = f"complaints/{complaint_id}.txt"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)

        qr = qrcode.make(f"رقم التظلم: {complaint_id}")
        qr_path = f"complaints/{complaint_id}.png"
        qr.save(qr_path)

        with open(qr_path, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=f"✅ تم استلام تظلمك\n🔢 رقم التظلم: {complaint_id}\nاحتفظ بالـ QR Code للمتابعة"
            )

        context.user_data["complaint_state"] = False
        return

    await update.message.reply_text("يرجى اختيار خدمة من القائمة")

def main():
    # تشغيل السيرفر الوهمي الخاص بـ Render
    keep_alive()
    
    # تشغيل البوت
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ البوت يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
