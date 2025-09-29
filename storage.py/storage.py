import json

def load_json(path):
    try:
        return json.load(open(path))
    except:
        return {}

def save_json(path, data):
    json.dump(data, open(path, 'w'))

# رصيد المستخدمين
def load_balances():
    return load_json('data/user_balances.json')

def save_balances(balances):
    save_json('data/user_balances.json', balances)

# الإيصالات المستخدمة
def load_used_balances():
    return set(load_json('data/used_balances.json'))

def save_used_balances(used):
    save_json('data/used_balances.json', list(used))

# انتظار إيصال
def mark_waiting_receipt(uid):
    w = load_json('data/waiting_receipts.json')
    w[uid] = True
    save_json('data/waiting_receipts.json', w)

def is_waiting_receipt(uid):
    return load_json('data/waiting_receipts.json').get(uid, False)

def clear_waiting_receipt(uid):
    w = load_json('data/waiting_receipts.json')
    w.pop(uid, None)
    save_json('data/waiting_receipts.json', w)

# انتظار طلب خدمة
def mark_waiting_request(uid, service):
    w = load_json('data/waiting_requests.json')
    w[uid] = service
    save_json('data/waiting_requests.json', w)

def get_waiting_request(uid):
    return load_json('data/waiting_requests.json').get(uid)

def clear_waiting_request(uid):
    w = load_json('data/waiting_requests.json')
    w.pop(uid, None)
    save_json('data/waiting_requests.json', w)

# تجميع الطلبات
def save_pending_submission(uid, text=None, file_id=None):
    data = load_json('data/pending_submissions.json')
    if uid not in data:
        data[uid] = {"texts": [], "files": []}
    if text:
        data[uid]["texts"].append(text)
    if file_id:
        data[uid]["files"].append(file_id)
    save_json('data/pending_submissions.json', data)

def get_pending_submission(uid):
    return load_json('data/pending_submissions.json').get(uid)

def clear_pending_submission(uid):
    data = load_json('data/pending_submissions.json')
    data.pop(uid, None)
    save_json('data/pending_submissions.json', data)

# الخدمة المختارة
def set_pending_service(uid, service):
    data = load_json('data/pending_services.json')
    data[uid] = service
    save_json('data/pending_services.json', data)

def get_pending_service(uid):
    return load_json('data/pending_services.json').get(uid)

def clear_pending_service(uid):
    data = load_json('data/pending_services.json')
    data.pop(uid, None)
    save_json('data/pending_services.json', data)

# عدد الصفحات
def set_pending_pages(uid, pages):
    data = load_json('data/pending_pages.json')
    data[uid] = pages
    save_json('data/pending_pages.json', data)

def get_pending_pages(uid):
    return load_json('data/pending_pages.json').get(uid)

def clear_pending_pages(uid):
    data = load_json('data/pending_pages.json')
    data.pop(uid, None)
    save_json('data/pending_pages.json', data)