import subprocess

required_packages = [
    "python-telegram-bot>=22.0",
    "telethon>=1.33",
    "python-dotenv",
    "aiofiles",
    "rich",
    "schedule",
    "requests"
]

print("🚀 جاري تثبيت المكتبات المطلوبة...\n")

for package in required_packages:
    print(f"📦 تثبيت: {package}")
    result = subprocess.run(["pip", "install", package], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ تم تثبيت {package} بنجاح.\n")
    else:
        print(f"❌ فشل في تثبيت {package}.\n🔍 الخطأ:\n{result.stderr}\n")

print("🎯 عملية التثبيت انتهت.")