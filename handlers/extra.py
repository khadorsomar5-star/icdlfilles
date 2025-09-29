import json
import os
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes
from config import ADMIN_ID

RECEIPT_FILE = 'data/receipts.json'
USER_FILE = 'data/users.json'

# ✅ دالة إضافة إيصال (من قبل الإدمن فقط)
async def add_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    if user_id != int(ADMIN_ID):
        await update.message.reply_text("❌ فقط الإدمن يمكنه تسجيل الإيصالات.")
        return

    if not text.startswith("إضافة"):
        return

    parts = text.split()
    if len(parts) != 3:
        await update.message.reply_text("❌ الصيغة غير صحيحة. استخدم: إضافة <الإيصال> <الفئة>")
        return

    receipt = parts[1]
    try:
        amount = int(parts[2])
    except ValueError:
        await update.message.reply_text("❌ الفئة غير صحيحة.")
        return

    # تحميل الإيصالات
    if not os.path.exists(RECEIPT_FILE):
        receipts = {}
    else:
        try:
            with open(RECEIPT_FILE, 'r', encoding='utf-8') as f:
                receipts = json.load(f)
        except json.JSONDecodeError:
            receipts = {}

    receipts[receipt] = amount

    try:
        with open(RECEIPT_FILE, 'w', encoding='utf-8') as f:
            json.dump(receipts, f, ensure_ascii=False, indent=2)
        await update.message.reply_text(f"✅ تم إضافة الإيصال {receipt} بقيمة {amount} نقطة.")
    except Exception as e:
        await update.message.reply_text("❌ حدث خطأ أثناء حفظ الإيصال.")
        print(f"خطأ في حفظ الإيصال: {e}")

add_receipt_handler = MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    add_receipt
)

# ✅ دالة تسجيل المستخدم
async def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = str(user.id)
    username = user.username or "بدون اسم"

    if not os.path.exists(USER_FILE):
        users = {}
    else:
        try:
            with open(USER_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
        except json.JSONDecodeError:
            users = {}

    if user_id not in users:
        users[user_id] = {
            "username": username,
            "first_name": user.first_name,
            "last_name": user.last_name or ""
        }

        try:
            with open(USER_FILE, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            await update.message.reply_text(
                f"✅ تم تسجيلك.\n📌 رقمك: {user_id}\n👤 اسم المستخدم: @{username}"
            )
        except Exception as e:
            await update.message.reply_text("❌ حدث خطأ أثناء حفظ بياناتك.")
            print(f"خطأ في حفظ المستخدم: {e}")
    else:
        await update.message.reply_text(
            f"📌 رقمك: {user_id}\n👤 اسم المستخدم: @{username}"
        )

register_user_handler = MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    register_user
)