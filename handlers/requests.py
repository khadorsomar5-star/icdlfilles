import json
import os
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

RECEIPT_FILE = 'data/receipts.json'
USED_RECEIPT_FILE = 'data/used_receipts.json'
PAID_USERS_FILE = 'data/paid_users.json'
REQUESTS_FILE = 'data/requests.json'

# ✅ دالة التحقق من الإيصال من المستخدم
async def verify_receipt_from_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    receipt = update.message.text.strip()

    if not receipt.isdigit():
        await update.message.reply_text("❌ الرجاء إرسال رقم إيصال صالح (أرقام فقط).")
        return

    # تحميل الإيصالات المسجلة
    receipts = {}
    if os.path.exists(RECEIPT_FILE):
        try:
            with open(RECEIPT_FILE, 'r', encoding='utf-8') as f:
                receipts = json.load(f)
        except json.JSONDecodeError:
            pass

    if receipt not in receipts:
        await update.message.reply_text("❌ هذا الرقم غير مسجل كإيصال دفع.")
        return

    # تحميل الإيصالات المستخدمة
    used = []
    if os.path.exists(USED_RECEIPT_FILE):
        try:
            with open(USED_RECEIPT_FILE, 'r', encoding='utf-8') as f:
                used = json.load(f)
        except json.JSONDecodeError:
            pass

    if receipt in used:
        await update.message.reply_text("⚠️ هذا الإيصال تم استخدامه مسبقًا.")
        return

    # تسجيل الإيصال كمستخدم
    used.append(receipt)
    with open(USED_RECEIPT_FILE, 'w', encoding='utf-8') as f:
        json.dump(used, f, ensure_ascii=False, indent=2)

    # تسجيل المستخدم كمدفوع
    paid = {}
    if os.path.exists(PAID_USERS_FILE):
        try:
            with open(PAID_USERS_FILE, 'r', encoding='utf-8') as f:
                paid = json.load(f)
        except json.JSONDecodeError:
            pass

    paid[user_id] = receipts[receipt]  # حفظ الفئة أو القيمة المرتبطة بالإيصال
    with open(PAID_USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(paid, f, ensure_ascii=False, indent=2)

    await update.message.reply_text("✅ تم التحقق من إيصالك بنجاح.\n📥 يمكنك الآن إرسال الملف أو الطلب.")

verify_receipt_handler = MessageHandler(
    filters.TEXT & filters.Regex(r'^\d+$'),
    verify_receipt_from_user
)

# ✅ دالة استقبال الطلب بعد التحقق
async def collect_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    username = user.username or "بدون اسم"
    text = update.message.text or ""
    file_id = None

    if update.message.document:
        file_id = update.message.document.file_id
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id

    # التحقق من حالة الدفع
    paid = {}
    if os.path.exists(PAID_USERS_FILE):
        try:
            with open(PAID_USERS_FILE, 'r', encoding='utf-8') as f:
                paid = json.load(f)
        except json.JSONDecodeError:
            pass

    service = paid.get(user_id)
    if not service:
        await update.message.reply_text("❌ لم يتم التحقق من الدفع بعد.")
        return

    # تسجيل الطلب
    requests = []
    if os.path.exists(REQUESTS_FILE):
        try:
            with open(REQUESTS_FILE, 'r', encoding='utf-8') as f:
                requests = json.load(f)
        except json.JSONDecodeError:
            pass

    requests.append({
        "user_id": user_id,
        "username": username,
        "service": service,
        "text": text,
        "file_id": file_id
    })

    with open(REQUESTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(requests, f, ensure_ascii=False, indent=2)

    await update.message.reply_text("📥 تم استلام طلبك بنجاح، سيتم تنفيذه قريبًا.")

collect_request_handler = MessageHandler(
    filters.Document.ALL | filters.PHOTO | (filters.TEXT & ~filters.Regex(r'^\d+$')),
    collect_request
)