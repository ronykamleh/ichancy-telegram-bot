"""
معالجات أوامر البوت
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from database import DatabaseManager, User, Transaction
from config import Config
from keyboards import Keyboards
from utils import format_currency, validate_amount, get_user_display_name
from payment_handler import PaymentHandler
from referral_handler import ReferralHandler
from admin_handler import AdminHandler
from contact_handler import ContactHandler
from gaming_handler import GamingHandler

logger = logging.getLogger(__name__)
db = DatabaseManager()

# حالات المحادثة
WAITING_FOR_AMOUNT = "waiting_for_amount"
WAITING_FOR_RECIPIENT = "waiting_for_recipient"
WAITING_FOR_GIFT_CODE = "waiting_for_gift_code"
WAITING_FOR_MESSAGE = "waiting_for_message"

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر البدء"""
    user_id = update.effective_user.id
    
    # التحقق من وجود كود إحالة
    referral_code = None
    if context.args and len(context.args) > 0:
        referral_code = context.args[0]
    
    # إنشاء أو الحصول على المستخدم
    user = db.get_user(user_id)
    if not user:
        user = db.create_user(
            telegram_id=user_id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            last_name=update.effective_user.last_name
        )
        
        # معالجة الإحالة
        if referral_code and referral_code != user.referral_code:
            await handle_referral(user, referral_code)
    
    # رسالة الترحيب
    welcome_message = Config.MESSAGES["welcome"].format(
        referral_code=user.referral_code,
        balance=format_currency(user.balance)
    )
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=Keyboards.main_menu()
    )

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج القائمة الرئيسية"""
    user = db.get_user(update.effective_user.id)
    if not user:
        await start_handler(update, context)
        return
    
    message = Config.MESSAGES["main_menu"].format(
        balance=format_currency(user.balance),
        referral_count=user.referral_count,
        referral_earnings=format_currency(user.referral_earnings)
    )
    
    if update.message:
        await update.message.reply_text(message, reply_markup=Keyboards.main_menu())
    else:
        await update.callback_query.edit_message_text(message, reply_markup=Keyboards.main_menu())

async def deposit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الإيداع"""
    message = """
💰 شحن رصيد في البوت

اختر طريقة الدفع المفضلة لديك:
    """
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            reply_markup=Keyboards.payment_methods("deposit")
        )
    else:
        await update.message.reply_text(
            message,
            reply_markup=Keyboards.payment_methods("deposit")
        )

async def withdraw_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج السحب"""
    user = db.get_user(update.effective_user.id)
    
    if user.balance < Config.MIN_WITHDRAWAL:
        message = f"❌ الحد الأدنى للسحب هو {format_currency(Config.MIN_WITHDRAWAL)}\n💵 رصيدك الحالي: {format_currency(user.balance)}"
        
        if update.callback_query:
            await update.callback_query.answer(message, show_alert=True)
        else:
            await update.message.reply_text(message, reply_markup=Keyboards.main_menu())
        return
    
    message = f"""
💸 سحب رصيد من البوت

💵 رصيدك الحالي: {format_currency(user.balance)}
💰 الحد الأدنى للسحب: {format_currency(Config.MIN_WITHDRAWAL)}
💰 الحد الأقصى للسحب: {format_currency(Config.MAX_WITHDRAWAL)}

اختر طريقة السحب:
    """
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            reply_markup=Keyboards.payment_methods("withdraw")
        )
    else:
        await update.message.reply_text(
            message,
            reply_markup=Keyboards.payment_methods("withdraw")
        )

async def referral_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج نظام الإحالات"""
    user = db.get_user(update.effective_user.id)
    
    bot_username = context.bot.username
    referral_link = f"https://t.me/{bot_username}?start={user.referral_code}"
    
    message = f"""
👥 نظام الإحالات

🔗 رابط الإحالة الخاص بك:
{referral_link}

📊 إحصائياتك:
👥 عدد الإحالات: {user.referral_count}
💰 أرباح الإحالات: {format_currency(user.referral_earnings)}
📈 نسبة الربح: {Config.REFERRAL_PERCENTAGE}%

💡 كيف يعمل نظام الإحالات:
• شارك رابطك مع الأصدقاء
• عند تسجيلهم ستحصل على {Config.REFERRAL_PERCENTAGE}% من كل عملية إيداع يقومون بها
• يمكنك سحب أرباح الإحالات في أي وقت
    """
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            reply_markup=Keyboards.referral_menu()
        )
    else:
        await update.message.reply_text(
            message,
            reply_markup=Keyboards.referral_menu()
        )

async def gift_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج إهداء الرصيد"""
    user = db.get_user(update.effective_user.id)
    
    if user.balance < Config.MIN_GIFT:
        message = f"❌ الحد الأدنى للإهداء هو {format_currency(Config.MIN_GIFT)}\n💵 رصيدك الحالي: {format_currency(user.balance)}"
        
        if update.callback_query:
            await update.callback_query.answer(message, show_alert=True)
        else:
            await update.message.reply_text(message, reply_markup=Keyboards.main_menu())
        return
    
    message = f"""
🎁 إهداء رصيد

💵 رصيدك الحالي: {format_currency(user.balance)}
💰 الحد الأدنى للإهداء: {format_currency(Config.MIN_GIFT)}

📝 لإهداء رصيد لصديق، أرسل المبلغ الذي تريد إهداءه:
    """
    
    # حفظ حالة المحادثة
    context.user_data['state'] = WAITING_FOR_AMOUNT
    context.user_data['operation'] = 'gift'
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            reply_markup=Keyboards.cancel_operation()
        )
    else:
        await update.message.reply_text(
            message,
            reply_markup=Keyboards.cancel_operation()
        )

async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج لوحة الإدمن"""
    user_id = update.effective_user.id
    
    if user_id not in Config.ADMIN_IDS:
        await update.message.reply_text("❌ ليس لديك صلاحية للوصول إلى لوحة الإدمن")
        return
    
    message = """
🔧 لوحة تحكم الإدمن

مرحباً بك في لوحة التحكم. اختر العملية المطلوبة:
    """
    
    await update.message.reply_text(
        message,
        reply_markup=Keyboards.admin_panel()
    )

async def transaction_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج سجل المعاملات"""
    message = """
📜 سجل العمليات

اختر نوع المعاملات التي تريد عرضها:
    """
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            reply_markup=Keyboards.transaction_history_menu()
        )
    else:
        await update.message.reply_text(
            message,
            reply_markup=Keyboards.transaction_history_menu()
        )

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج التواصل"""
    message = """
📧 تواصل معنا

يمكنك التواصل معنا من خلال الخيارات التالية:
    """
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            reply_markup=Keyboards.contact_menu()
        )
    else:
        await update.message.reply_text(
            message,
            reply_markup=Keyboards.contact_menu()
        )

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الاستعلامات المضمنة"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # القائمة الرئيسية
    if data == "main_menu":
        await main_menu_handler(update, context)
    
    # الإيداع والسحب
    elif data == "deposit":
        await deposit_handler(update, context)
    elif data == "withdraw":
        await withdraw_handler(update, context)
    
    # نظام الإحالات
    elif data == "referrals":
        await referral_handler(update, context)
    
    # إهداء الرصيد
    elif data == "gift_balance":
        await gift_handler(update, context)
    
    # كود الهدية
    elif data == "gift_code":
        await handle_gift_code_menu(update, context)
    
    # التواصل
    elif data == "contact":
        await contact_handler(update, context)
    
    # رسالة للإدمن
    elif data == "message_admin":
        await handle_message_admin(update, context)
    
    # سجل المعاملات
    elif data == "transactions":
        await transaction_handler(update, context)
    
    # الشروط والأحكام
    elif data == "terms":
        await handle_terms(update, context)
    
    # معالجة طرق الدفع
    elif data.startswith("deposit_") or data.startswith("withdraw_"):
        await handle_payment_method(update, context, data)
    
    # إلغاء العملية
    elif data == "cancel_operation":
        context.user_data.clear()
        await main_menu_handler(update, context)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الرسائل النصية"""
    user_state = context.user_data.get('state')
    
    if user_state == WAITING_FOR_AMOUNT:
        await handle_amount_input(update, context)
    elif user_state == WAITING_FOR_RECIPIENT:
        await handle_recipient_input(update, context)
    elif user_state == WAITING_FOR_GIFT_CODE:
        await handle_gift_code_input(update, context)
    elif user_state == WAITING_FOR_MESSAGE:
        await handle_message_input(update, context)
    else:
        # رسالة افتراضية
        await update.message.reply_text(
            "استخدم الأزرار أدناه للتنقل في البوت:",
            reply_markup=Keyboards.main_menu()
        )

# دوال مساعدة

async def handle_referral(user, referral_code):
    """معالجة الإحالة"""
    session = db.get_session()
    try:
        referrer = session.query(User).filter(User.referral_code == referral_code).first()
        if referrer and referrer.id != user.id:
            user.referred_by = referral_code
            referrer.referral_count += 1
            session.commit()
            logger.info(f"تم تسجيل إحالة جديدة: {user.telegram_id} -> {referrer.telegram_id}")
    finally:
        session.close()

async def handle_amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إدخال المبلغ"""
    try:
        amount = float(update.message.text)
        operation = context.user_data.get('operation')
        method = context.user_data.get('method')
        
        if operation == 'gift':
            user = db.get_user(update.effective_user.id)
            
            if amount < Config.MIN_GIFT:
                await update.message.reply_text(
                    f"❌ الحد الأدنى للإهداء هو {format_currency(Config.MIN_GIFT)}",
                    reply_markup=Keyboards.cancel_operation()
                )
                return
            
            if amount > user.balance:
                await update.message.reply_text(
                    f"❌ رصيدك غير كافي\n💵 رصيدك الحالي: {format_currency(user.balance)}",
                    reply_markup=Keyboards.cancel_operation()
                )
                return
            
            context.user_data['amount'] = amount
            context.user_data['state'] = WAITING_FOR_RECIPIENT
            
            await update.message.reply_text(
                f"💰 المبلغ: {format_currency(amount)}\n\n👤 الآن أرسل معرف المستخدم أو اسم المستخدم للشخص الذي تريد إهداءه:",
                reply_markup=Keyboards.cancel_operation()
            )
        
        elif operation == 'deposit':
            # معالجة طلب الإيداع
            context.user_data.clear()
            await PaymentHandler.process_deposit_request(update, context, amount, method)
        
        elif operation == 'withdraw':
            # معالجة طلب السحب
            context.user_data.clear()
            await PaymentHandler.process_withdraw_request(update, context, amount, method)
    
    except ValueError:
        await update.message.reply_text(
            "❌ يرجى إدخال مبلغ صحيح",
            reply_markup=Keyboards.cancel_operation()
        )

async def handle_recipient_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إدخال المستلم"""
    recipient_input = update.message.text.strip()
    
    # البحث عن المستخدم
    session = db.get_session()
    try:
        recipient = None
        
        # البحث بمعرف التليجرام
        if recipient_input.isdigit():
            recipient = session.query(User).filter(User.telegram_id == recipient_input).first()
        
        # البحث باسم المستخدم
        if not recipient and recipient_input.startswith('@'):
            username = recipient_input[1:]
            recipient = session.query(User).filter(User.username == username).first()
        elif not recipient:
            recipient = session.query(User).filter(User.username == recipient_input).first()
        
        if not recipient:
            await update.message.reply_text(
                "❌ المستخدم غير موجود. تأكد من صحة المعرف أو اسم المستخدم",
                reply_markup=Keyboards.cancel_operation()
            )
            return
        
        # تنفيذ عملية الإهداء
        amount = context.user_data['amount']
        sender = db.get_user(update.effective_user.id)
        
        if sender.balance >= amount:
            # خصم من المرسل
            sender.balance -= amount
            # إضافة للمستلم
            recipient.balance += amount
            
            # إضافة سجل الهدية
            from database import Gift
            gift = Gift(
                sender_id=sender.id,
                receiver_id=recipient.id,
                amount=amount
            )
            session.add(gift)
            session.commit()
            
            # رسالة تأكيد للمرسل
            await update.message.reply_text(
                f"✅ تم إهداء {format_currency(amount)} بنجاح!\n👤 إلى: {get_user_display_name(recipient)}",
                reply_markup=Keyboards.main_menu()
            )
            
            # إشعار للمستلم
            try:
                await context.bot.send_message(
                    chat_id=recipient.telegram_id,
                    text=f"🎁 تهانينا! لقد تلقيت هدية بقيمة {format_currency(amount)}\n👤 من: {get_user_display_name(sender)}",
                    reply_markup=Keyboards.main_menu()
                )
            except TelegramError:
                logger.warning(f"لا يمكن إرسال إشعار للمستخدم {recipient.telegram_id}")
        
        else:
            await update.message.reply_text(
                "❌ رصيدك غير كافي لإتمام هذه العملية",
                reply_markup=Keyboards.main_menu()
            )
        
        # مسح حالة المحادثة
        context.user_data.clear()
        
    finally:
        session.close()

async def handle_gift_code_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة قائمة كود الهدية"""
    message = """
🎁 كود هدية

أرسل كود الهدية للحصول على رصيد مجاني:
    """
    
    context.user_data['state'] = WAITING_FOR_GIFT_CODE
    
    await update.callback_query.edit_message_text(
        message,
        reply_markup=Keyboards.cancel_operation()
    )

async def handle_gift_code_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إدخال كود الهدية"""
    code = update.message.text.strip().upper()
    
    session = db.get_session()
    try:
        from database import GiftCode, GiftCodeUsage
        
        # البحث عن الكود
        gift_code = session.query(GiftCode).filter(
            GiftCode.code == code,
            GiftCode.is_active == True
        ).first()
        
        if not gift_code:
            await update.message.reply_text(
                "❌ كود الهدية غير صحيح أو منتهي الصلاحية",
                reply_markup=Keyboards.main_menu()
            )
            context.user_data.clear()
            return
        
        # التحقق من عدد الاستخدامات
        if gift_code.current_uses >= gift_code.max_uses:
            await update.message.reply_text(
                "❌ تم استنفاد عدد استخدامات هذا الكود",
                reply_markup=Keyboards.main_menu()
            )
            context.user_data.clear()
            return
        
        # التحقق من استخدام المستخدم للكود مسبقاً
        user = db.get_user(update.effective_user.id)
        existing_usage = session.query(GiftCodeUsage).filter(
            GiftCodeUsage.code_id == gift_code.id,
            GiftCodeUsage.user_id == user.id
        ).first()
        
        if existing_usage:
            await update.message.reply_text(
                "❌ لقد استخدمت هذا الكود من قبل",
                reply_markup=Keyboards.main_menu()
            )
            context.user_data.clear()
            return
        
        # تطبيق الكود
        user.balance += gift_code.amount
        gift_code.current_uses += 1
        
        # تسجيل الاستخدام
        usage = GiftCodeUsage(
            code_id=gift_code.id,
            user_id=user.id
        )
        session.add(usage)
        session.commit()
        
        await update.message.reply_text(
            f"🎉 تهانينا! تم إضافة {format_currency(gift_code.amount)} إلى رصيدك\n💵 رصيدك الجديد: {format_currency(user.balance)}",
            reply_markup=Keyboards.main_menu()
        )
        
        context.user_data.clear()
        
    finally:
        session.close()

async def handle_message_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إرسال رسالة للإدمن"""
    message = """
📩 رسالة للإدمن

أرسل رسالتك وسيتم توصيلها للإدارة:
    """
    
    context.user_data['state'] = WAITING_FOR_MESSAGE
    
    await update.callback_query.edit_message_text(
        message,
        reply_markup=Keyboards.cancel_operation()
    )

async def handle_message_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إدخال الرسالة"""
    message_text = update.message.text
    user = db.get_user(update.effective_user.id)
    
    session = db.get_session()
    try:
        from database import AdminMessage
        
        admin_message = AdminMessage(
            user_id=user.id,
            message=message_text
        )
        session.add(admin_message)
        session.commit()
        
        # إشعار الإدمن
        for admin_id in Config.ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"📩 رسالة جديدة من المستخدم {get_user_display_name(user)}\n\n{message_text}"
                )
            except TelegramError:
                logger.warning(f"لا يمكن إرسال إشعار للإدمن {admin_id}")
        
        await update.message.reply_text(
            "✅ تم إرسال رسالتك للإدارة. سيتم الرد عليك قريباً",
            reply_markup=Keyboards.main_menu()
        )
        
        context.user_data.clear()
        
    finally:
        session.close()

async def handle_terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الشروط والأحكام"""
    terms_text = """
📌 الشروط والأحكام

🔸 شروط الاستخدام:
• يجب أن تكون فوق 18 سنة لاستخدام الخدمة
• ممنوع استخدام البوت لأغراض غير قانونية
• الحد الأدنى للإيداع: {min_deposit} ل.س
• الحد الأدنى للسحب: {min_withdrawal} ل.س

🔸 سياسة الإحالات:
• تحصل على {referral_percentage}% من كل إيداع يقوم به المُحال
• أرباح الإحالات قابلة للسحب في أي وقت

🔸 سياسة الخصوصية:
• نحن نحترم خصوصيتك ولا نشارك بياناتك مع أطراف ثالثة
• يتم تشفير جميع المعاملات المالية

🔸 المسؤولية:
• الإدارة غير مسؤولة عن أي خسائر ناتجة عن سوء الاستخدام
• يحق للإدارة تعليق أو إغلاق أي حساب يخالف الشروط

📞 للاستفسارات: استخدم زر "تواصل معنا"
    """.format(
        min_deposit=format_currency(Config.MIN_DEPOSIT),
        min_withdrawal=format_currency(Config.MIN_WITHDRAWAL),
        referral_percentage=Config.REFERRAL_PERCENTAGE
    )
    
    await update.callback_query.edit_message_text(
        terms_text,
        reply_markup=Keyboards.back_to_main()
    )

async def handle_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة اختيار طريقة الدفع"""
    data = update.callback_query.data
    operation, method = data.split('_', 1)
    
    method_info = Config.PAYMENT_METHODS.get(method)
    if not method_info:
        await update.callback_query.answer("❌ طريقة دفع غير صحيحة")
        return
    
    if operation == "deposit":
        message = f"""
💰 الإيداع عبر {method_info['name']} {method_info['emoji']}

📝 تعليمات الإيداع:
1. أرسل المبلغ الذي تريد إيداعه
2. سيتم توجيهك لإتمام عملية الدفع
3. بعد التأكيد سيتم إضافة الرصيد لحسابك

💰 الحد الأدنى: {format_currency(Config.MIN_DEPOSIT)}
💰 الحد الأقصى: {format_currency(Config.MAX_DEPOSIT)}

أرسل المبلغ الآن:
        """
    else:  # withdraw
        user = db.get_user(update.effective_user.id)
        message = f"""
💸 السحب عبر {method_info['name']} {method_info['emoji']}

💵 رصيدك الحالي: {format_currency(user.balance)}
💰 الحد الأدنى: {format_currency(Config.MIN_WITHDRAWAL)}
💰 الحد الأقصى: {format_currency(Config.MAX_WITHDRAWAL)}

📝 تعليمات السحب:
1. أرسل المبلغ الذي تريد سحبه
2. سيتم مراجعة طلبك من قبل الإدارة
3. سيتم تحويل المبلغ خلال 24 ساعة

أرسل المبلغ الآن:
        """
    
    context.user_data['state'] = WAITING_FOR_AMOUNT
    context.user_data['operation'] = operation
    context.user_data['method'] = method
    
    await update.callback_query.edit_message_text(
        message,
        reply_markup=Keyboards.cancel_operation()
    )

