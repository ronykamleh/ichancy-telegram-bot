# دليل التثبيت والنشر المفصل 📋

هذا الدليل يوضح خطوات تثبيت ونشر بوت التليجرام العربي على خادم VPS بالتفصيل.

## 📋 المتطلبات الأساسية

### متطلبات النظام
- **نظام التشغيل**: Ubuntu 20.04+ أو CentOS 8+
- **الذاكرة**: 1GB RAM كحد أدنى (2GB مُوصى به)
- **التخزين**: 10GB مساحة فارغة
- **الشبكة**: اتصال إنترنت مستقر

### متطلبات البرمجيات
- Python 3.11 أو أحدث
- pip (مدير حزم Python)
- Git
- SQLite أو MySQL (اختياري)
- Docker (اختياري)

## 🔧 إعداد الخادم

### 1. تحديث النظام
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 2. تثبيت Python 3.11
```bash
# Ubuntu/Debian
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip -y

# CentOS/RHEL
sudo yum install python3.11 python3.11-pip -y
```

### 3. تثبيت Git
```bash
# Ubuntu/Debian
sudo apt install git -y

# CentOS/RHEL
sudo yum install git -y
```

### 4. إنشاء مستخدم للبوت (اختياري ولكن مُوصى به)
```bash
sudo adduser botuser
sudo usermod -aG sudo botuser
su - botuser
```

## 📥 تحميل وإعداد المشروع

### 1. تحميل المشروع
```bash
cd /home/botuser
git clone <repository-url> telegram_bot
cd telegram_bot
```

### 2. إنشاء البيئة الافتراضية
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 3. تثبيت المتطلبات
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## ⚙️ إعداد البوت

### 1. إنشاء البوت في التليجرام

1. ابحث عن `@BotFather` في التليجرام
2. أرسل `/newbot`
3. اتبع التعليمات لإنشاء البوت
4. احفظ الـ Token المُعطى

### 2. إعداد المتغيرات البيئية
```bash
cp .env.example .env
nano .env
```

قم بتعديل الملف وإضافة إعداداتك:
```env
# إعدادات البوت الأساسية
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
BOT_USERNAME=your_bot_username

# قاعدة البيانات
DATABASE_URL=sqlite:///data/bot_database.db

# الإدمن (ضع معرف التليجرام الخاص بك)
ADMIN_IDS=123456789

# إعدادات المدفوعات
MIN_DEPOSIT=5.0
MAX_DEPOSIT=10000.0
MIN_WITHDRAWAL=10.0
MAX_WITHDRAWAL=1000.0
WITHDRAWAL_FEE=0.02

# إعدادات الإحالات
REFERRAL_PERCENTAGE=5.0
MIN_GIFT=5.0

# معلومات الدعم
SUPPORT_PHONE=+1234567890
SUPPORT_EMAIL=support@example.com
SUPPORT_HOURS=24/7

# وضع التطوير
DEBUG=False
```

### 3. إنشاء المجلدات المطلوبة
```bash
mkdir -p data logs
chmod 755 data logs
```

### 4. اختبار البوت
```bash
python test_bot.py
```

## 🚀 تشغيل البوت

### الطريقة الأولى: التشغيل المباشر
```bash
# تشغيل البوت
python bot.py

# أو باستخدام السكريبت
./run.sh
```

### الطريقة الثانية: استخدام systemd (مُوصى به للإنتاج)

1. إنشاء ملف الخدمة:
```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

2. إضافة المحتوى التالي:
```ini
[Unit]
Description=Arabic Telegram Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/telegram_bot
Environment=PATH=/home/botuser/telegram_bot/venv/bin
ExecStart=/home/botuser/telegram_bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. تفعيل وتشغيل الخدمة:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

4. التحقق من حالة الخدمة:
```bash
sudo systemctl status telegram-bot
```

### الطريقة الثالثة: استخدام Docker

1. بناء الصورة:
```bash
docker build -t arabic-telegram-bot .
```

2. تشغيل الحاوية:
```bash
docker run -d \
  --name telegram-bot \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  arabic-telegram-bot
```

3. أو استخدام Docker Compose:
```bash
docker-compose up -d
```

## 🗄️ إعداد قاعدة البيانات MySQL (اختياري)

### 1. تثبيت MySQL
```bash
# Ubuntu/Debian
sudo apt install mysql-server -y

# CentOS/RHEL
sudo yum install mysql-server -y
```

### 2. تأمين MySQL
```bash
sudo mysql_secure_installation
```

### 3. إنشاء قاعدة البيانات والمستخدم
```sql
mysql -u root -p

CREATE DATABASE telegram_bot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'botuser'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON telegram_bot.* TO 'botuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. تحديث إعدادات قاعدة البيانات
```env
DATABASE_URL=mysql+pymysql://botuser:strong_password@localhost/telegram_bot
```

### 5. تثبيت مكتبة MySQL
```bash
pip install pymysql
```

## 🔒 إعدادات الأمان

### 1. إعداد Firewall
```bash
# Ubuntu/Debian
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 2. إعداد SSL (اختياري)
```bash
# تثبيت Certbot
sudo apt install certbot -y

# الحصول على شهادة SSL
sudo certbot certonly --standalone -d yourdomain.com
```

### 3. تأمين ملفات الإعدادات
```bash
chmod 600 .env
chown botuser:botuser .env
```

## 📊 المراقبة والصيانة

### 1. مراقبة السجلات
```bash
# سجلات البوت
tail -f logs/bot.log

# سجلات النظام (systemd)
sudo journalctl -u telegram-bot -f

# سجلات Docker
docker logs -f telegram-bot
```

### 2. النسخ الاحتياطي
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/botuser/backups"

mkdir -p $BACKUP_DIR

# نسخ احتياطي لقاعدة البيانات
cp data/bot_database.db $BACKUP_DIR/bot_database_$DATE.db

# نسخ احتياطي للسجلات
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz logs/

# حذف النسخ القديمة (أكثر من 30 يوم)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### 3. تحديث البوت
```bash
# إيقاف البوت
sudo systemctl stop telegram-bot

# تحديث الكود
git pull origin main

# تحديث المتطلبات
source venv/bin/activate
pip install -r requirements.txt

# إعادة تشغيل البوت
sudo systemctl start telegram-bot
```

## 🔧 استكشاف الأخطاء وإصلاحها

### مشاكل شائعة وحلولها

#### 1. البوت لا يستجيب
```bash
# التحقق من حالة الخدمة
sudo systemctl status telegram-bot

# مراجعة السجلات
sudo journalctl -u telegram-bot --no-pager

# إعادة تشغيل البوت
sudo systemctl restart telegram-bot
```

#### 2. خطأ في قاعدة البيانات
```bash
# التحقق من صلاحيات الملفات
ls -la data/

# إعادة إنشاء قاعدة البيانات
rm data/bot_database.db
python -c "from database import DatabaseManager; db = DatabaseManager(); db.create_tables()"
```

#### 3. مشاكل الذاكرة
```bash
# مراقبة استخدام الذاكرة
htop

# إعادة تشغيل البوت
sudo systemctl restart telegram-bot
```

#### 4. مشاكل الشبكة
```bash
# التحقق من الاتصال
ping api.telegram.org

# التحقق من البروكسي (إذا كان مستخدماً)
curl -I https://api.telegram.org
```

## 📈 تحسين الأداء

### 1. إعدادات قاعدة البيانات
```sql
-- لـ MySQL
SET GLOBAL innodb_buffer_pool_size = 128M;
SET GLOBAL max_connections = 100;
```

### 2. إعدادات النظام
```bash
# زيادة حدود الملفات المفتوحة
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf
```

### 3. مراقبة الأداء
```bash
# تثبيت أدوات المراقبة
sudo apt install htop iotop nethogs -y

# مراقبة استخدام الموارد
htop
iotop
nethogs
```

## 🔄 التحديثات التلقائية

### إعداد التحديثات التلقائية للنظام
```bash
# Ubuntu/Debian
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure unattended-upgrades

# CentOS/RHEL
sudo yum install yum-cron -y
sudo systemctl enable yum-cron
sudo systemctl start yum-cron
```

## 📞 الدعم الفني

في حالة مواجهة مشاكل:

1. راجع السجلات أولاً
2. تأكد من صحة الإعدادات
3. تحقق من اتصال الإنترنت
4. راجع وثائق المشروع
5. اتصل بالدعم الفني

---

**تم إعداد هذا الدليل لضمان نشر ناجح وآمن للبوت** 🚀

