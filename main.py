from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import qrcode
import uuid
import os
import openpyxl
from keep_alive import keep_alive  # استدعاء دالة التشغيل المستمر لمنصة Render

# جلب التوكن من الخزنة السرية في Render (أمان 100%)
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# التأكد من وجود التوكن لتجنب الأخطاء
if not TOKEN:
    print("⚠️ تنبيه: لم يتم العثور على التوكن! تأكد من إضافته في Environment Variables في Render.")

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
            "📚 وصف
