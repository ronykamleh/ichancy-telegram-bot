#!/bin/bash

# ملف تشغيل بوت ichancy.com
# بوت تليجرام احترافي لإدارة الأرصدة والمعاملات المالية

echo "🎰 بدء تشغيل بوت ichancy.com..."

# التحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 غير مثبت"
    exit 1
fi

# التحقق من وجود pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 غير مثبت"
    exit 1
fi

# إنشاء المجلدات المطلوبة
echo "📁 إنشاء المجلدات..."
mkdir -p data logs backups temp

# التحقق من وجود ملف المتطلبات
if [ ! -f "requirements.txt" ]; then
    echo "❌ ملف requirements.txt غير موجود"
    exit 1
fi

# تثبيت المتطلبات
echo "📦 تثبيت المتطلبات..."
pip3 install -r requirements.txt

# التحقق من وجود ملف .env
if [ ! -f ".env" ]; then
    echo "⚠️ ملف .env غير موجود"
    echo "📋 يرجى تشغيل: python3 setup.py"
    echo "أو إنشاء ملف .env يدوياً من .env.example"
    exit 1
fi

# تحميل متغيرات البيئة
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# التحقق من توكن البوت
if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "YOUR_BOT_TOKEN_HERE" ]; then
    echo "❌ يرجى تعيين BOT_TOKEN في ملف .env"
    exit 1
fi

# إعداد قاعدة البيانات إذا لم تكن موجودة
if [ ! -f "data/telegram_bot.db" ]; then
    echo "🗄️ إعداد قاعدة البيانات..."
    python3 -c "
from database import DatabaseManager
db = DatabaseManager()
db.create_tables()
print('✅ تم إنشاء قاعدة البيانات')
"
fi

# تشغيل البوت
echo "🚀 تشغيل البوت..."
echo "📋 للإيقاف: اضغط Ctrl+C"
echo "📊 لمراقبة اللوجز: tail -f logs/bot.log"
echo ""

# تشغيل البوت مع إعادة التشغيل التلقائي
while true; do
    python3 main.py
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo "✅ تم إيقاف البوت بنجاح"
        break
    else
        echo "❌ البوت توقف بخطأ (كود: $exit_code)"
        echo "🔄 إعادة التشغيل خلال 5 ثوانٍ..."
        sleep 5
    fi
done

