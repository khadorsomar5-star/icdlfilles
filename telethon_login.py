from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters
)
from config import BOT_TOKEN, ADMIN_ID

# استيراد دوال تعبئة الرصيد
from handlers.verify_sms import ask_receipt, verify_receipt

# استيراد باقي الـ handlers
from handlers.start import (
    start_handler,
    word_file_handler, pay_word_handler,
    excel_file_handler, pay_excel_handler,
    ppt_file_handler, pay_ppt_handler,
    shared_task_handler, pay_shared_handler
)
from handlers.services import services_handler
from handlers.extra import add_receipt_handler, register_user_handler
from handlers.requests import collect_request_handler, verify_receipt_handler
from handlers.admin_receipts import register_receipt

# بناء التطبيق
app = ApplicationBuilder().token(BOT_TOKEN).build()

# زر تعبئة الرصيد
app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^💰 تعبئة رصيد$"), ask_receipt))

# استقبال رقم العملية فقط إذا المستخدم داخل مرحلة التحقق
app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^\d+$"), verify_receipt))

# تسجيل الإيصالات من الإدمن فقط
app.add_handler(MessageHandler(filters.TEXT & filters.User(user_id=int(ADMIN_ID)), register_receipt))

# باقي الخدمات
handlers = [
    start_handler,
    word_file_handler, pay_word_handler,
    excel_file_handler, pay_excel_handler,
    ppt_file_handler, pay_ppt_handler,
    shared_task_handler, pay_shared_handler,
    services_handler,
    add_receipt_handler, register_user_handler,
    collect_request_handler,
    verify_receipt_handler
]

for handler in handlers:
    app.add_handler(handler)

# بدء التشغيل
if __name__ == "__main__":
    print("✅ البوت جاهز ويعمل الآن...")
    app.run_polling()