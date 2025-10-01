import json
from main import start
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters
from main import (
    load_balances,
    save_balances,
    mark_waiting_request
)
# دوال المساعدة العامة
async def send_service(update, context, label, price, service_key):
    await update.message.reply_text(
        f"{label}\n💰 السعر: {price} ليرة سورية\nإذا كنت موافق، أرسل: دفع {service_key}",
        parse_mode="Markdown"
    )

async def pay_service(update, context, price, service_key):
    user_id = str(update.effective_user.id)
    balances = load_balances()
    balance = balances.get(user_id, 0)

    if balance < price:
        await update.message.reply_text("❌ رصيدك غير كافي لهذه الخدمة.")
        return

    balances[user_id] = balance - price
    save_balances(balances)
    mark_waiting_request(user_id, service_key)
    await update.message.reply_text(
        f"✅ تم الدفع بنجاح.\n📥 الرجاء الآن إرسال المعلومات أو الملف المطلوب لخدمة *{service_key}*.",
        parse_mode="Markdown"
    )
#فوتوشوب
# فوتوشوب
async def send_photoshop_menu(update, context):
    keyboard = [["1️⃣ تعديل وجه شخص"], ["2️⃣ تحسين صورة"], ["3️⃣ تصميم ملفت"], ["4️⃣ يحدد لاحقًا"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("📷 اختر نوع خدمة فوتوشوب المطلوبة:", reply_markup=reply_markup)

async def send_photoshop_face(update, context): await send_service(update, context, "🧑‍🎨 تعديل وجه شخص", 18000, "photoshop_face")
async def pay_photoshop_face(update, context): await pay_service(update, context, 18000, "photoshop_face")

async def send_photoshop_enhance(update, context): await send_service(update, context, "🖼 تحسين صورة", 15000, "photoshop_enhance")
async def pay_photoshop_enhance(update, context): await pay_service(update, context, 15000, "photoshop_enhance")

async def send_photoshop_design(update, context): await send_service(update, context, "🎯 تصميم ملفت", 22000, "photoshop_design")
async def pay_photoshop_design(update, context): await pay_service(update, context, 22000, "photoshop_design")

async def send_photoshop_later(update, context): await send_service(update, context, "📷 فوتوشوب - يحدد لاحقًا", 0, "photoshop_later")
async def pay_photoshop_later(update, context): await pay_service(update, context, 0, "photoshop_later")
#ترجمة
# ترجمة
async def send_translation_menu(update, context):
    keyboard = [["1️⃣ ترجمة ملف"], ["2️⃣ ترجمة مقال"], ["3️⃣ ترجمة وثيقة رسمية"], ["4️⃣ يحدد لاحقًا"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("🌐 اختر نوع خدمة الترجمة المطلوبة:", reply_markup=reply_markup)

async def send_translation_file(update, context): await update.message.reply_text("📄 ترجمة ملف:\n💬 كم عدد الأوراق؟")
async def pay_translation_file(update, context): await pay_service(update, context, 0, "translation_file")  # السعر يحسب لاحقًا

async def send_translation_article(update, context): await send_service(update, context, "📝 ترجمة مقال", 18000, "translation_article")
async def pay_translation_article(update, context): await pay_service(update, context, 18000, "translation_article")

async def send_translation_doc(update, context): await send_service(update, context, "📑 ترجمة وثيقة رسمية", 25000, "translation_doc")
async def pay_translation_doc(update, context): await pay_service(update, context, 25000, "translation_doc")

async def send_translation_later(update, context): await send_service(update, context, "🌐 ترجمة - يحدد لاحقًا", 0, "translation_later")
async def pay_translation_later(update, context): await pay_service(update, context, 0, "translation_later")

#العروض
async def send_offers_menu(update, context):
    keyboard = [["🎯 عرض 1"], ["🔥 عرض 2"], ["💼 عرض 3"], ["🧠 عرض 4"], ["🔙 رجوع"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("🎁 اختر أحد العروض المتاحة:", reply_markup=reply_markup)
async def send_offer_1(update, context): await send_service(update, context, "🎯 عرض 1", 10000, "offer_1")
async def pay_offer_1(update, context): await pay_service(update, context, 10000, "offer_1")

async def send_offer_2(update, context): await send_service(update, context, "🔥 عرض 2", 15000, "offer_2")
async def pay_offer_2(update, context): await pay_service(update, context, 15000, "offer_2")

async def send_offer_3(update, context): await send_service(update, context, "💼 عرض 3", 20000, "offer_3")
async def pay_offer_3(update, context): await pay_service(update, context, 20000, "offer_3")

async def send_offer_4(update, context): await send_service(update, context, "🧠 عرض 4", 25000, "offer_4")
async def pay_offer_4(update, context): await pay_service(update, context, 25000, "offer_4")

# Word
async def send_word_format(update, context): await send_service(update, context, "📄 Word - تنسيق فقط", 2000, "word_format")
async def pay_word_format(update, context): await pay_service(update, context, 2000, "word_format")

async def send_word_write(update, context): await send_service(update, context, "📄 Word - كتابة وتنسيق", 3000, "word_write")
async def pay_word_write(update, context): await pay_service(update, context, 3000, "word_write")

async def send_word_equations(update, context): await send_service(update, context, "📄 Word - كتابة وتنسيق ومعادلات", 3500, "word_equations")
async def pay_word_equations(update, context): await pay_service(update, context, 3500, "word_equations")

async def send_word_images(update, context): await send_service(update, context, "📄 Word - كتابة وتنسيق وصور", 3000, "word_images")
async def pay_word_images(update, context): await pay_service(update, context, 3000, "word_images")

# Excel
async def send_excel_table(update, context): await send_service(update, context, "📊 Excel - تنسيق جدول", 30000, "excel_table")
async def pay_excel_table(update, context): await pay_service(update, context, 30000, "excel_table")

async def send_excel_formulas(update, context): await send_service(update, context, "📊 Excel - إدخال معادلات", 100000, "excel_formulas")
async def pay_excel_formulas(update, context): await pay_service(update, context, 100000, "excel_formulas")

async def send_excel_chart(update, context): await send_service(update, context, "📊 Excel - جدول وخطوط بيانية", 125000, "excel_chart")
async def pay_excel_chart(update, context): await pay_service(update, context, 125000, "excel_chart")

async def send_excel_later(update, context): await send_service(update, context, "📊 Excel - يحدد لاحقًا", 0, "excel_later")
async def pay_excel_later(update, context): await pay_service(update, context, 0, "excel_later")

# PowerPoint
async def send_ppt_dynamic(update, context): await update.message.reply_text("🎞 كم عدد الصفحات المطلوبة لعرض PowerPoint؟")
async def pay_ppt(update, context): await pay_service(update, context, 30, "ppt")

# الوظائف المشتركة
async def send_shared_task(update, context):
    keyboard = [["🔍 حلقة بحث Word"], ["🧩 Word & PowerPoint"], ["🧩 Word & Excel"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("🧩 اختر نوع الوظيفة المشتركة:", reply_markup=reply_markup)

async def send_shared_word(update, context): await send_service(update, context, "🔍 حلقة بحث Word", 50000, "shared_word")
async def pay_shared_word(update, context): await pay_service(update, context, 50000, "shared_word")

async def send_shared_word_ppt(update, context): await send_service(update, context, "🧩 Word & PowerPoint", 90000, "shared_word_ppt")
async def pay_shared_word_ppt(update, context): await pay_service(update, context, 90000, "shared_word_ppt")

async def send_shared_word_excel(update, context): await send_service(update, context, "🧩 Word & Excel", 110000, "shared_word_excel")
async def pay_shared_word_excel(update, context): await pay_service(update, context, 110000, "shared_word_excel")
# ربط الـ handlers
start_handler = CommandHandler("start", start)

# Word
word_format_handler = MessageHandler(filters.TEXT & filters.Regex("^1️⃣ تنسيق فقط$"), send_word_format)
pay_word_format_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع word_format$"), pay_word_format)

word_write_handler = MessageHandler(filters.TEXT & filters.Regex("^2️⃣ كتابة وتنسيق$"), send_word_write)
pay_word_write_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع word_write$"), pay_word_write)

word_equations_handler = MessageHandler(filters.TEXT & filters.Regex("^3️⃣ كتابة وتنسيق ومعادلات$"), send_word_equations)
pay_word_equations_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع word_equations$"), pay_word_equations)

word_images_handler = MessageHandler(filters.TEXT & filters.Regex("^4️⃣ كتابة وتنسيق وصور$"), send_word_images)
pay_word_images_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع word_images$"), pay_word_images)

# Excel
excel_table_handler = MessageHandler(filters.TEXT & filters.Regex("^1️⃣ تنسيق جدول$"), send_excel_table)
pay_excel_table_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع excel_table$"), pay_excel_table)

excel_formulas_handler = MessageHandler(filters.TEXT & filters.Regex("^2️⃣ إدخال معادلات$"), send_excel_formulas)
pay_excel_formulas_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع excel_formulas$"), pay_excel_formulas)

excel_chart_handler = MessageHandler(filters.TEXT & filters.Regex("^3️⃣ جدول وخطوط بيانية$"), send_excel_chart)
pay_excel_chart_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع excel_chart$"), pay_excel_chart)

excel_later_handler = MessageHandler(filters.TEXT & filters.Regex("^4️⃣ يحدد لاحقًا$"), send_excel_later)
pay_excel_later_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع excel_later$"), pay_excel_later)

# PowerPoint
ppt_file_handler = MessageHandler(filters.TEXT & filters.Regex("^📽 PowerPoint$"), send_ppt_dynamic)
pay_ppt_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع ppt$"), pay_ppt)

# الوظائف المشتركة
shared_task_handler = MessageHandler(filters.TEXT & filters.Regex("^🧩 وظيفة مشتركة$"), send_shared_task)

shared_word_handler = MessageHandler(filters.TEXT & filters.Regex("^🔍 حلقة بحث Word$"), send_shared_word)
pay_shared_word_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع shared_word$"), pay_shared_word)

shared_word_ppt_handler = MessageHandler(filters.TEXT & filters.Regex("^🧩 Word & PowerPoint$"), send_shared_word_ppt)
pay_shared_word_ppt_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع shared_word_ppt$"), pay_shared_word_ppt)

shared_word_excel_handler = MessageHandler(filters.TEXT & filters.Regex("^🧩 Word & Excel$"), send_shared_word_excel)
pay_shared_word_excel_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع shared_word_excel$"), pay_shared_word_excel)
# Canva
async def send_canva_menu(update, context):
    keyboard = [["📢 إعلان"], ["🎉 كرت حفلة"], ["🖼 لوغو Logo"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("🎨 اختر نوع التصميم المطلوب:", reply_markup=reply_markup)

async def send_canva_ad(update, context): await send_service(update, context, "📢 تصميم إعلان", 15000, "canva_ad")
async def pay_canva_ad(update, context): await pay_service(update, context, 15000, "canva_ad")

async def send_canva_card(update, context): await send_service(update, context, "🎉 تصميم كرت حفلة", 20000, "canva_card")
async def pay_canva_card(update, context): await pay_service(update, context, 20000, "canva_card")

async def send_canva_logo(update, context): await send_service(update, context, "🖼 تصميم لوغو", 25000, "canva_logo")
async def pay_canva_logo(update, context): await pay_service(update, context, 25000, "canva_logo")
canva_menu_handler = MessageHandler(filters.TEXT & filters.Regex("^🎨 تصميم Canva$"), send_canva_menu)

canva_ad_handler = MessageHandler(filters.TEXT & filters.Regex("^📢 إعلان$"), send_canva_ad)
pay_canva_ad_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع canva_ad$"), pay_canva_ad)

canva_card_handler = MessageHandler(filters.TEXT & filters.Regex("^🎉 كرت حفلة$"), send_canva_card)
pay_canva_card_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع canva_card$"), pay_canva_card)

canva_logo_handler = MessageHandler(filters.TEXT & filters.Regex("^🖼 لوغو Logo$"), send_canva_logo)
pay_canva_logo_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع canva_logo$"), pay_canva_logo)
# فوتوشوب
photoshop_menu_handler = MessageHandler(filters.TEXT & filters.Regex("^📷 فوتوشوب$"), send_photoshop_menu)
photoshop_face_handler = MessageHandler(filters.TEXT & filters.Regex("^1️⃣ تعديل وجه شخص$"), send_photoshop_face)
pay_photoshop_face_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع photoshop_face$"), pay_photoshop_face)

photoshop_enhance_handler = MessageHandler(filters.TEXT & filters.Regex("^2️⃣ تحسين صورة$"), send_photoshop_enhance)
pay_photoshop_enhance_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع photoshop_enhance$"), pay_photoshop_enhance)

photoshop_design_handler = MessageHandler(filters.TEXT & filters.Regex("^3️⃣ تصميم ملفت$"), send_photoshop_design)
pay_photoshop_design_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع photoshop_design$"), pay_photoshop_design)

photoshop_later_handler = MessageHandler(filters.TEXT & filters.Regex("^4️⃣ يحدد لاحقًا$"), send_photoshop_later)
pay_photoshop_later_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع photoshop_later$"), pay_photoshop_later)

# ترجمة
translation_menu_handler = MessageHandler(filters.TEXT & filters.Regex("^🌐 ترجمة$"), send_translation_menu)
translation_file_handler = MessageHandler(filters.TEXT & filters.Regex("^1️⃣ ترجمة ملف$"), send_translation_file)
pay_translation_file_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع translation_file$"), pay_translation_file)

translation_article_handler = MessageHandler(filters.TEXT & filters.Regex("^2️⃣ ترجمة مقال$"), send_translation_article)
pay_translation_article_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع translation_article$"), pay_translation_article)

translation_doc_handler = MessageHandler(filters.TEXT & filters.Regex("^3️⃣ ترجمة وثيقة رسمية$"), send_translation_doc)
pay_translation_doc_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع translation_doc$"), pay_translation_doc)

translation_later_handler = MessageHandler(filters.TEXT & filters.Regex("^4️⃣ يحدد لاحقًا$"), send_translation_later)
pay_translation_later_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع translation_later$"), pay_translation_later)
#العروض
offers_menu_handler = MessageHandler(filters.TEXT & filters.Regex("^🎁 العروض$"), send_offers_menu)

offer_1_handler = MessageHandler(filters.TEXT & filters.Regex("^🎯 عرض 1$"), send_offer_1)
pay_offer_1_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع offer_1$"), pay_offer_1)

offer_2_handler = MessageHandler(filters.TEXT & filters.Regex("^🔥 عرض 2$"), send_offer_2)
pay_offer_2_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع offer_2$"), pay_offer_2)

offer_3_handler = MessageHandler(filters.TEXT & filters.Regex("^💼 عرض 3$"), send_offer_3)
pay_offer_3_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع offer_3$"), pay_offer_3)

offer_4_handler = MessageHandler(filters.TEXT & filters.Regex("^🧠 عرض 4$"), send_offer_4)
pay_offer_4_handler = MessageHandler(filters.TEXT & filters.Regex("^دفع offer_4$"), pay_offer_4)
