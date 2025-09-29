from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from config import BOT_TOKEN, CHANNEL_ID, ADMIN_NOTIFICATIONS_ID, ADMIN_COMMANDS_ID
import json, re
REQUIRED_CHANNELS = [
    {"name": "📢 قناة 1", "url": "https://t.me/itekernal", "id": "-1003123247092"},
    {"name": "📢 قناة 2", "url": "https://t.me/somarkernal", "id": "-1003123247092"}
]

# تحميل وحفظ JSON
def load_json(path): 
    try:
        with open(path, 'r') as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    except: return {}

def save_json(path, data): json.dump(data, open(path, 'w'))

def load_balances(): return load_json('data/user_balances.json')
def save_balances(b): save_json('data/user_balances.json', b)
def load_used_balances(): return set(load_json('data/used_balances.json'))
def save_used_balances(u): save_json('data/used_balances.json', list(u))

def mark_waiting_receipt(uid): w = load_json('data/waiting_receipts.json'); w[uid] = True; save_json('data/waiting_receipts.json', w)
def is_waiting_receipt(uid): return load_json('data/waiting_receipts.json').get(uid, False)
def clear_waiting_receipt(uid): w = load_json('data/waiting_receipts.json'); w.pop(uid, None); save_json('data/waiting_receipts.json', w)

def mark_waiting_request(uid, service): w = load_json('data/waiting_requests.json'); w[uid] = service; save_json('data/waiting_requests.json', w)
def get_waiting_request(uid): return load_json('data/waiting_requests.json').get(uid)
def clear_waiting_request(uid): w = load_json('data/waiting_requests.json'); w.pop(uid, None); save_json('data/waiting_requests.json', w)

def save_pending_submission(uid, text=None, file_id=None):
    data = load_json('data/pending_submissions.json')
    if uid not in data: data[uid] = {"texts": [], "files": []}
    if text: data[uid]["texts"].append(text)
    if file_id: data[uid]["files"].append(file_id)
    save_json('data/pending_submissions.json', data)

def get_pending_submission(uid): return load_json('data/pending_submissions.json').get(uid)
def clear_pending_submission(uid): data = load_json('data/pending_submissions.json'); data.pop(uid, None); save_json('data/pending_submissions.json', data)

def set_pending_service(uid, service): data = load_json('data/pending_services.json'); data[uid] = service; save_json('data/pending_services.json', data)
def get_pending_service(uid): return load_json('data/pending_services.json').get(uid)
def clear_pending_service(uid): data = load_json('data/pending_services.json'); data.pop(uid, None); save_json('data/pending_services.json', data)

def set_pending_pages(uid, pages): data = load_json('data/pending_pages.json'); data[uid] = pages; save_json('data/pending_pages.json', data)
def get_pending_pages(uid): return load_json('data/pending_pages.json').get(uid)
def clear_pending_pages(uid): data = load_json('data/pending_pages.json'); data.pop(uid, None); save_json('data/pending_pages.json', data)

admin_file_queue = {}
channel_receipts = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    balance = load_balances().get(uid, 0)
    keyboard = [["💰 تعبئة رصيد"], ["📄 ملف Word", "📊 ملف Excel"], ["📽 PowerPoint", "🧩 وظيفة مشتركة"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"👋 أهلاً بك {update.effective_user.first_name}!\n📌 رقمك: {uid}\n💳 رصيدك: {balance} ليرة سورية\n👇 اختر الخدمة:",
        reply_markup=reply_markup
    )

async def ask_receipt(update, context):
    mark_waiting_receipt(str(update.effective_user.id))
    await update.message.reply_text(" 📩 أرسل الرصيد المراد ايداعه على احد هذة الاكواد: 345343         ,         68676     ,ملاحظة: ارسل سيرتيل كاش وليس رصيد عادي ثم ارسل رقم العملية للتحقق   سوف يتم التحقق من العملية عندما يكون الادمن متصل اي من دقيقة الى 6 ساعات على الاكثر.")

async def verify_receipt(update, context):
    uid = str(update.effective_user.id)
    if not is_waiting_receipt(uid): return
    receipt = update.message.text.strip()
    clear_waiting_receipt(uid)
    used = load_used_balances()
    if receipt in used:
        await update.message.reply_text("⚠️ الرقم مستخدم مسبقًا.")
        return
    if receipt in channel_receipts:
        amount = channel_receipts[receipt]
        balances = load_balances()
        balances[uid] = balances.get(uid, 0) + amount
        save_balances(balances)
        used.add(receipt)
        save_used_balances(used)
        await update.message.reply_text(f"✅ تم إضافة {amount} ليرة سورية.")
    else:
        await update.message.reply_text(" لم يتم العثور على الرقم❌ : الرقم غير صحيح او الادمن لم يتصل بعد انتظر بضع ساعات واعد الارسال.")

async def handle_service_selection(update, context):
    uid = str(update.effective_user.id)
    text = update.message.text.strip()
    if text == "📄 ملف Word":
        set_pending_service(uid, "word")
        await update.message.reply_text("📝 خدمة Word:\nتنسيق وكتابة ملف احترافئ,ارسل عدد الصفحات الصحيح لان لن يتم كتابة الى العدد المدخل,اذا كنت تريد كتابة حلقة بحث فاضغط على زر وظيفة مشتركة.\n💰السعر:5000 ليرة سورية.\nكم عدد الصفحات المطلوبة؟")
    elif text == "📊 ملف Excel":
        set_pending_service(uid, "excel")
        await update.message.reply_text("📊 خدمة Excel:\nتنسيق جداول وصيغ ورسوم.\n💰السعر:60000 ليرة سورية.\nكم عدد الصفحات المطلوبة؟")
    elif text == "📽 PowerPoint":
        set_pending_service(uid, "power_point")
        await update.message.reply_text("🎞 خدمة PowerPoint:\nعرض تقديمي احترافي.\n💰 السعر:35000 ليرة سورية.\nإذا موافق، أرسل: دفع power_point")

async def handle_shared_job_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    text = update.message.text.strip()
    if text == "🧩 وظيفة مشتركة":
        keyboard = [["🔍 حلقة بحث Word"], ["🧩 Word & Excel"], ["🧩 Word & PowerPoint"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("🧩 اختر نوع الوظيفة المشتركة:", reply_markup=reply_markup)
    elif text == "🔍 حلقة بحث Word":
        set_pending_service(uid, "shared_word")
        await update.message.reply_text("🔍 حلقة بحث Word:\n💰 السعر:50000 ليرة سورية.\nإذا موافق، أرسل: دفع shared_word")
    elif text == "🧩 Word & Excel":
        set_pending_service(uid, "shared_word_excel")
        await update.message.reply_text("🧩 Word & Excel:\n💰 السعر:11000 ليرة سورية.\nإذا موافق، أرسل: دفع shared_word_excel")
    elif text == "🧩 Word & PowerPoint":
        set_pending_service(uid, "shared_word_ppt")
        await update.message.reply_text("🧩 Word & PowerPoint:\n💰 السعر:90000 ليرة سورية.\nإذا موافق، أرسل: دفع shared_word_ppt")

async def handle_numeric_input(update, context):
    uid = str(update.effective_user.id)
    text = update.message.text.strip()
    if is_waiting_receipt(uid):
        await verify_receipt(update, context)
        return
    service = get_pending_service(uid)
    if service in ["word", "excel"] and text.isdigit():
        pages = int(text)
        set_pending_pages(uid, pages)
        price = pages * (5000 if service == "word" else 60000)
        await update.message.reply_text(f"✅ السعر الإجمالي: {pages} × {(5000 if service == 'word' else 60000)} = {price} ليرة سورية.\nإذا كنت موافق، أرسل: دفع {service}")

async def handle_payment(update, context):
    uid = str(update.effective_user.id)
    text = update.message.text.strip().lower()
    service = get_pending_service(uid)
    pages = get_pending_pages(uid)
    if service in ["word", "excel"] and pages:
        price = pages * (5000 if service == "word" else 60000)
    elif "power_point" in text: service = "power_point"; price = 35000

    elif "shared_word_excel" in text: service = "shared_word_excel"; price = 110000
    elif "shared_word_ppt" in text: service = "shared_word_ppt"; price =90000
    elif "shared_word" in text: service = "shared_word"; price = 50000
    elif "power_point" in text: service = "power_point"; price = 1000
    else: return
    balances = load_balances()
    if balances.get(uid, 0) < price:
        await update.message.reply_text("❌ رصيدك غير كافي.")
        return
    balances[uid] -= price
    save_balances(balances)
    mark_waiting_request(uid, service)
    clear_pending_service(uid)
    clear_pending_pages(uid)
    await update.message.reply_text("✅ تم الدفع.\n📩 أرسل المعلومات والملفات،وارسل اسمك ورقمك الواتس من اجل ان نتواصل معك ونأكد استلام الملفات والمباشرة بالعمل والمواعيد المتوقعة للانتهاء, وعند الانتهاء أرسل كلمة 'انتهيت'.")
async def handle_admin_file_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.channel_post or not update.channel_post.text: return
    if update.channel_post.chat_id != ADMIN_COMMANDS_ID: return

    text = update.channel_post.text.strip()
    if text.startswith("ارسال_ملف"):
        parts = text.split()
        if len(parts) != 2 or not parts[1].isdigit():
            await context.bot.send_message(chat_id=update.channel_post.chat_id, text="❌ الصيغة: ارسال_ملف [ID]")
            return
        target_id = parts[1]
        admin_file_queue[update.channel_post.chat_id] = {
            "target": target_id,
            "texts": [],
            "files": []
        }
        await context.bot.send_message(
            chat_id=update.channel_post.chat_id,
            text=f"📌 جاهز لاستقبال الملفات للمستخدم ID: {target_id}\n✍️ أرسل الملفات أو النصوص، وعند الانتهاء من ارسال الملفات أرسل كلمة انتهيت.",
            parse_mode="Markdown"
        )
async def handle_user_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    pending = get_waiting_request(uid)
    if not pending: return

    if update.message.text and update.message.text.strip().lower() == "انتهيت":
        submission = get_pending_submission(uid)
        header = f"📥 طلب جديد\n🛠 الخدمة: {pending}\n👤 المستخدم: {uid}"

        if submission and submission["texts"]:
            combined = "\n---\n".join(submission["texts"])
            await context.bot.send_message(chat_id=CHANNEL_ID, text=f"{header}\n📄 معلومات:\n{combined}")

        if submission and submission["files"]:
            for file_id in submission["files"]:
                await context.bot.send_document(chat_id=CHANNEL_ID, document=file_id, caption=f"📎 ملف خدمة {pending}")

        await update.message.reply_text("✅ تم إرسال طلبك بنجاح.")
        clear_pending_submission(uid)
        clear_waiting_request(uid)
        await context.bot.send_message(ADMIN_NOTIFICATIONS_ID, text=f"📢 تم استلام طلب جديد من المستخدم {uid} لخدمة {pending}")
        print(f"📬 تم إرسال طلب المستخدم {uid} لخدمة {pending}")
        return

    if update.message.text:
        save_pending_submission(uid, text=update.message.text.strip())
        print(f"📝 تم حفظ نص من المستخدم {uid}")
    elif update.message.document:
        save_pending_submission(uid, file_id=update.message.document.file_id)
        print(f"📎 تم حفظ ملف من المستخدم {uid}")
    elif update.message.photo:
        save_pending_submission(uid, file_id=update.message.photo[-1].file_id)
        print(f"🖼 تم حفظ صورة من المستخدم {uid}")
async def handle_channel_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.channel_post or not update.channel_post.text:
        return

    text = update.channel_post.text.strip()
    amount_match = re.search(r"مبلغ\s+(\d+)\s*ل\.س", text)
    code_match = re.search(r"رقم العملية\s+هو\s+(\d+)", text)

    if amount_match and code_match:
        amount = int(amount_match.group(1))
        receipt_id = code_match.group(1)
        channel_receipts[receipt_id] = amount
        print(f"✅ تم تسجيل إيصال: {receipt_id} بمبلغ {amount}")
async def handle_admin_file_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.channel_post.chat_id
    if admin_id != ADMIN_COMMANDS_ID or admin_id not in admin_file_queue: return

    if update.channel_post.text and update.channel_post.text.strip().lower() == "انتهيت":
        data = admin_file_queue.pop(admin_id)
        target = int(data["target"])
        try:
            if data["texts"]:
                combined = "\n---\n".join(data["texts"])
                await context.bot.send_message(chat_id=target, text=f"📤 ملفات جاهزة:\n{combined}")
            for file_id in data["files"]:
                await context.bot.send_document(chat_id=target, document=file_id)
            await context.bot.send_message(chat_id=admin_id, text="✅ تم إرسال الملفات للمستخدم.")
        except Exception as e:
            await context.bot.send_message(chat_id=admin_id, text=f"❌ فشل الإرسال: {e}")
        return

    if update.channel_post.text:
        admin_file_queue[admin_id]["texts"].append(update.channel_post.text.strip())
    elif update.channel_post.document:
        admin_file_queue[admin_id]["files"].append(update.channel_post.document.file_id)
    elif update.channel_post.photo:
        admin_file_queue[admin_id]["files"].append(update.channel_post.photo[-1].file_id)
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^💰 تعبئة رصيد$"), ask_receipt))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^📄 ملف Word$|^📊 ملف Excel$|^📽 PowerPoint$"), handle_service_selection))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^🧩 وظيفة مشتركة$|^🔍 حلقة بحث Word$|^🧩 Word & Excel$|^🧩 Word & PowerPoint$"), handle_shared_job_selection))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"(?i)^دفع"), handle_payment))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^\d+$"), handle_numeric_input))
    app.add_handler(MessageHandler(filters.ALL & filters.UpdateType.MESSAGE, handle_user_submission))
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, handle_channel_receipt))
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, handle_admin_file_command))
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, handle_admin_file_submission))

    print("✅ البوت يعمل الآن...")
    app.run_polling()