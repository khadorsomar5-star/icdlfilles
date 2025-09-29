import requests

SECOND_BOT_TOKEN = "5368736703:AAHCsZU5PSSNAuZOvAom9Dx7tQ2ug55guog"  # ← ضع توكن البوت الثاني هنا

def send_text_to_user(chat_id, message):
    url = f"https://api.telegram.org/bot{SECOND_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message
    }
    return requests.post(url, data=data).json()

def send_file_to_user(chat_id, file_id, caption=None):
    url = f"https://api.telegram.org/bot{SECOND_BOT_TOKEN}/sendDocument"
    data = {
        "chat_id": chat_id,
        "document": file_id,
        "caption": caption or "📤 ملف جاهز من البوت الثاني"
    }
    return requests.post(url, data=data).json()