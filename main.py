from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from config import BOT_TOKEN, CHANNEL_ID, ADMIN_NOTIFICATIONS_ID, ADMIN_COMMANDS_ID,PUBLIC_SERVICE_CHANNEL_ID
import json, re

REQUIRED_CHANNELS = [
    {"name": "📢 قناة الشروحات", "url": "https://t.me/itekernal"},
    {"name": "📢 قناة اعلانات البوت والاثباتات", "url": "https://t.me/somarkernal"}
]

def load_json(path):
    try:
        with open(path, 'r') as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    except:
        return {}

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
# إرسال روابط القنوات المطلوبة
async def send_channel_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    links = "\n".join([f"{ch['name']}: [اضغط هنا]({ch['url']})" for ch in REQUIRED_CHANNELS])
    await update.message.reply_text(
        f"📢 القنوات المطلوبة للاشتراك:\n\n{links}",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

# بدء المحادثة
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    balance = load_balances().get(uid, 0)
    await send_channel_links(update, context)
    keyboard = [
    ["💰 تعبئة رصيد"],
    ["📄 ملف Word", "📊 ملف Excel"],
    ["🎨 تصميم Canva", "📽 PowerPoint"],
    ["📷 فوتوشوب", "🌐 ترجمة"],
    ["🧩 وظيفة مشتركة", "🎁 العروض"]
]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"👋 أهلاً بك {update.effective_user.first_name}!\n📌 رقمك: {uid}\n💳 رصيدك: {balance} ل.س\n👇 اختر الخدمة:",
        reply_markup=reply_markup
    )

# طلب إيصال دفع
async def ask_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    mark_waiting_receipt(uid)

    file_id = "AgACAgQAAxkBAAISM2jdpTkAAThv2XzrSWfcxIJLynNkIQACz8sxG20n8FJDUAim719OpQEAAwIAA3gAAzYE" # ← استبدله بـ file_id الحقيقي للصورة

    caption = (
        "💳 طرق الدفع المتاحة:\n\n"
        "📱 *سيريتل كاش*: أرسل المبلغ على أحد الأكواد:\n"
        "🔢 37059919     أو 47213550\n\n"
        "🏦 *شام كاش*:  إرسل المبلغ على الحساب:\n"
        "ab9d71345893e66018a157d7e11e9729\n"
        " او امسح الرمز المرسل بالصورة\n\n"
        "📩 ثم انتظر عشر دقائق وأرسل رقم العملية.\n"
        "⏱ اذا لم يتم التحقق اعد ارسال الرمز بعد نصف ساعة."
    )

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=file_id,
        caption=caption,
        parse_mode="Markdown"
    )

# التحقق من إيصال الدفع
async def verify_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if not is_waiting_receipt(uid):
        return

    receipt = update.message.text.strip()
    clear_waiting_receipt(uid)
    used = load_used_balances()

    if receipt in used:
        await update.message.reply_text("⚠️ الرقم مستخدم مسبقًا.")
        return

    if receipt in channel_receipts:
        amount = int(channel_receipts[receipt])
        balances = load_balances()
        balances[uid] = balances.get(uid, 0) + amount
        save_balances(balances)
        used.add(receipt)
        save_used_balances(used)
        await update.message.reply_text(f"✅ تم إضافة {amount} ل.س إلى رصيدك.")
    else:
        await update.message.reply_text("❌ لم يتم العثور على الرقم. انتظر قليلاً وأعد الإرسال.")
        # اختيار خدمات Word
async def handle_word_selection(update, context):
    uid = str(update.effective_user.id)
    text = update.message.text.strip()
    if text == "📄 ملف Word":
        keyboard = [["1️⃣ تنسيق فقط"], ["2️⃣ كتابة وتنسيق"], ["3️⃣ كتابة وتنسيق ومعادلات"], ["4️⃣ كتابة وتنسيق وصور"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("📄 اختر نوع خدمة Word المطلوبة:", reply_markup=reply_markup)
    elif text in ["1️⃣ تنسيق فقط", "2️⃣ كتابة وتنسيق", "3️⃣ كتابة وتنسيق ومعادلات", "4️⃣ كتابة وتنسيق وصور"]:
        prices = {"1️⃣ تنسيق فقط": 2500, "2️⃣ كتابة وتنسيق": 3500, "3️⃣ كتابة وتنسيق ومعادلات": 4000, "4️⃣ كتابة وتنسيق وصور": 3500}
        context.user_data["word_price_per_page"] = prices[text]
        set_pending_service(uid, "word_final")
        await update.message.reply_text("📄 كم عدد الصفحات المطلوبة؟")

# اختيار خدمات Excel
async def handle_excel_selection(update, context):
    uid = str(update.effective_user.id)
    text = update.message.text.strip()
    if text == "📊 ملف Excel":
        keyboard = [["1️⃣ تنسيق جدول"], ["2️⃣ إدخال معادلات"], ["3️⃣ جدول وخطوط بيانية"], ["4️⃣ يحدد لاحقًا"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("📊 اختر نوع خدمة Excel المطلوبة:", reply_markup=reply_markup)
    elif text == "1️⃣ تنسيق جدول":
        set_pending_service(uid, "excel_table")
        await update.message.reply_text("📊 تنسيق جدول:\n💰 السعر: 36000 ل.س\nإذا موافق، أرسل: دفع excel_table")
    elif text == "2️⃣ إدخال معادلات":
        set_pending_service(uid, "excel_formulas")
        await update.message.reply_text("📊 إدخال معادلات:\n💰 السعر: 120000 ل.س\nإذا موافق، أرسل: دفع excel_formulas")
    elif text == "3️⃣ جدول وخطوط بيانية":
        set_pending_service(uid, "excel_chart")
        await update.message.reply_text("📊 جدول وخطوط بيانية:\n💰 السعر: 145000 ل.س\nإذا موافق، أرسل: دفع excel_chart")
    elif text == "4️⃣ يحدد لاحقًا":
        set_pending_service(uid, "excel_later")
        await update.message.reply_text("📊 يحدد لاحقًا:\n💰 السعر: 0 ل.س\nإذا موافق، أرسل: دفع excel_later")

# اختيار خدمات PowerPoint
async def handle_ppt_selection(update, context):
    uid = str(update.effective_user.id)
    set_pending_service(uid, "power_point")
    await update.message.reply_text("📽 كم عدد السلايدات المطلوبة؟")

# اختيار خدمات Canva
async def handle_canva_selection(update, context):
    uid = str(update.effective_user.id)
    text = update.message.text.strip()
    if text == "🎨 تصميم Canva":
        keyboard = [["📢 إعلان"], ["🎉 كرت حفلة"], ["🖼 لوغو Logo"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("🎨 اختر نوع التصميم المطلوب:", reply_markup=reply_markup)
    elif text == "📢 إعلان":
        set_pending_service(uid, "canva_ad")
        await update.message.reply_text("📢 إعلان:\n💰 السعر: 15000 ل.س\nإذا موافق، أرسل: دفع canva_ad")
    elif text == "🎉 كرت حفلة":
        set_pending_service(uid, "canva_card")
        await update.message.reply_text("🎉 كرت حفلة:\n💰 السعر: 20000 ل.س\nإذا موافق، أرسل: دفع canva_card")
    elif text == "🖼 لوغو Logo":
        set_pending_service(uid, "canva_logo")
        await update.message.reply_text("🖼 لوغو:\n💰 السعر: 25000 ل.س\nإذا موافق، أرسل: دفع canva_logo")

# اختيار الوظائف المشتركة
async def handle_shared_job_selection(update, context):
    uid = str(update.effective_user.id)
    text = update.message.text.strip()
    if text == "🧩 وظيفة مشتركة":
        keyboard = [["🔍 حلقة بحث Word"], ["🧩 Word & Excel"], ["🧩 Word & PowerPoint"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("🧩 اختر نوع الوظيفة المشتركة:", reply_markup=reply_markup)
    elif text == "🔍 حلقة بحث Word":
        set_pending_service(uid, "shared_word")
        await update.message.reply_text("🔍 حلقة بحث Word:\n💰 السعر: 50000 ل.س\nإذا موافق، أرسل: دفع shared_word")
    elif text == "🧩 Word & Excel":
        set_pending_service(uid, "shared_word_excel")
        await update.message.reply_text("🧩 Word & Excel:\n💰 السعر: 63000 ل.س\nإذا موافق، أرسل: دفع shared_word_excel")
    elif text == "🧩 Word & PowerPoint":
        set_pending_service(uid, "shared_word_ppt")
        await update.message.reply_text("🧩 Word & PowerPoint:\n💰 السعر: 120000 ل.س\nإذا موافق، أرسل: دفع shared_word_ppt")
        #فوتوشوووب
async def handle_photoshop_selection(update, context):
    uid = str(update.effective_user.id)
    text = update.message.text.strip()

    if text == "📷 فوتوشوب":
        keyboard = [["1️⃣ تعديل وجه شخص"], ["2️⃣ تحسين صورة"], ["3️⃣ تصميم ملفت"], ["4️⃣ يحدد لاحقًا"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("📷 اختر نوع خدمة فوتوشوب المطلوبة:", reply_markup=reply_markup)

    elif text == "1️⃣ تعديل وجه شخص":
        set_pending_service(uid, "photoshop_face")
        await update.message.reply_text("🧑‍🎨 تعديل وجه:\n💰 السعر: 18000 ل.س\nإذا موافق، أرسل: دفع photoshop_face")

    elif text == "2️⃣ تحسين صورة":
        set_pending_service(uid, "photoshop_enhance")
        await update.message.reply_text("🖼 تحسين صورة:\n💰 السعر: 15000 ل.س\nإذا موافق، أرسل: دفع photoshop_enhance")

    elif text == "3️⃣ تصميم ملفت":
        set_pending_service(uid, "photoshop_design")
        await update.message.reply_text("🎯 تصميم ملفت:\n💰 السعر: 22000 ل.س\nإذا موافق، أرسل: دفع photoshop_design")

    elif text == "4️⃣ يحدد لاحقًا":
        set_pending_service(uid, "photoshop_later")
        await update.message.reply_text("📷 يحدد لاحقًا:\n💰 السعر: 0 ل.س\nإذا موافق، أرسل: دفع photoshop_later")
        #ترجمو
async def handle_translation_selection(update, context):
    uid = str(update.effective_user.id)
    text = update.message.text.strip()

    if text == "🌐 ترجمة":
        keyboard = [["1️⃣ ترجمة ملف"], ["2️⃣ ترجمة مقال"], ["3️⃣ ترجمة وثيقة رسمية"], ["4️⃣ يحدد لاحقًا"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("🌐 اختر نوع خدمة الترجمة المطلوبة:", reply_markup=reply_markup)

    elif text == "1️⃣ ترجمة ملف":
        set_pending_service(uid, "translation_file")
        await update.message.reply_text("📄 ترجمة ملف:\n💬 كم عدد الأوراق؟")

    elif text == "2️⃣ ترجمة مقال":
        set_pending_service(uid, "translation_article")
        await update.message.reply_text("📝 ترجمة مقال:\n💰 السعر: 18000 ل.س\nإذا موافق، أرسل: دفع translation_article")

    elif text == "3️⃣ ترجمة وثيقة رسمية":
        set_pending_service(uid, "translation_doc")
        await update.message.reply_text("📑 ترجمة وثيقة رسمية:\n💰 السعر: 25000 ل.س\nإذا موافق، أرسل: دفع translation_doc")

    elif text == "4️⃣ يحدد لاحقًا":
        set_pending_service(uid, "translation_later")
        await update.message.reply_text("🌐 يحدد لاحقًا:\n💰 السعر: 0 ل.س\nإذا موافق، أرسل: دفع translation_later")
        
        #العروض
async def handle_offers_selection(update, context):
    uid = str(update.effective_user.id)
    text = update.message.text.strip()

    if text == "🎁 العروض":
        keyboard = [["🎯 عرض 1"], ["🔥 عرض 2"], ["💼 عرض 3"], ["🧠 عرض 4"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("🎁 اختر أحد العروض المتاحة:", reply_markup=reply_markup)

    elif text == "🎯 عرض 1":
        set_pending_service(uid, "offer_1")
        await update.message.reply_text("🎯 عرض 1:\n💰 السعر: 10000 ل.س\nإذا موافق، أرسل: دفع offer_1")

    elif text == "🔥 عرض 2":
        set_pending_service(uid, "offer_2")
        await update.message.reply_text("🔥 عرض 2:\n💰 السعر: 15000 ل.س\nإذا موافق، أرسل: دفع offer_2")

    elif text == "💼 عرض 3":
        set_pending_service(uid, "offer_3")
        await update.message.reply_text("💼 عرض 3:\n💰 السعر: 20000 ل.س\nإذا موافق، أرسل: دفع offer_3")

    elif text == "🧠 عرض 4":
        set_pending_service(uid, "offer_4")
        await update.message.reply_text("🧠 عرض 4:\n💰 السعر: 25000 ل.س\nإذا موافق، أرسل: دفع offer_4")
        # إدخال عدد الصفحات
async def handle_numeric_input(update, context):
    uid = str(update.effective_user.id)
    text = update.message.text.strip()

    if is_waiting_receipt(uid):
        await verify_receipt(update, context)
        return

    service = get_pending_service(uid)
    if service == "power_point" and text.isdigit():
        pages = int(text)
        set_pending_pages(uid, pages)
        price = pages * 3500
        await update.message.reply_text(f"✅ السعر الإجمالي: {pages} × 3500 = {price} ل.س\nإذا كنت موافق، أرسل: دفع power_point")
    elif service == "word_final" and text.isdigit():
        pages = int(text)
        set_pending_pages(uid, pages)
        price = pages * context.user_data.get("word_price_per_page", 0)
        await update.message.reply_text(f"✅ السعر الإجمالي: {pages} × {context.user_data['word_price_per_page']} = {price} ل.س\nإذا كنت موافق، أرسل: دفع word")
    elif service == "translation_file" and text.isdigit():
        pages = int(text)
        set_pending_pages(uid, pages)
        price = pages * 6000  # سعر الورقة الواحدة
        await update.message.reply_text(f"✅ السعر الإجمالي: {pages} × 6000 = {price} ل.س\nإذا كنت موافق، أرسل: دفع translation_file")
# الدفع
async def handle_payment(update, context):
    uid = str(update.effective_user.id)
    text = update.message.text.strip().lower()
    service = get_pending_service(uid)
    pages = get_pending_pages(uid)
    price = 0

    if service == "power_point" and pages:
        price = pages * 3500
    elif service == "word_final" and pages:
        price_per_page = context.user_data.get("word_price_per_page", 0)
        price = pages * price_per_page
    elif service == "excel_table": price = 36000
    elif service == "excel_formulas": price = 120000
    elif service == "excel_chart": price = 145000
    elif service == "excel_later": price = 0
    elif service == "canva_ad": price = 15000
    elif service == "canva_card": price = 20000
    elif service == "canva_logo": price = 25000
    elif service == "shared_word": price = 50000
    elif service == "shared_word_excel": price = 63000
    elif service == "shared_word_ppt": price = 120000
    elif service == "photoshop_face": price = 18000
    elif service == "photoshop_enhance": price = 15000
    elif service == "photoshop_design": price = 22000
    elif service == "photoshop_later": price = 0
    elif service == "translation_article": price = 18000
    elif service == "translation_doc": price = 25000
    elif service == "translation_later": price = 0
    elif service == "translation_file" and pages: price = pages * 6000
    elif service == "offer_1": price = 10000
    elif service == "offer_2": price = 15000
    elif service == "offer_3": price = 20000
    elif service == "offer_4": price = 25000
    else:
        await update.message.reply_text("❌ لا يوجد خدمة معلقة أو بيانات غير مكتملة.")
        return

    balances = load_balances()
    current_balance = balances.get(uid, 0)
    if current_balance < price:
        await update.message.reply_text(f"❌ رصيدك غير كافي. رصيدك الحالي: {current_balance} ل.س")
        return

    balances[uid] = current_balance - price
    save_balances(balances)
    mark_waiting_request(uid, service)
    clear_pending_service(uid)
    

    await update.message.reply_text(
        "✅ تم الدفع بنجاح.\n📩 أرسل المعلومات والملفات المطلوبة، واسمك ورقمك الواتس للتواصل.\n📌 عند الانتهاء أرسل كلمة 'انتهيت'."
    )

# استخراج تفاصيل الخدمة
def get_service_details(uid, context):
    service = get_waiting_request(uid)
    pages = get_pending_pages(uid)
    price = 0
    name = "غير معروف"

    word_types = {
        2500: "تنسيق فقط",
        3500: "كتابة وتنسيق",
        4000: "كتابة وتنسيق ومعادلات"
    }

    if service == "word_final":
        price_per_page = context.user_data.get("word_price_per_page", 0)
        name = f"Word - {word_types.get(price_per_page, 'غير معروف')}"
        price = pages * price_per_page if pages else 0
    elif service == "power_point":
        name = "PowerPoint"
        price = pages * 3500 if pages else 0
    elif service == "excel_table": name = "Excel - تنسيق جدول"; price = 36000
    elif service == "excel_formulas": name = "Excel - إدخال معادلات"; price = 120000
    elif service == "excel_chart": name = "Excel - جدول وخطوط بيانية"; price = 145000
    elif service == "excel_later": name = "Excel - يحدد لاحقًا"; price = 0
    elif service == "canva_ad": name = "Canva - إعلان"; price = 15000
    elif service == "canva_card": name = "Canva - كرت حفلة"; price = 20000
    elif service == "canva_logo": name = "Canva - لوغو"; price = 25000
    elif service == "shared_word": name = "حلقة بحث Word"; price = 50000
    elif service == "shared_word_excel": name = "Word & Excel"; price = 63000
    elif service == "shared_word_ppt": name = "Word & PowerPoint"; price = 120000
    elif service == "photoshop_face": name = "فوتوشوب - تعديل وجه"; price = 18000
    elif service == "photoshop_enhance": name = "فوتوشوب - تحسين صورة"; price = 15000
    elif service == "photoshop_design": name = "فوتوشوب - تصميم ملفت"; price = 22000
    elif service == "photoshop_later": name = "فوتوشوب - يحدد لاحقًا"; price = 0
    elif service == "translation_article": name = "ترجمة - مقال"; price = 18000
    elif service == "translation_doc": name = "ترجمة - وثيقة رسمية"; price = 25000
    elif service == "translation_later": name = "ترجمة - يحدد لاحقًا"; price = 0
    elif service == "translation_file": name = "ترجمة - ملف"; price = pages * 6000 if pages else 0
    elif service == "offer_1": name = "🎯 عرض 1"; price = 10000
    elif service == "offer_2": name = "🔥 عرض 2"; price = 15000
    elif service == "offer_3": name = "💼 عرض 3"; price = 20000
    elif service == "offer_4": name = "🧠 عرض 4"; price = 25000
    return {
        "name": name,
        "pages": pages,
        "price": price
    }
    # استقبال الطلبات بعد الدفع
async def handle_user_submission(update, context):
    uid = str(update.effective_user.id)
    service = get_waiting_request(uid)
    if not service:
        return

    if update.message.text and "انتهيت" in update.message.text.strip().lower():
        submission = get_pending_submission(uid)
        details = get_service_details(uid, context)

        name = details.get("name", "غير معروف")
        pages = details.get("pages")
        price = details.get("price", 0)
        pages_text = pages if pages is not None else "غير محدد"

        header = (
            f"📥 طلب جديد\n"
            f"👤 المستخدم: {uid}\n"
            f"🛠 الخدمة: {name}\n"
            f"📄 عدد الصفحات: {pages_text}\n"
            f"💰 السعر المدفوع: {price} ل.س"
        )

        if submission and submission["texts"]:
            combined = "\n---\n".join(submission["texts"])
            await context.bot.send_message(chat_id=CHANNEL_ID, text=f"{header}\n📄 معلومات إضافية:\n{combined}")
        else:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=header)
        if submission and submission["files"]:
            for file_id in submission["files"]:
                try:
                    await context.bot.send_document(chat_id=CHANNEL_ID, document=file_id, caption=f"📎 ملف لخدمة {name}")
                except:
                    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=file_id, caption=f"🖼 صورة لخدمة {name}")
      
        # إرسال نسخة مختصرة إلى قناة الخدمة العامة
        try:
           await context.bot.send_message(
               chat_id=PUBLIC_SERVICE_CHANNEL_ID,
               text=(
                     f"📌 طلب جديد\n"
                     f"👤 الاسم: {update.effective_user.first_name}\n"
                     f"🆔 ID: {uid}\n"
                     f"🛠 الخدمة: {details.get('name', 'غير معروف')}\n"
                     f"💰 السعر: {details.get('price', 0)} ل.س"
        )
    )
        except Exception as e:
           print(f"⚠️ فشل إرسال الطلب إلى القناة العامة: {e}")
        await update.message.reply_text("✅ تم إرسال طلبك بنجاح.سنتواصل معك خلال بضعة ساعات, سيتم تنفيذه قريبًا.")

        try:
            await context.bot.send_message(chat_id=ADMIN_NOTIFICATIONS_ID, text=f"📢 تم استلام طلب جديد من المستخدم {uid} لخدمة {name}")
            
        except Exception as e:
            print(f"⚠️ فشل إرسال إشعار الإدارة: {e}")

        clear_pending_submission(uid)
        clear_waiting_request(uid)
        clear_pending_service(uid)
        clear_pending_pages(uid)
        return

    if update.message.text:
        save_pending_submission(uid, text=update.message.text.strip())
    elif update.message.document:
        save_pending_submission(uid, file_id=update.message.document.file_id)
    elif update.message.photo:
    # نأخذ أعلى جودة من الصور المرسلة
         photo_id = update.message.photo[-1].file_id
    save_pending_submission(uid, file_id=photo_id)

# استقبال إيصالات الدفع من القناة
async def handle_channel_receipt(update, context):
    if not update.channel_post or not update.channel_post.text:
        return
    text = update.channel_post.text.strip()
    amount_match = re.search(r"مبلغ\s+(\d+)\s*ل\.س", text)
    code_match = re.search(r"رقم العملية\s+هو\s+(\d+)", text)
    if amount_match and code_match:
        amount = int(amount_match.group(1))
        receipt_id = code_match.group(1)
        channel_receipts[receipt_id] = amount

# أوامر الإدارة لإرسال ملفات للمستخدمين
async def handle_admin_file_command(update, context):
    if not update.channel_post or not update.channel_post.text:
        return
    if update.channel_post.chat_id != ADMIN_COMMANDS_ID:
        return
    text = update.channel_post.text.strip()
    if text.startswith("ارسال_ملف"):
        parts = text.split()
        if len(parts) != 2 or not parts[1].isdigit():
            await context.bot.send_message(chat_id=update.channel_post.chat_id, text="❌ الصيغة: ارسال_ملف [ID]")
            return
        target_id = parts[1]
        admin_file_queue[update.channel_post.chat_id] = {"target": target_id, "texts": [], "files": []}
        await context.bot.send_message(chat_id=update.channel_post.chat_id, text=f"📌 جاهز لاستقبال الملفات للمستخدم ID: {target_id}\n✍️ أرسل الملفات أو النصوص، وعند الانتهاء أرسل كلمة انتهيت.")

async def handle_admin_file_submission(update, context):
    admin_id = update.channel_post.chat_id
    if admin_id != ADMIN_COMMANDS_ID or admin_id not in admin_file_queue:
        return

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
        # تشغيل البوت وربط جميع الـ handlers
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("channel", send_channel_links))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^💰 تعبئة رصيد$"), ask_receipt))

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^📄 ملف Word$|^1️⃣ تنسيق فقط$|^2️⃣ كتابة وتنسيق$|^3️⃣ كتابة وتنسيق ومعادلات$|^4️⃣ كتابة وتنسيق وصور$"), handle_word_selection))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^📊 ملف Excel$|^1️⃣ تنسيق جدول$|^2️⃣ إدخال معادلات$|^3️⃣ جدول وخطوط بيانية$|^4️⃣ يحدد لاحقًا$"), handle_excel_selection))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^🎨 تصميم Canva$|^📢 إعلان$|^🎉 كرت حفلة$|^🖼 لوغو Logo$"), handle_canva_selection))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^🧩 وظيفة مشتركة$|^🔍 حلقة بحث Word$|^🧩 Word & Excel$|^🧩 Word & PowerPoint$"), handle_shared_job_selection))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^📽 PowerPoint$"), handle_ppt_selection))
# زر فوتوشوب وخياراته
    app.add_handler(MessageHandler(
    filters.TEXT & filters.Regex(r"^📷 فوتوشوب$|^1️⃣ تعديل وجه شخص$|^2️⃣ تحسين صورة$|^3️⃣ تصميم ملفت$|^4️⃣ يحدد لاحقًا$"),
    handle_photoshop_selection
))

# زر ترجمة وخياراته
    app.add_handler(MessageHandler(
    filters.TEXT & filters.Regex(r"^🌐 ترجمة$|^1️⃣ ترجمة ملف$|^2️⃣ ترجمة مقال$|^3️⃣ ترجمة وثيقة رسمية$|^4️⃣ يحدد لاحقًا$"),
    handle_translation_selection
))
    app.add_handler(MessageHandler(
    filters.TEXT & filters.Regex(r"^🎁 العروض$|^🎯 عرض 1$|^🔥 عرض 2$|^💼 عرض 3$|^🧠 عرض 4$"),
    handle_offers_selection
))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"(?i)^دفع"), handle_payment))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^\d+$"), handle_numeric_input))

    app.add_handler(MessageHandler(filters.ALL & filters.UpdateType.MESSAGE, handle_user_submission))
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, handle_channel_receipt))
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, handle_admin_file_command))
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, handle_admin_file_submission))

    print("✅ البوت يعمل الآن...")
    app.run_polling()
