#!/usr/bin/env python3
"""
ملف الإعداد السريع للبوت - ichancy.com
"""

import os
import sys
import subprocess
import sqlite3
from datetime import datetime

def print_banner():
    """طباعة شعار البوت"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🎰 بوت تليجرام ichancy.com - الإعداد السريع 🎰           ║
║                                                              ║
║    بوت احترافي لإدارة الأرصدة والمعاملات المالية            ║
║    مع دعم الكازينو والرهانات الرياضية                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """التحقق من إصدار Python"""
    if sys.version_info < (3, 8):
        print("❌ يتطلب Python 3.8 أو أحدث")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} - متوافق")

def install_requirements():
    """تثبيت المتطلبات"""
    print("\n📦 تثبيت المتطلبات...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ تم تثبيت جميع المتطلبات بنجاح")
    except subprocess.CalledProcessError:
        print("❌ فشل في تثبيت المتطلبات")
        sys.exit(1)

def create_directories():
    """إنشاء المجلدات المطلوبة"""
    print("\n📁 إنشاء المجلدات...")
    directories = ['data', 'logs', 'backups', 'temp']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ تم إنشاء مجلد: {directory}")

def setup_environment():
    """إعداد متغيرات البيئة"""
    print("\n⚙️ إعداد متغيرات البيئة...")
    
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ ملف {env_file} موجود بالفعل")
        return
    
    # قراءة المعلومات من المستخدم
    print("\nيرجى إدخال المعلومات التالية:")
    
    bot_token = input("🤖 توكن البوت (من @BotFather): ").strip()
    if not bot_token:
        print("❌ توكن البوت مطلوب")
        sys.exit(1)
    
    admin_ids = input("👑 معرفات الإدمن (مفصولة بفواصل): ").strip()
    
    # إعدادات اختيارية
    print("\n📋 إعدادات اختيارية (اضغط Enter للتخطي):")
    
    min_deposit = input("💰 الحد الأدنى للإيداع (افتراضي: 10): ").strip() or "10"
    max_deposit = input("💰 الحد الأقصى للإيداع (افتراضي: 10000): ").strip() or "10000"
    min_withdrawal = input("💸 الحد الأدنى للسحب (افتراضي: 20): ").strip() or "20"
    max_withdrawal = input("💸 الحد الأقصى للسحب (افتراضي: 5000): ").strip() or "5000"
    
    referral_percentage = input("👥 نسبة ربح الإحالات % (افتراضي: 10): ").strip() or "10"
    
    # إعدادات ichancy
    print("\n🎰 إعدادات ichancy.com:")
    ichancy_api_key = input("🔑 مفتاح API (اختياري): ").strip()
    ichancy_partner_id = input("🤝 معرف الشريك (اختياري): ").strip()
    
    # كتابة ملف .env
    env_content = f"""# إعدادات البوت - ichancy.com
# تم الإنشاء في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# إعدادات التليجرام
BOT_TOKEN={bot_token}
ADMIN_IDS={admin_ids}

# إعدادات قاعدة البيانات
DATABASE_URL=sqlite:///data/telegram_bot.db

# حدود المعاملات
MIN_DEPOSIT={min_deposit}
MAX_DEPOSIT={max_deposit}
MIN_WITHDRAWAL={min_withdrawal}
MAX_WITHDRAWAL={max_withdrawal}
MIN_GIFT=5

# إعدادات الإحالات
REFERRAL_PERCENTAGE={referral_percentage}

# إعدادات الجاكبوت
MIN_JACKPOT=1000
JACKPOT_CONTRIBUTION_RATE=0.01
JACKPOT_DRAW_TIME=23:59

# إعدادات ichancy.com
ICHANCY_API_KEY={ichancy_api_key}
ICHANCY_PARTNER_ID={ichancy_partner_id}
ICHANCY_WEBHOOK_SECRET=

# إعدادات الدعم
SUPPORT_PHONE=+963912345678
SUPPORT_EMAIL=support@ichancy.com
SUPPORT_TELEGRAM=@ichancy_support

# إعدادات الأمان
MAX_DAILY_WITHDRAWALS=3
MAX_DAILY_DEPOSITS=10
WITHDRAWAL_COOLDOWN=3600
REQUIRE_ADMIN_APPROVAL=true
AUTO_BAN_THRESHOLD=10

# إعدادات التسجيل
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/bot.log
LOG_MAX_FILE_SIZE=10485760
LOG_BACKUP_COUNT=5
"""
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"✅ تم إنشاء ملف {env_file}")

def setup_database():
    """إعداد قاعدة البيانات"""
    print("\n🗄️ إعداد قاعدة البيانات...")
    
    try:
        from database import DatabaseManager
        
        db = DatabaseManager()
        db.create_tables()
        
        print("✅ تم إنشاء قاعدة البيانات والجداول بنجاح")
        
        # إنشاء مستخدم إدمن تجريبي
        session = db.get_session()
        try:
            from database import User
            
            # التحقق من وجود مستخدم إدمن
            admin_exists = session.query(User).filter(User.is_admin == True).first()
            
            if not admin_exists:
                print("\n👑 إنشاء حساب إدمن تجريبي...")
                admin_user = User(
                    telegram_id="123456789",  # معرف تجريبي
                    username="admin",
                    first_name="Admin",
                    last_name="User",
                    balance=10000.0,
                    is_admin=True,
                    referral_code="ADMIN001"
                )
                session.add(admin_user)
                session.commit()
                print("✅ تم إنشاء حساب إدمن تجريبي (ID: 123456789)")
        
        finally:
            session.close()
            
    except Exception as e:
        print(f"❌ خطأ في إعداد قاعدة البيانات: {str(e)}")
        sys.exit(1)

def create_systemd_service():
    """إنشاء خدمة systemd"""
    print("\n🔧 إنشاء خدمة systemd...")
    
    current_dir = os.getcwd()
    python_path = sys.executable
    
    service_content = f"""[Unit]
Description=Ichancy Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory={current_dir}
Environment=PATH={os.path.dirname(python_path)}
ExecStart={python_path} main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = "ichancy-bot.service"
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    print(f"✅ تم إنشاء ملف الخدمة: {service_file}")
    print(f"📋 لتثبيت الخدمة، قم بتشغيل:")
    print(f"   sudo cp {service_file} /etc/systemd/system/")
    print(f"   sudo systemctl enable ichancy-bot")
    print(f"   sudo systemctl start ichancy-bot")

def print_completion_message():
    """طباعة رسالة الإكمال"""
    message = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🎉 تم إعداد البوت بنجاح! 🎉                              ║
║                                                              ║
║    📋 الخطوات التالية:                                       ║
║                                                              ║
║    1️⃣ تشغيل البوت:                                          ║
║       python3 main.py                                        ║
║                                                              ║
║    2️⃣ أو تشغيل البوت في الخلفية:                            ║
║       nohup python3 main.py &                                ║
║                                                              ║
║    3️⃣ للتحقق من حالة البوت:                                 ║
║       tail -f logs/bot.log                                   ║
║                                                              ║
║    🔗 موقع ichancy.com: https://www.ichancy.com/            ║
║                                                              ║
║    📧 للدعم: support@ichancy.com                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(message)

def main():
    """الدالة الرئيسية للإعداد"""
    try:
        print_banner()
        
        print("🚀 بدء عملية الإعداد...")
        
        # التحقق من إصدار Python
        check_python_version()
        
        # إنشاء المجلدات
        create_directories()
        
        # تثبيت المتطلبات
        install_requirements()
        
        # إعداد متغيرات البيئة
        setup_environment()
        
        # إعداد قاعدة البيانات
        setup_database()
        
        # إنشاء خدمة systemd
        create_systemd_service()
        
        # رسالة الإكمال
        print_completion_message()
        
    except KeyboardInterrupt:
        print("\n❌ تم إلغاء الإعداد بواسطة المستخدم")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ خطأ في الإعداد: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

