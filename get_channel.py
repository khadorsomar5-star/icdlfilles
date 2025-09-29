import subprocess

required_packages = {
    "python-telegram-bot": ">=22.0",
    "telethon": ">=1.33",
    "python-dotenv": "",
    "aiofiles": "",
    "rich": "",
    "schedule": "",
    "requests": ""
}

print("🚀 جاري تثبيت المكتبات المطلوبة...\n")

for package, version in required_packages.items():
    full_package = f"{package}{version}"
    print(f"📦 تثبيت: {full_package}")
    result = subprocess.run(["pip", "install", full_package], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ تم تثبيت {package} بنجاح.\n")
    else:
        print(f"❌ فشل في تثبيت {package}.\n🔍 الخطأ:\n{result.stderr}\n")

print("🎯 عملية التثبيت انتهت.")