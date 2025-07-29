"""
معالج المدفوعات والمعاملات المالية
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from database import DatabaseManager, User, Transaction
from config import Config
from keyboards import Keyboards
from utils import format_currency, validate_amount, get_user_display_name, generate_transaction_reference

logger = logging.getLogger(__name__)
db = DatabaseManager()

class PaymentHandler:
    """معالج المدفوعات"""
    
    @staticmethod
    async def process_deposit_request(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: float, method: str):
        """معالجة طلب الإيداع"""
        user = db.get_user(update.effective_user.id)
        
        # التحقق من صحة المبلغ
        is_valid, validated_amount, error_msg = validate_amount(
            str(amount), 
            Config.MIN_DEPOSIT, 
            Config.MAX_DEPOSIT
        )
        
        if not is_valid:
            await update.message.reply_text(
                error_msg,
                reply_markup=Keyboards.main_menu()
            )
            return
        
        # إنشاء معاملة جديدة
        session = db.get_session()
        try:
            transaction = Transaction(
                user_id=user.id,
                transaction_type="deposit",
                amount=validated_amount,
                method=method,
                status="pending",
                description=f"طلب إيداع عبر {Config.PAYMENT_METHODS[method]['name']}"
            )
            session.add(transaction)
            session.commit()
            session.refresh(transaction)
            
            # التحقق من إمكانية المعالجة التلقائية
            method_config = Config.PAYMENT_METHODS[method]
            if method_config.get("auto_enabled", False):
                # معالجة تلقائية (إذا كان API متوفر)
                success = await PaymentHandler.process_automatic_deposit(transaction, method_config)
                if success:
                    await PaymentHandler.complete_deposit(transaction.id, update, context)
                    return
            
            # معالجة يدوية
            await PaymentHandler.process_manual_deposit(transaction, update, context)
            
        finally:
            session.close()
    
    @staticmethod
    async def process_withdraw_request(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: float, method: str):
        """معالجة طلب السحب"""
        user = db.get_user(update.effective_user.id)
        
        # التحقق من صحة المبلغ
        is_valid, validated_amount, error_msg = validate_amount(
            str(amount), 
            Config.MIN_WITHDRAWAL, 
            min(Config.MAX_WITHDRAWAL, user.balance)
        )
        
        if not is_valid:
            await update.message.reply_text(
                error_msg,
                reply_markup=Keyboards.main_menu()
            )
            return
        
        # التحقق من كفاية الرصيد
        if user.balance < validated_amount:
            await update.message.reply_text(
                f"❌ رصيدك غير كافي\n💵 رصيدك الحالي: {format_currency(user.balance)}",
                reply_markup=Keyboards.main_menu()
            )
            return
        
        # إنشاء معاملة جديدة
        session = db.get_session()
        try:
            transaction = Transaction(
                user_id=user.id,
                transaction_type="withdraw",
                amount=validated_amount,
                method=method,
                status="pending",
                description=f"طلب سحب عبر {Config.PAYMENT_METHODS[method]['name']}"
            )
            session.add(transaction)
            session.commit()
            session.refresh(transaction)
            
            # خصم المبلغ مؤقتاً (سيتم إرجاعه في حالة الرفض)
            user.balance -= validated_amount
            session.commit()
            
            # التحقق من إمكانية المعالجة التلقائية
            method_config = Config.PAYMENT_METHODS[method]
            if method_config.get("auto_enabled", False):
                # معالجة تلقائية (إذا كان API متوفر)
                success = await PaymentHandler.process_automatic_withdrawal(transaction, method_config)
                if success:
                    await PaymentHandler.complete_withdrawal(transaction.id, update, context)
                    return
            
            # معالجة يدوية
            await PaymentHandler.process_manual_withdrawal(transaction, update, context)
            
        finally:
            session.close()
    
    @staticmethod
    async def process_manual_deposit(transaction: Transaction, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الإيداع اليدوي"""
        method_info = Config.PAYMENT_METHODS[transaction.method]
        reference = generate_transaction_reference()
        
        # تحديث مرجع المعاملة
        session = db.get_session()
        try:
            transaction.description += f"\nمرجع المعاملة: {reference}"
            session.commit()
        finally:
            session.close()
        
        # رسالة للمستخدم
        user_message = f"""
✅ تم إنشاء طلب الإيداع بنجاح!

💰 المبلغ: {format_currency(transaction.amount)}
🏦 الطريقة: {method_info['name']} {method_info['emoji']}
🔢 مرجع المعاملة: {reference}
⏳ الحالة: قيد المراجعة

📝 تعليمات الدفع:
{PaymentHandler.get_payment_instructions(transaction.method, transaction.amount)}

⏰ سيتم مراجعة طلبك خلال 24 ساعة وإضافة الرصيد لحسابك بعد التأكيد.
        """
        
        await update.message.reply_text(
            user_message,
            reply_markup=Keyboards.main_menu()
        )
        
        # إشعار الإدمن
        await PaymentHandler.notify_admin_deposit(transaction, reference, context)
    
    @staticmethod
    async def process_manual_withdrawal(transaction: Transaction, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة السحب اليدوي"""
        method_info = Config.PAYMENT_METHODS[transaction.method]
        reference = generate_transaction_reference()
        
        # تحديث مرجع المعاملة
        session = db.get_session()
        try:
            transaction.description += f"\nمرجع المعاملة: {reference}"
            session.commit()
        finally:
            session.close()
        
        # رسالة للمستخدم
        user_message = f"""
✅ تم إنشاء طلب السحب بنجاح!

💸 المبلغ: {format_currency(transaction.amount)}
🏦 الطريقة: {method_info['name']} {method_info['emoji']}
🔢 مرجع المعاملة: {reference}
⏳ الحالة: قيد المراجعة

💵 تم خصم المبلغ مؤقتاً من رصيدك
⏰ سيتم تحويل المبلغ خلال 24 ساعة بعد المراجعة
        """
        
        await update.message.reply_text(
            user_message,
            reply_markup=Keyboards.main_menu()
        )
        
        # إشعار الإدمن
        await PaymentHandler.notify_admin_withdrawal(transaction, reference, context)
    
    @staticmethod
    async def process_automatic_deposit(transaction: Transaction, method_config: Dict[str, Any]) -> bool:
        """معالجة الإيداع التلقائي"""
        # هنا يمكن إضافة كود API للمعالجة التلقائية
        # مثال: استدعاء API سيريتل كاش أو البنك
        
        # للتجربة، نعتبر أن المعالجة التلقائية غير متوفرة حالياً
        return False
    
    @staticmethod
    async def process_automatic_withdrawal(transaction: Transaction, method_config: Dict[str, Any]) -> bool:
        """معالجة السحب التلقائي"""
        # هنا يمكن إضافة كود API للمعالجة التلقائية
        # مثال: استدعاء API سيريتل كاش أو البنك
        
        # للتجربة، نعتبر أن المعالجة التلقائية غير متوفرة حالياً
        return False
    
    @staticmethod
    async def complete_deposit(transaction_id: int, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إتمام عملية الإيداع"""
        session = db.get_session()
        try:
            transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
            if not transaction:
                return
            
            user = session.query(User).filter(User.id == transaction.user_id).first()
            if not user:
                return
            
            # إضافة الرصيد
            user.balance += transaction.amount
            transaction.status = "completed"
            transaction.processed_at = datetime.utcnow()
            
            # معالجة أرباح الإحالة
            if user.referred_by:
                await PaymentHandler.process_referral_earnings(user, transaction.amount, session)
            
            session.commit()
            
            # إشعار المستخدم
            try:
                await context.bot.send_message(
                    chat_id=user.telegram_id,
                    text=f"✅ تم إتمام عملية الإيداع بنجاح!\n💰 المبلغ: {format_currency(transaction.amount)}\n💵 رصيدك الجديد: {format_currency(user.balance)}",
                    reply_markup=Keyboards.main_menu()
                )
            except TelegramError:
                logger.warning(f"لا يمكن إرسال إشعار للمستخدم {user.telegram_id}")
            
        finally:
            session.close()
    
    @staticmethod
    async def complete_withdrawal(transaction_id: int, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إتمام عملية السحب"""
        session = db.get_session()
        try:
            transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
            if not transaction:
                return
            
            user = session.query(User).filter(User.id == transaction.user_id).first()
            if not user:
                return
            
            # تأكيد السحب
            transaction.status = "completed"
            transaction.processed_at = datetime.utcnow()
            session.commit()
            
            # إشعار المستخدم
            try:
                await context.bot.send_message(
                    chat_id=user.telegram_id,
                    text=f"✅ تم إتمام عملية السحب بنجاح!\n💸 المبلغ: {format_currency(transaction.amount)}\n💵 رصيدك الحالي: {format_currency(user.balance)}",
                    reply_markup=Keyboards.main_menu()
                )
            except TelegramError:
                logger.warning(f"لا يمكن إرسال إشعار للمستخدم {user.telegram_id}")
            
        finally:
            session.close()
    
    @staticmethod
    async def reject_transaction(transaction_id: int, reason: str, context: ContextTypes.DEFAULT_TYPE):
        """رفض المعاملة"""
        session = db.get_session()
        try:
            transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
            if not transaction:
                return
            
            user = session.query(User).filter(User.id == transaction.user_id).first()
            if not user:
                return
            
            # إرجاع الرصيد في حالة السحب
            if transaction.transaction_type == "withdraw" and transaction.status == "pending":
                user.balance += transaction.amount
            
            transaction.status = "failed"
            transaction.admin_notes = reason
            transaction.processed_at = datetime.utcnow()
            session.commit()
            
            # إشعار المستخدم
            try:
                await context.bot.send_message(
                    chat_id=user.telegram_id,
                    text=f"❌ تم رفض طلب {transaction.transaction_type}\n💰 المبلغ: {format_currency(transaction.amount)}\n📝 السبب: {reason}",
                    reply_markup=Keyboards.main_menu()
                )
            except TelegramError:
                logger.warning(f"لا يمكن إرسال إشعار للمستخدم {user.telegram_id}")
            
        finally:
            session.close()
    
    @staticmethod
    async def process_referral_earnings(user: User, deposit_amount: float, session):
        """معالجة أرباح الإحالة"""
        if not user.referred_by:
            return
        
        # البحث عن المُحيل
        referrer = session.query(User).filter(User.referral_code == user.referred_by).first()
        if not referrer:
            return
        
        # حساب الأرباح
        earnings = deposit_amount * (Config.REFERRAL_PERCENTAGE / 100)
        
        # إضافة الأرباح للمُحيل
        referrer.referral_earnings += earnings
        referrer.balance += earnings
        
        # إنشاء معاملة أرباح الإحالة
        referral_transaction = Transaction(
            user_id=referrer.id,
            transaction_type="referral",
            amount=earnings,
            status="completed",
            description=f"أرباح إحالة من {get_user_display_name(user)} - إيداع {format_currency(deposit_amount)}"
        )
        session.add(referral_transaction)
    
    @staticmethod
    def get_payment_instructions(method: str, amount: float) -> str:
        """الحصول على تعليمات الدفع"""
        instructions = {
            "syriatel_cash": f"""
📱 سيريتل كاش:
• ادفع المبلغ {format_currency(amount)} إلى الرقم: 0999123456
• أرسل لقطة شاشة من عملية الدفع
• تأكد من إرسال المبلغ الصحيح
            """,
            "bank": f"""
🏦 التحويل البنكي:
• اسم البنك: البنك التجاري السوري
• رقم الحساب: 123456789
• اسم صاحب الحساب: شركة المدفوعات
• المبلغ: {format_currency(amount)}
• أرسل صورة من إيصال التحويل
            """,
            "usdt": f"""
💰 USDT (TRC20):
• العنوان: TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx
• الشبكة: TRON (TRC20)
• المبلغ: {amount / 3000:.2f} USDT (سعر الصرف: 3000 ل.س)
• أرسل hash المعاملة بعد التحويل
            """
        }
        
        return instructions.get(method, "تعليمات الدفع غير متوفرة")
    
    @staticmethod
    async def notify_admin_deposit(transaction: Transaction, reference: str, context: ContextTypes.DEFAULT_TYPE):
        """إشعار الإدمن بطلب الإيداع"""
        user = db.get_user_by_id(transaction.user_id)
        method_info = Config.PAYMENT_METHODS[transaction.method]
        
        admin_message = f"""
🔔 طلب إيداع جديد

👤 المستخدم: {get_user_display_name(user)}
🆔 المعرف: {user.telegram_id}
💰 المبلغ: {format_currency(transaction.amount)}
🏦 الطريقة: {method_info['name']} {method_info['emoji']}
🔢 المرجع: {reference}
📅 التاريخ: {transaction.created_at.strftime('%Y-%m-%d %H:%M')}

استخدم /admin لإدارة الطلبات
        """
        
        for admin_id in Config.ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=admin_message
                )
            except TelegramError:
                logger.warning(f"لا يمكن إرسال إشعار للإدمن {admin_id}")
    
    @staticmethod
    async def notify_admin_withdrawal(transaction: Transaction, reference: str, context: ContextTypes.DEFAULT_TYPE):
        """إشعار الإدمن بطلب السحب"""
        user = db.get_user_by_id(transaction.user_id)
        method_info = Config.PAYMENT_METHODS[transaction.method]
        
        admin_message = f"""
🔔 طلب سحب جديد

👤 المستخدم: {get_user_display_name(user)}
🆔 المعرف: {user.telegram_id}
💸 المبلغ: {format_currency(transaction.amount)}
🏦 الطريقة: {method_info['name']} {method_info['emoji']}
🔢 المرجع: {reference}
💵 الرصيد بعد السحب: {format_currency(user.balance)}
📅 التاريخ: {transaction.created_at.strftime('%Y-%m-%d %H:%M')}

استخدم /admin لإدارة الطلبات
        """
        
        for admin_id in Config.ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=admin_message
                )
            except TelegramError:
                logger.warning(f"لا يمكن إرسال إشعار للإدمن {admin_id}")

# إضافة دالة مساعدة لقاعدة البيانات
def get_user_by_id(user_id: int) -> Optional[User]:
    """الحصول على مستخدم بواسطة ID"""
    session = db.get_session()
    try:
        return session.query(User).filter(User.id == user_id).first()
    finally:
        session.close()

# إضافة الدالة لفئة DatabaseManager
DatabaseManager.get_user_by_id = get_user_by_id

