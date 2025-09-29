
import json
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

# تحميل الرصيد
def load_balances():
    try:
        with open('data/user_balances.json', 'r') as f:
            return json.load(f)
    except:
        return {}

# حفظ الرصيد
def save_balances(balances):
    with open('data/user_balances.json', 'w') as f:
        json.dump(balances, f)

# حفظ حالة الدفع
def mark_paid(user_id, service):
    try:
        with open('data/paid_users.json', 'r') as f:
            paid = json.load(f)
    except:
        paid = {}
    paid[user_id] = service
    with open('data/paid_users.json', 'w') as f:
        json.dump(paid, f)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        await update.effective_chat.send_message("📌 يرجى كتابة /start مباشرة في المحادثة مع البوت.")
        return

    user = update.effective_user
    user_id = str(user.id)
    balances = load_balances()
    balance = balances.get(user_id, 0)

    keyboard = [
        ["💰 تعبئة رصيد"],
        ["📄 ملف Word", "📊 ملف Excel"],
        ["📽 PowerPoint", "🧩 وظيفة مشتركة"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)



    message = (
        f"👋 *أهلاً بك {user.first_name}!*\n"
        f"📌 *رقمك:* {user_id}\n"
        f"💳 *رصيدك الحالي:* *{balance} نقطة*\n\n"
        "👇 *اختر الخدمة التي تريدها من القائمة:*"
    )

    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")

# عرض الخدمات
async def send_service(update: Update, context: ContextTypes.DEFAULT_TYPE, label, price, service_key):
    print(f"📩 استلم طلب: {label}")
    await update.message.reply_text(
        f"{label}\n💰 السعر: {price} نقطة\n"
        f"إذا كنت موافق، أرسل: *دفع {service_key}*",
        parse_mode="Markdown"
    )

# الدفع
async def pay_service(update: Update, context: ContextTypes.DEFAULT_TYPE, price, service_key):
    user_id = str(update.effective_user.id)
    balances = load_balances()
    balance = balances.get(user_id, 0)

    if balance < price:
        await update.message.reply_text("❌ رصيدك غير كافي لهذه الخدمة.")
        return

    balances[user_id] = balance - price
    save_balances(balances)
    mark_paid(user_id, service_key)
    print(f"💵 دفع ناجح: {service_key} من المستخدم {user_id}")
    await update.message.reply_text(
        f"✅ تم الدفع بنجاح.\n📥 الرجاء الآن إرسال المعلومات أو الملف المطلوب لخدمة *{service_key.capitalize()}*.",
        parse_mode="Markdown"
    )

# خدمات فردية
async def send_word_file(update, context): await send_service(update, context, "📄 خدمة ملف Word", 20, "word")
async def pay_word(update, context): await pay_service(update, context, 20, "word")

async def send_excel_file(update, context): await send_service(update, context, "📊 خدمة ملف Excel", 25, "excel")
async def pay_excel(update, context): await pay_service(update, context, 25, "excel")

async def send_ppt_file(update, context): await send_service(update, context, "📽 خدمة PowerPoint", 30, "ppt")
async def pay_ppt(update, context): await pay_service(update, context, 30, "ppt")


# الوظيفة المشتركة الأصلية
async def send_shared_task(update, context):
    keyboard = [
        ["🔍 حلقة بحث Word"],
        ["🧩 Word & PowerPoint"],
        ["🧩 Word & Excel"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("🧩 اختر نوع الوظيفة المشتركة:", reply_markup=reply_markup)

async def pay_shared(update, context): await pay_service(update, context, 40, "shared")

# الوظائف المشتركة الفرعية
async def send_shared_word(update, context): await send_service(update, context, "🔍 حلقة بحث Word", 40, "shared_word")
async def pay_shared_word(update, context): await pay_service(update, context, 40, "shared_word")
async def send_shared_word_ppt(update, context): await send_service(update, context, "🧩 Word & PowerPoint", 50, "shared_word_ppt")
async def pay_shared_word_ppt(update, context): await pay_service(update, context, 50, "shared_word_ppt")

async def send_shared_word_excel(update, context): await send_service(update, context, "🧩 Word & Excel", 55, "shared_word_excel")
async def pay_shared_word_excel(update, context): await pay_service(update, context, 55, "shared_word_excel")

# تسجيل الـ handlers
start_handler = CommandHandler("start", start)

word_file_handler = MessageHandler(filters.TEXT & filters.Regex("^📄 ملف Word$"), send_word_file)
pay_word_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع word$"), pay_word)

excel_file_handler = MessageHandler(filters.TEXT & filters.Regex("^📊 ملف Excel$"), send_excel_file)
pay_excel_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع excel$"), pay_excel)

ppt_file_handler = MessageHandler(filters.TEXT & filters.Regex("^📽 PowerPoint$"), send_ppt_file)
pay_ppt_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع ppt$"), pay_ppt)

shared_task_handler = MessageHandler(filters.TEXT & filters.Regex("^🧩 وظيفة مشتركة$"), send_shared_task)
pay_shared_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع shared$"), pay_shared)

shared_word_handler = MessageHandler(filters.TEXT & filters.Regex("^🔍 حلقة بحث Word$"), send_shared_word)
pay_shared_word_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع shared_word$"), pay_shared_word)

shared_word_ppt_handler = MessageHandler(filters.TEXT & filters.Regex("^🧩 Word & PowerPoint$"), send_shared_word_ppt)
pay_shared_word_ppt_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع shared_word_ppt$"), pay_shared_word_ppt)

shared_word_excel_handler = MessageHandler(filters.TEXT & filters.Regex("^🧩 Word & Excel$"), send_shared_word_excel)
pay_shared_word_excel_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع shared_word_excel$"), pay_shared_word_excel)