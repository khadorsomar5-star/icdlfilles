from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from sender_bot import send_file_to_user, send_text_to_user

BOT_TOKEN = "8067422944:AAGFjWo7Erb333J2AX0PUVY1ywGPnoGYXnc"
ADMIN_ID = 1440549574 # ← غيّر لـ ID تبعك الحقيقي

admin_target_map = {}

async def show_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    keyboard = [[InlineKeyboardButton("📤 إرسال للمستخدم", callback_data="set_target")]]
    await update.message.reply_text("🎛 اختر الإجراء:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        return
    admin_target_map[ADMIN_ID] = {"awaiting_id": True}
    await query.message.reply_text("🆔 أرسل الآن ID المستخدم يلي بدك ترسل له.")

async def receive_target_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    data = admin_target_map.get(ADMIN_ID)
    if not data or not data.get("awaiting_id"):
        return
    if update.message.text and update.message.text.strip().isdigit():
        admin_target_map[ADMIN_ID] = {"target": update.message.text.strip()}
        await update.message.reply_text(f"🎯 سيتم إرسال الملفات تلقائيًا للمستخدم {update.message.text.strip()}", parse_mode="Markdown")

async def auto_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    data = admin_target_map.get(ADMIN_ID)
    if not data or not data.get("target"):
        return
    target_id = data["target"]
    if update.message.document:
        file_id = update.message.document.file_id
        send_file_to_user(target_id, file_id)
        await update.message.reply_text("✅ تم إرسال الملف تلقائيًا.")
    elif update.message.text:
        send_text_to_user(target_id, update.message.text)
        await update.message.reply_text("✅ تم إرسال الرسالة تلقائيًا.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("panel", show_panel))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & filters.User(ADMIN_ID), receive_target_id))
    app.add_handler(MessageHandler(filters.ALL & filters.User(ADMIN_ID), auto_forward))
    print("✅ البوت شغّال...")
    app.run_polling()