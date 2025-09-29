from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

# إعدادات البوت
BOT_TOKEN = "8067422944:AAGFjWo7Erb333J2AX0PUVY1ywGPnoGYXnc"
ADMIN_ID =  1440549574 # ضع معرف حساب الإدمن (وليس معرف قناة)
admin_file_queue = {}

# 🎛️ عرض لوحة التحكم عند /start فقط
async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    keyboard = [
        [InlineKeyboardButton("📤 إرسال ملفات", callback_data="start_send")],
        [InlineKeyboardButton("✅ إنهاء الإرسال", callback_data="finish_send")]
    ]
    await update.message.reply_text("🎛️ لوحة التحكم:", reply_markup=InlineKeyboardMarkup(keyboard))

# 🧩 التعامل مع ضغط الأزرار
async def handle_admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    if query.data == "start_send":
        admin_file_queue[ADMIN_ID] = {
            "target": None,
            "texts": [],
            "files": [],
            "awaiting_id": True
        }
        await query.message.reply_text("🆔 أرسل ID المستخدم الآن:")

    elif query.data == "finish_send":
        data = admin_file_queue.get(ADMIN_ID)
        if not data or not data["target"]:
            await query.message.reply_text("⚠️ لم يتم تحديد المستخدم أو لا يوجد ملفات.")
            return

        target = int(data["target"])
        try:
            if data["texts"]:
                combined = "\n---\n".join(data["texts"])
                await context.bot.send_message(chat_id=target, text=f"📤 ملفات جاهزة:\n{combined}")
            for file_id in data["files"]:
                await context.bot.send_document(chat_id=target, document=file_id)
            await query.message.reply_text("✅ تم إرسال الملفات للمستخدم.")
            admin_file_queue.pop(ADMIN_ID)
        except Exception as e:
            await query.message.reply_text(f"❌ فشل الإرسال: {e}")

# 📥 استقبال ID المستخدم أو الملفات
async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID or ADMIN_ID not in admin_file_queue:
        return

    data = admin_file_queue[ADMIN_ID]

    if data.get("awaiting_id"):
        if update.message.text and update.message.text.strip().isdigit():
            data["target"] = update.message.text.strip()
            data["awaiting_id"] = False
            await update.message.reply_text("📥 الآن أرسل الملفات أو النصوص، ثم اضغط زر ✅ إنهاء الإرسال.")
        else:
            await update.message.reply_text("⚠️ الرجاء إرسال رقم ID صحيح.")
        return

    if update.message.text:
        data["texts"].append(update.message.text.strip())
    elif update.message.document:
        data["files"].append(update.message.document.file_id)
    elif update.message.photo:
        data["files"].append(update.message.photo[-1].file_id)

# 🚀 تشغيل البوت
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # عرض لوحة التحكم عند /start فقط
    app.add_handler(CommandHandler("admin", show_admin_panel))

    # التعامل مع ضغط الأزرار
    app.add_handler(CallbackQueryHandler(handle_admin_buttons))

    # استقبال الملفات والنصوص من الإدمن
    app.add_handler(MessageHandler(filters.ALL & filters.User(user_id=ADMIN_ID), handle_admin_input))

    print("✅ البوت يعمل الآن بواجهة الإدمن...")
    app.run_polling()