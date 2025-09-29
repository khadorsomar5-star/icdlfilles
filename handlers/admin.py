from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

ADMIN_ID = 1440549574  # تأكد أنه نفس المعرف

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ هذا الأمر مخصص للإدمن فقط.")
        return
    keyboard = [
        [InlineKeyboardButton("📤 إرسال ملفات", callback_data="start_send")],
        [InlineKeyboardButton("✅ إنهاء الإرسال", callback_data="finish_send")]
    ]
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🎛 لوحة التحكم:", reply_markup=InlineKeyboardMarkup(keyboard))
    