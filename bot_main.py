from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from handlers.start import (
    start_handler, fill_handler, word_file_handler, pay_word_handler,
    excel_file_handler, pay_excel_handler, ppt_file_handler, pay_ppt_handler,
    shared_task_handler, pay_shared_handler
)
from handlers.services import services_handler
from handlers.requests import verify_receipt_handler, collect_request_handler
from handlers.extra import add_receipt_handler, register_user_handler
from handlers.admin_receipts import register_receipt
from handlers.verify_sms import verify_handler

from config import BOT_TOKEN, ADMIN_ID

# بناء التطبيق
app = ApplicationBuilder().token(BOT_TOKEN).build()

# تسجيل جميع الهاندلرز
handlers = [
    start_handler, fill_handler,
    word_file_handler, pay_word_handler,
    excel_file_handler, pay_excel_handler,
    ppt_file_handler, pay_ppt_handler,
    shared_task_handler, pay_shared_handler,
    services_handler, verify_handler,
    add_receipt_handler, register_user_handler,
    verify_receipt_handler, collect_request_handler
]

for handler in handlers:
    app.add_handler(handler)

# تسجيل الإيصالات من الإدمن فقط
app.add_handler(MessageHandler(
    filters.TEXT & filters.User(user_id=int(ADMIN_ID)),
    register_receipt
))

# تشغيل البوت
if __name__== "__main__":
    print("✅ البوت جاهز ويعمل الآن...")
    app.run_polling()
    