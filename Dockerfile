# استخدام Python 3.11 كصورة أساسية
FROM python:3.11-slim

# تعيين متغير البيئة لمنع إنشاء ملفات .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# تعيين مجلد العمل
WORKDIR /app

# تثبيت متطلبات النظام
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات وتثبيت المكتبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملفات المشروع
COPY . .

# إنشاء مجلد قاعدة البيانات
RUN mkdir -p /app/data

# تعيين الصلاحيات
RUN chmod +x bot.py

# تعريف المنفذ (اختياري للمراقبة)
EXPOSE 8000

# تشغيل البوت
CMD ["python", "bot.py"]

