from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from telegram import Update
from config import BOT_TOKEN

# دالة استخراج معرف القناة
async def reveal_channel_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post:
        chat_id = update.channel_post.chat_id
        print(f"📌 chat_id = {chat_id}")
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"📌 معرف القناة (chat_id): {chat_id}",
            parse_mode="Markdown"
        )

# تشغيل التطبيق
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, reveal_channel_id))

if __name__ == "__main__":
    print("✅ جاهز لاستقبال منشورات القناة...")
    app.run_polling()