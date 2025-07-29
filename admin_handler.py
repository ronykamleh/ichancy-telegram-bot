"""
معالج صلاحيات الإدمن
"""

import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from database import DatabaseManager, User, Transaction, GiftCode
from config import Config
from keyboards import Keyboards
from utils import format_currency, get_user_display_name

logger = logging.getLogger(__name__)
db = DatabaseManager()

class AdminHandler:
    """فئة معالج صلاحيات الإدمن"""
    
    @staticmethod
    async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """لوحة تحكم الإدمن الرئيسية"""
        user_id = update.effective_user.id
        
        if user_id not in Config.ADMIN_IDS:
            await update.message.reply_text("❌ ليس لديك صلاحية للوصول إلى لوحة الإدمن")
            return
        
        # إحصائيات عامة
        session = db.get_session()
        try:
            total_users = session.query(User).count()
            total_balance = session.query(User).with_entities(db.func.sum(User.balance)).scalar() or 0
            today_transactions = session.query(Transaction).filter(
                Transaction.created_at >= datetime.now().date()
            ).count()
            
            message = f"""
🔧 لوحة تحكم الإدمن

📊 إحصائيات عامة:
👥 إجمالي المستخدمين: {total_users}
💰 إجمالي الأرصدة: {format_currency(total_balance)}
📈 معاملات اليوم: {today_transactions}

اختر العملية المطلوبة:
            """
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    message,
                    reply_markup=Keyboards.admin_panel()
                )
            else:
                await update.message.reply_text(
                    message,
                    reply_markup=Keyboards.admin_panel()
                )
        finally:
            session.close()
    
    @staticmethod
    async def user_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إدارة المستخدمين"""
        message = """
👥 إدارة المستخدمين

اختر العملية المطلوبة:
        """
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=Keyboards.user_management_menu()
        )
    
    @staticmethod
    async def add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إضافة رصيد لمستخدم"""
        message = """
💰 إضافة رصيد

أرسل معرف المستخدم والمبلغ بالتنسيق التالي:
معرف_المستخدم المبلغ

مثال: 123456789 100
        """
        
        context.user_data['admin_operation'] = 'add_balance'
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=Keyboards.cancel_admin_operation()
        )
    
    @staticmethod
    async def deduct_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """خصم رصيد من مستخدم"""
        message = """
💸 خصم رصيد

أرسل معرف المستخدم والمبلغ بالتنسيق التالي:
معرف_المستخدم المبلغ

مثال: 123456789 50
        """
        
        context.user_data['admin_operation'] = 'deduct_balance'
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=Keyboards.cancel_admin_operation()
        )
    
    @staticmethod
    async def user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض معلومات مستخدم"""
        message = """
ℹ️ معلومات المستخدم

أرسل معرف المستخدم أو اسم المستخدم:
        """
        
        context.user_data['admin_operation'] = 'user_info'
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=Keyboards.cancel_admin_operation()
        )
    
    @staticmethod
    async def create_gift_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إنشاء كود هدية"""
        message = """
🎁 إنشاء كود هدية

أرسل تفاصيل الكود بالتنسيق التالي:
الكود المبلغ عدد_الاستخدامات

مثال: WELCOME2024 50 100
        """
        
        context.user_data['admin_operation'] = 'create_gift_code'
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=Keyboards.cancel_admin_operation()
        )
    
    @staticmethod
    async def view_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الإحصائيات التفصيلية"""
        session = db.get_session()
        try:
            # إحصائيات المستخدمين
            total_users = session.query(User).count()
            active_users_today = session.query(User).filter(
                User.last_activity >= datetime.now().date()
            ).count()
            
            # إحصائيات المعاملات
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            today_deposits = session.query(Transaction).filter(
                Transaction.transaction_type == 'deposit',
                Transaction.created_at >= today
            ).count()
            
            today_withdrawals = session.query(Transaction).filter(
                Transaction.transaction_type == 'withdraw',
                Transaction.created_at >= today
            ).count()
            
            week_transactions = session.query(Transaction).filter(
                Transaction.created_at >= week_ago
            ).count()
            
            month_transactions = session.query(Transaction).filter(
                Transaction.created_at >= month_ago
            ).count()
            
            # إحصائيات الأرصدة
            total_balance = session.query(User).with_entities(db.func.sum(User.balance)).scalar() or 0
            avg_balance = session.query(User).with_entities(db.func.avg(User.balance)).scalar() or 0
            
            message = f"""
📊 إحصائيات تفصيلية

👥 المستخدمون:
• إجمالي المستخدمين: {total_users}
• نشطون اليوم: {active_users_today}

💰 المعاملات:
• إيداعات اليوم: {today_deposits}
• سحوبات اليوم: {today_withdrawals}
• معاملات الأسبوع: {week_transactions}
• معاملات الشهر: {month_transactions}

💵 الأرصدة:
• إجمالي الأرصدة: {format_currency(total_balance)}
• متوسط الرصيد: {format_currency(avg_balance)}
            """
            
            await update.callback_query.edit_message_text(
                message,
                reply_markup=Keyboards.admin_back_menu()
            )
        finally:
            session.close()
    
    @staticmethod
    async def pending_transactions(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض المعاملات المعلقة"""
        session = db.get_session()
        try:
            pending = session.query(Transaction).filter(
                Transaction.status == 'pending'
            ).order_by(Transaction.created_at.desc()).limit(10).all()
            
            if not pending:
                message = "✅ لا توجد معاملات معلقة حالياً"
            else:
                message = "⏳ المعاملات المعلقة:\n\n"
                for i, transaction in enumerate(pending, 1):
                    user = session.query(User).filter(User.id == transaction.user_id).first()
                    message += f"{i}. {transaction.transaction_type.upper()}\n"
                    message += f"👤 {get_user_display_name(user)}\n"
                    message += f"💰 {format_currency(transaction.amount)}\n"
                    message += f"📅 {transaction.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                    message += f"🆔 ID: {transaction.id}\n\n"
            
            await update.callback_query.edit_message_text(
                message,
                reply_markup=Keyboards.pending_transactions_menu()
            )
        finally:
            session.close()
    
    @staticmethod
    async def approve_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """الموافقة على معاملة"""
        message = """
✅ الموافقة على معاملة

أرسل رقم المعاملة للموافقة عليها:
        """
        
        context.user_data['admin_operation'] = 'approve_transaction'
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=Keyboards.cancel_admin_operation()
        )
    
    @staticmethod
    async def reject_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """رفض معاملة"""
        message = """
❌ رفض معاملة

أرسل رقم المعاملة لرفضها:
        """
        
        context.user_data['admin_operation'] = 'reject_transaction'
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=Keyboards.cancel_admin_operation()
        )
    
    @staticmethod
    async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إرسال رسالة جماعية"""
        message = """
📢 إرسال رسالة جماعية

أرسل الرسالة التي تريد إرسالها لجميع المستخدمين:
        """
        
        context.user_data['admin_operation'] = 'broadcast'
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=Keyboards.cancel_admin_operation()
        )
    
    @staticmethod
    async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة مدخلات الإدمن"""
        operation = context.user_data.get('admin_operation')
        text = update.message.text.strip()
        
        if operation == 'add_balance':
            await AdminHandler._handle_balance_operation(update, context, text, 'add')
        elif operation == 'deduct_balance':
            await AdminHandler._handle_balance_operation(update, context, text, 'deduct')
        elif operation == 'user_info':
            await AdminHandler._handle_user_info(update, context, text)
        elif operation == 'create_gift_code':
            await AdminHandler._handle_create_gift_code(update, context, text)
        elif operation == 'approve_transaction':
            await AdminHandler._handle_transaction_action(update, context, text, 'approve')
        elif operation == 'reject_transaction':
            await AdminHandler._handle_transaction_action(update, context, text, 'reject')
        elif operation == 'broadcast':
            await AdminHandler._handle_broadcast(update, context, text)
        
        # مسح العملية
        context.user_data.pop('admin_operation', None)
    
    @staticmethod
    async def _handle_balance_operation(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, operation: str):
        """معالجة عمليات الرصيد"""
        try:
            parts = text.split()
            if len(parts) != 2:
                await update.message.reply_text(
                    "❌ تنسيق خاطئ. استخدم: معرف_المستخدم المبلغ",
                    reply_markup=Keyboards.admin_panel()
                )
                return
            
            user_id = int(parts[0])
            amount = float(parts[1])
            
            session = db.get_session()
            try:
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    await update.message.reply_text(
                        "❌ المستخدم غير موجود",
                        reply_markup=Keyboards.admin_panel()
                    )
                    return
                
                if operation == 'add':
                    user.balance += amount
                    action = "إضافة"
                    emoji = "➕"
                else:
                    if user.balance < amount:
                        await update.message.reply_text(
                            f"❌ رصيد المستخدم غير كافي\n💵 الرصيد الحالي: {format_currency(user.balance)}",
                            reply_markup=Keyboards.admin_panel()
                        )
                        return
                    user.balance -= amount
                    action = "خصم"
                    emoji = "➖"
                
                # إضافة سجل المعاملة
                transaction = Transaction(
                    user_id=user.id,
                    transaction_type='admin_adjustment',
                    amount=amount if operation == 'add' else -amount,
                    status='completed',
                    description=f"{action} رصيد من الإدمن"
                )
                session.add(transaction)
                session.commit()
                
                # إشعار المستخدم
                try:
                    await context.bot.send_message(
                        chat_id=user.telegram_id,
                        text=f"{emoji} تم {action} {format_currency(amount)} إلى رصيدك\n💵 رصيدك الحالي: {format_currency(user.balance)}"
                    )
                except TelegramError:
                    logger.warning(f"لا يمكن إرسال إشعار للمستخدم {user.telegram_id}")
                
                await update.message.reply_text(
                    f"✅ تم {action} {format_currency(amount)} بنجاح\n👤 المستخدم: {get_user_display_name(user)}\n💵 الرصيد الجديد: {format_currency(user.balance)}",
                    reply_markup=Keyboards.admin_panel()
                )
            finally:
                session.close()
                
        except (ValueError, IndexError):
            await update.message.reply_text(
                "❌ تنسيق خاطئ. استخدم: معرف_المستخدم المبلغ",
                reply_markup=Keyboards.admin_panel()
            )
    
    @staticmethod
    async def _handle_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """معالجة عرض معلومات المستخدم"""
        session = db.get_session()
        try:
            user = None
            
            # البحث بمعرف التليجرام
            if text.isdigit():
                user = session.query(User).filter(User.telegram_id == int(text)).first()
            
            # البحث باسم المستخدم
            if not user:
                username = text.replace('@', '')
                user = session.query(User).filter(User.username == username).first()
            
            if not user:
                await update.message.reply_text(
                    "❌ المستخدم غير موجود",
                    reply_markup=Keyboards.admin_panel()
                )
                return
            
            # إحصائيات المستخدم
            total_deposits = session.query(Transaction).filter(
                Transaction.user_id == user.id,
                Transaction.transaction_type == 'deposit',
                Transaction.status == 'completed'
            ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
            
            total_withdrawals = session.query(Transaction).filter(
                Transaction.user_id == user.id,
                Transaction.transaction_type == 'withdraw',
                Transaction.status == 'completed'
            ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
            
            transaction_count = session.query(Transaction).filter(
                Transaction.user_id == user.id
            ).count()
            
            message = f"""
👤 معلومات المستخدم

🆔 معرف التليجرام: {user.telegram_id}
👤 الاسم: {get_user_display_name(user)}
📱 اسم المستخدم: @{user.username or 'غير محدد'}
📅 تاريخ التسجيل: {user.created_at.strftime('%Y-%m-%d')}
📅 آخر نشاط: {user.last_activity.strftime('%Y-%m-%d %H:%M') if user.last_activity else 'غير محدد'}

💰 الأرصدة:
💵 الرصيد الحالي: {format_currency(user.balance)}
📈 إجمالي الإيداعات: {format_currency(total_deposits)}
📉 إجمالي السحوبات: {format_currency(total_withdrawals)}

👥 الإحالات:
🔗 كود الإحالة: {user.referral_code}
👥 عدد الإحالات: {user.referral_count}
💰 أرباح الإحالات: {format_currency(user.referral_earnings)}
👤 أحاله: {user.referred_by or 'لا يوجد'}

📊 الإحصائيات:
📈 عدد المعاملات: {transaction_count}
            """
            
            await update.message.reply_text(
                message,
                reply_markup=Keyboards.admin_panel()
            )
        finally:
            session.close()
    
    @staticmethod
    async def _handle_create_gift_code(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """معالجة إنشاء كود هدية"""
        try:
            parts = text.split()
            if len(parts) != 3:
                await update.message.reply_text(
                    "❌ تنسيق خاطئ. استخدم: الكود المبلغ عدد_الاستخدامات",
                    reply_markup=Keyboards.admin_panel()
                )
                return
            
            code = parts[0].upper()
            amount = float(parts[1])
            max_uses = int(parts[2])
            
            session = db.get_session()
            try:
                # التحقق من عدم وجود الكود
                existing = session.query(GiftCode).filter(GiftCode.code == code).first()
                if existing:
                    await update.message.reply_text(
                        "❌ هذا الكود موجود بالفعل",
                        reply_markup=Keyboards.admin_panel()
                    )
                    return
                
                # إنشاء الكود
                gift_code = GiftCode(
                    code=code,
                    amount=amount,
                    max_uses=max_uses,
                    current_uses=0,
                    is_active=True,
                    created_by=update.effective_user.id
                )
                session.add(gift_code)
                session.commit()
                
                await update.message.reply_text(
                    f"✅ تم إنشاء كود الهدية بنجاح\n🎁 الكود: {code}\n💰 المبلغ: {format_currency(amount)}\n🔢 عدد الاستخدامات: {max_uses}",
                    reply_markup=Keyboards.admin_panel()
                )
            finally:
                session.close()
                
        except (ValueError, IndexError):
            await update.message.reply_text(
                "❌ تنسيق خاطئ. استخدم: الكود المبلغ عدد_الاستخدامات",
                reply_markup=Keyboards.admin_panel()
            )
    
    @staticmethod
    async def _handle_transaction_action(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, action: str):
        """معالجة الموافقة/رفض المعاملات"""
        try:
            transaction_id = int(text)
            
            session = db.get_session()
            try:
                transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
                if not transaction:
                    await update.message.reply_text(
                        "❌ المعاملة غير موجودة",
                        reply_markup=Keyboards.admin_panel()
                    )
                    return
                
                if transaction.status != 'pending':
                    await update.message.reply_text(
                        f"❌ المعاملة {transaction.status} بالفعل",
                        reply_markup=Keyboards.admin_panel()
                    )
                    return
                
                user = session.query(User).filter(User.id == transaction.user_id).first()
                
                if action == 'approve':
                    transaction.status = 'completed'
                    
                    if transaction.transaction_type == 'deposit':
                        user.balance += transaction.amount
                    
                    status_text = "تمت الموافقة على"
                    emoji = "✅"
                else:
                    transaction.status = 'rejected'
                    status_text = "تم رفض"
                    emoji = "❌"
                
                session.commit()
                
                # إشعار المستخدم
                try:
                    await context.bot.send_message(
                        chat_id=user.telegram_id,
                        text=f"{emoji} {status_text} طلب {transaction.transaction_type} بقيمة {format_currency(transaction.amount)}"
                    )
                except TelegramError:
                    logger.warning(f"لا يمكن إرسال إشعار للمستخدم {user.telegram_id}")
                
                await update.message.reply_text(
                    f"{emoji} {status_text} المعاملة رقم {transaction_id} بنجاح",
                    reply_markup=Keyboards.admin_panel()
                )
            finally:
                session.close()
                
        except ValueError:
            await update.message.reply_text(
                "❌ رقم المعاملة غير صحيح",
                reply_markup=Keyboards.admin_panel()
            )
    
    @staticmethod
    async def _handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """معالجة الرسالة الجماعية"""
        session = db.get_session()
        try:
            users = session.query(User).all()
            sent_count = 0
            failed_count = 0
            
            for user in users:
                try:
                    await context.bot.send_message(
                        chat_id=user.telegram_id,
                        text=f"📢 رسالة من الإدارة:\n\n{text}"
                    )
                    sent_count += 1
                except TelegramError:
                    failed_count += 1
                    logger.warning(f"فشل إرسال الرسالة للمستخدم {user.telegram_id}")
            
            await update.message.reply_text(
                f"📢 تم إرسال الرسالة الجماعية\n✅ تم الإرسال: {sent_count}\n❌ فشل الإرسال: {failed_count}",
                reply_markup=Keyboards.admin_panel()
            )
        finally:
            session.close()

