import json
from telegram import Update
from telegram.ext import ContextTypes
from check_receipt import check_receipt

def load_verified_receipts():
    try:
        with open('data/verified_receipts.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_verified_receipt(receipt, user_id):
    receipts = load_verified_receipts()
    receipts[receipt] = user_id
    with open('data/verified_receipts.json', 'w') as f:
        json.dump(receipts, f)

def load_balances():
    try:
        with open('data/user_balances.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def save_balances(balances):
    with open('data/user_balances.json', 'w') as f:
        json.dump(balances, f)

# بدء التحقق بعد الضغط على الزر
async def ask_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_receipt"] = True
    await update.message.reply_text("💰 أرسل رقم العملية ليتم التحقق منه.")

# التحقق من رقم العملية
async def verify_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_receipt"):
        return  # تجاهل إذا المستخدم مو ضمن مرحلة التحقق

    receipt_text = update.message.text.strip()
    user_id = str(update.effective_user.id)

    if not receipt_text.isdigit():
        await update.message.reply_text("❌ الرجاء إرسال رقم عملية صالح.")
        return

    amount = await check_receipt(receipt_text)
    if amount is None:
        await update.message.reply_text("❌ لم يتم العثور على هذا الإيصال داخل القناة.")
        return

    verified = load_verified_receipts()
    if receipt_text in verified:
        await update.message.reply_text("⚠️ هذا الإيصال تم استخدامه مسبقًا.")
        return

    balances = load_balances()
    balances[user_id] = balances.get(user_id, 0) + amount
    save_balances(balances)
    save_verified_receipt(receipt_text, user_id)

    context.user_data["awaiting_receipt"] = False
    await update.message.reply_text(f"✅ تم إضافة {amount} ل.س إلى رصيدك.")