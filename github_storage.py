import requests, base64, json

# إعدادات GitHub
GITHUB_TOKEN = "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"
REPO = "khadorsomar5-star/kernal-json"
BRANCH = "main"

# قراءة محتوى ملف من الريبو
def read_github_file(path):
    url = f"https://api.github.com/repos/{REPO}/contents/{path}?ref={BRANCH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()["content"]
        decoded = base64.b64decode(content).decode("utf-8")
        return decoded
    else:
        print("❌ Error reading file:", response.text)
        return None

# تعديل ورفع ملف إلى الريبو
def update_github_file(path, new_content, commit_message):
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # جلب SHA الحالي
    get_resp = requests.get(url, headers=headers)
    if get_resp.status_code != 200:
        print("❌ Error getting SHA:", get_resp.text)
        return

    sha = get_resp.json()["sha"]
    encoded_content = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")

    payload = {
        "message": commit_message,
        "content": encoded_content,
        "sha": sha,
        "branch": BRANCH
    }

    put_resp = requests.put(url, headers=headers, json=payload)
    if put_resp.status_code in [200, 201]:
        print("✅ File updated successfully")
    else:
        print("❌ Error updating file:", put_resp.text)
