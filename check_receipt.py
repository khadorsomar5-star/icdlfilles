from telethon import TelegramClient
from telethon.tl.functions.messages import ImportChatInviteRequest
import re
from config import API_ID, API_HASH, INVITE_LINK

client = TelegramClient('session', API_ID, API_HASH)

async def check_receipt(receipt_number: str) -> int | None:
    try:
        await client.start()

        # استخراج كود الدعوة من الرابط
        invite_code = INVITE_LINK.split('+')[-1]
        entity = await client(ImportChatInviteRequest(invite_code))

        async for message in client.iter_messages(entity, limit=200):
            if message.text and receipt_number in message.text:
                match = re.search(r"(?:مبلغ|قيمة|تم تحويل)[^\d]*(\d{3,})", message.text)
                if match:
                    amount = int(match.group(1).replace(",", ""))
                    print(f"✅ تم العثور على الإيصال: {receipt_number} بمبلغ {amount}")
                    return amount

        print(f"❌ لم يتم العثور على الإيصال: {receipt_number}")
        return None

    except Exception as e:
        print(f"❌ خطأ أثناء التحقق من الإيصال: {e}")
        return None