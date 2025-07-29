#!/usr/bin/env python3
"""
البوت الرئيسي - ichancy.com
بوت تليجرام احترافي لإدارة الأرصدة والمعاملات المالية
"""

import logging
import os
import asyncio
from datetime import time
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram.ext import JobQueue

# استيراد الوحدات المحلية
from config import Config
from database import DatabaseManager
from handlers import BotHandlers
from gaming_handler import GamingHandler

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOGGING_CONFIG['level']),
    handlers=[
        logging.FileHandler(Config.LOGGING_CONFIG['file_path']),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TelegramBot:
    """فئة البوت الرئيسية"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.handlers = BotHandlers()
        self.gaming_handler = GamingHandler()
        
    async def setup_database(self):
        """إعداد قاعدة البيانات"""
        try:
            # إنشاء مجلد البيانات إذا لم يكن موجوداً
            os.makedirs('data', exist_ok=True)
            
            # إنشاء الجداول
            self.db.create_tables()
            logger.info("تم إعداد قاعدة البيانات بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في إعداد قاعدة البيانات: {str(e)}")
            raise
    
    def setup_handlers(self, application):
        """إعداد معالجات الأوامر"""
        try:
            # أوامر البداية
            application.add_handler(CommandHandler("start", self.handlers.start_command))
            application.add_handler(CommandHandler("help", self.handlers.help_command))
            application.add_handler(CommandHandler("menu", self.handlers.main_menu))
            
            # أوامر الإدمن
            application.add_handler(CommandHandler("admin", self.handlers.admin_panel))
            application.add_handler(CommandHandler("stats", self.handlers.admin_stats))
            application.add_handler(CommandHandler("broadcast", self.handlers.admin_broadcast))
            
            # معالجات الأزرار
            application.add_handler(CallbackQueryHandler(self.handlers.button_handler))
            
            # معالجات الرسائل النصية
            application.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                self.handlers.text_message_handler
            ))
            
            # معالج الأخطاء
            application.add_error_handler(self.error_handler)
            
            logger.info("تم إعداد معالجات الأوامر بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في إعداد المعالجات: {str(e)}")
            raise
    
    def setup_jobs(self, application):
        """إعداد المهام المجدولة"""
        try:
            job_queue = application.job_queue
            
            # سحب الجاكبوت اليومي
            jackpot_time = time.fromisoformat(Config.JACKPOT_DRAW_TIME)
            job_queue.run_daily(
                self.gaming_handler.daily_jackpot_draw,
                time=jackpot_time,
                name="daily_jackpot_draw"
            )
            
            # تنظيف البيانات القديمة (أسبوعياً)
            job_queue.run_repeating(
                self.cleanup_old_data,
                interval=604800,  # أسبوع بالثواني
                name="weekly_cleanup"
            )
            
            # نسخ احتياطي يومي
            job_queue.run_daily(
                self.daily_backup,
                time=time(hour=2, minute=0),  # 2:00 صباحاً
                name="daily_backup"
            )
            
            logger.info("تم إعداد المهام المجدولة بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في إعداد المهام المجدولة: {str(e)}")
    
    async def error_handler(self, update, context):
        """معالج الأخطاء العام"""
        logger.error(f"خطأ في التحديث {update}: {context.error}")
        
        # تسجيل الخطأ في قاعدة البيانات
        if update and update.effective_user:
            self.db.log_system_event(
                log_type="error",
                module="telegram_bot",
                message=str(context.error),
                user_id=update.effective_user.id
            )
    
    async def cleanup_old_data(self, context):
        """تنظيف البيانات القديمة"""
        try:
            # تنظيف السجلات القديمة (أكثر من 3 أشهر)
            from datetime import datetime, timedelta
            from database import SystemLog, Transaction
            
            session = self.db.get_session()
            try:
                cutoff_date = datetime.utcnow() - timedelta(days=90)
                
                # حذف السجلات القديمة
                old_logs = session.query(SystemLog).filter(
                    SystemLog.created_at < cutoff_date
                ).delete()
                
                # حذف المعاملات المكتملة القديمة (الاحتفاظ بالمعلقة)
                old_transactions = session.query(Transaction).filter(
                    Transaction.created_at < cutoff_date,
                    Transaction.status.in_(['completed', 'failed', 'cancelled'])
                ).delete()
                
                session.commit()
                
                logger.info(f"تم تنظيف {old_logs} سجل و {old_transactions} معاملة قديمة")
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"خطأ في تنظيف البيانات: {str(e)}")
    
    async def daily_backup(self, context):
        """نسخ احتياطي يومي"""
        try:
            import shutil
            from datetime import datetime
            
            # إنشاء مجلد النسخ الاحتياطية
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)
            
            # اسم ملف النسخة الاحتياطية
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{backup_dir}/backup_{timestamp}.db"
            
            # نسخ قاعدة البيانات
            if os.path.exists("data/telegram_bot.db"):
                shutil.copy2("data/telegram_bot.db", backup_file)
                logger.info(f"تم إنشاء نسخة احتياطية: {backup_file}")
                
                # حذف النسخ القديمة (الاحتفاظ بآخر 7 نسخ)
                backup_files = sorted([f for f in os.listdir(backup_dir) if f.startswith("backup_")])
                if len(backup_files) > 7:
                    for old_backup in backup_files[:-7]:
                        os.remove(os.path.join(backup_dir, old_backup))
                        logger.info(f"تم حذف النسخة الاحتياطية القديمة: {old_backup}")
            
        except Exception as e:
            logger.error(f"خطأ في النسخ الاحتياطي: {str(e)}")
    
    async def run(self):
        """تشغيل البوت"""
        try:
            # التحقق من وجود التوكن
            if not Config.BOT_TOKEN or Config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
                logger.error("يرجى تعيين BOT_TOKEN في متغيرات البيئة")
                return
            
            # إعداد قاعدة البيانات
            await self.setup_database()
            
            # إنشاء التطبيق
            application = Application.builder().token(Config.BOT_TOKEN).build()
            
            # إعداد المعالجات والمهام
            self.setup_handlers(application)
            self.setup_jobs(application)
            
            logger.info("بدء تشغيل البوت...")
            
            # تشغيل البوت
            await application.run_polling(
                allowed_updates=["message", "callback_query"],
                drop_pending_updates=True
            )
            
        except Exception as e:
            logger.error(f"خطأ في تشغيل البوت: {str(e)}")
            raise

def main():
    """الدالة الرئيسية"""
    try:
        # إنشاء مجلدات اللوجز
        os.makedirs(os.path.dirname(Config.LOGGING_CONFIG['file_path']), exist_ok=True)
        
        # إنشاء وتشغيل البوت
        bot = TelegramBot()
        asyncio.run(bot.run())
        
    except KeyboardInterrupt:
        logger.info("تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        logger.error(f"خطأ في تشغيل البوت: {str(e)}")
        raise

if __name__ == "__main__":
    main()

