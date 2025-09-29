from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 تعبئة رصيد", callback_data="top_up")],
        [InlineKeyboardButton("📊 عرض الرصيد", callback_data="check_balance")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📋 خدماتنا المتاحة:",
        reply_markup=reply_markup
    )

services_handler = CommandHandler("services", services)