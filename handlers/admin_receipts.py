import json
import os
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID

RECEIPT_FILE = 'data/valid_receipts.json'

async def register_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # ✅ التحقق من صلاحية المستخدم
    if user_id != ADMIN_ID:
        return  # تجاهل أي شخص غير الإدمن

    # ✅ التحقق من أن النص رقم صالح
    if not text.isdigit():
        await update.message.reply_text("❌ الرجاء إرسال رقم إيصال صالح.")
        return

    # ✅ تحميل الإيصالات المسجلة مسبقًا
    if not os.path.exists(RECEIPT_FILE):
        valid_receipts = []
    else:
        try:
            with open(RECEIPT_FILE, 'r', encoding='utf-8') as f:
                valid_receipts = json.load(f)
        except json.JSONDecodeError:
            valid_receipts = []

    # ✅ التحقق من التكرار
    if text in valid_receipts:
        await update.message.reply_text("⚠️ هذا الإيصال مسجل مسبقًا.")
        return

    # ✅ إضافة الإيصال وتخزينه
    valid_receipts.append(text)
    try:
        with open(RECEIPT_FILE, 'w', encoding='utf-8') as f:
            json.dump(valid_receipts, f, ensure_ascii=False, indent=2)
        await update.message.reply_text(f"✅ تم تسجيل الإيصال: {text}")
    except Exception as e:
        await update.message.reply_text("❌ حدث خطأ أثناء حفظ الإيصال.")
        print(f"خطأ في حفظ الإيصال: {e}")