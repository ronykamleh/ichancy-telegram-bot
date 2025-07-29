"""
معالج الألعاب والجاكبوت - ichancy.com
"""

import logging
import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from database import DatabaseManager, User, Transaction
from config import Config
from keyboards import Keyboards
from utils import format_currency, get_user_display_name

logger = logging.getLogger(__name__)
db = DatabaseManager()

class GamingHandler:
    """فئة معالج الألعاب والجاكبوت"""
    
    @staticmethod
    async def jackpot_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """قائمة الجاكبوت الرئيسية"""
        session = db.get_session()
        try:
            # الحصول على قيمة الجاكبوت الحالية
            current_jackpot = session.query(db.func.sum(Transaction.amount)).filter(
                Transaction.transaction_type == 'jackpot_contribution',
                Transaction.status == 'completed'
            ).scalar() or 0
            
            # آخر فائز بالجاكبوت
            last_winner = session.query(Transaction).filter(
                Transaction.transaction_type == 'jackpot_win'
            ).order_by(Transaction.created_at.desc()).first()
            
            last_winner_info = ""
            if last_winner:
                winner_user = session.query(User).filter(User.id == last_winner.user_id).first()
                last_winner_info = f"\n🏆 آخر فائز: {get_user_display_name(winner_user)}\n💰 المبلغ: {format_currency(abs(last_winner.amount))}\n📅 التاريخ: {last_winner.created_at.strftime('%Y-%m-%d')}"
            
            message = f"""
🎲 الجاكبوت - ichancy.com

💎 قيمة الجاكبوت الحالية: {format_currency(current_jackpot)}

🎯 كيف تلعب:
• ادخل إلى موقع ichancy.com
• العب في الكازينو أو الرهانات الرياضية
• كل رهان يساهم في الجاكبوت
• اربح الجاكبوت الكامل بالحظ!

🌟 ميزات خاصة:
• جاكبوت متراكم يومياً
• فرص فوز عادلة للجميع
• مكافآت إضافية للفائزين
{last_winner_info}

🔗 العب الآن على ichancy.com
            """
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    message,
                    reply_markup=Keyboards.jackpot_menu()
                )
            else:
                await update.message.reply_text(
                    message,
                    reply_markup=Keyboards.jackpot_menu()
                )
        finally:
            session.close()
    
    @staticmethod
    async def betting_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """سجل الرهانات"""
        user = db.get_user(update.effective_user.id)
        
        session = db.get_session()
        try:
            # الحصول على رهانات المستخدم
            bets = session.query(Transaction).filter(
                Transaction.user_id == user.id,
                Transaction.transaction_type.in_(['bet_win', 'bet_loss', 'casino_win', 'casino_loss'])
            ).order_by(Transaction.created_at.desc()).limit(10).all()
            
            if not bets:
                message = """
📜 سجل الرهانات

❌ لا توجد رهانات مسجلة حتى الآن

🎯 ابدأ اللعب على ichancy.com لتسجيل رهاناتك هنا!
                """
            else:
                message = "📜 سجل الرهانات\n\n"
                
                total_wins = 0
                total_losses = 0
                
                for i, bet in enumerate(bets, 1):
                    bet_type = "🏆 فوز" if "win" in bet.transaction_type else "❌ خسارة"
                    game_type = "🎰 كازينو" if "casino" in bet.transaction_type else "⚽ رياضة"
                    
                    if "win" in bet.transaction_type:
                        total_wins += bet.amount
                    else:
                        total_losses += abs(bet.amount)
                    
                    message += f"{i}. {game_type} {bet_type}\n"
                    message += f"💰 {format_currency(abs(bet.amount))}\n"
                    message += f"📅 {bet.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                    if bet.description:
                        message += f"📝 {bet.description}\n"
                    message += "\n"
                
                # إحصائيات
                net_result = total_wins - total_losses
                message += f"📊 الإحصائيات:\n"
                message += f"🏆 إجمالي الأرباح: {format_currency(total_wins)}\n"
                message += f"❌ إجمالي الخسائر: {format_currency(total_losses)}\n"
                message += f"📈 النتيجة الصافية: {format_currency(net_result)}\n"
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    message,
                    reply_markup=Keyboards.betting_history_menu()
                )
            else:
                await update.message.reply_text(
                    message,
                    reply_markup=Keyboards.betting_history_menu()
                )
        finally:
            session.close()
    
    @staticmethod
    async def casino_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ألعاب الكازينو"""
        message = """
🎰 ألعاب الكازينو - ichancy.com

🌟 الألعاب المتاحة:

🎲 **الألعاب السريعة:**
• Crash - تحدي التوقيت المثالي
• Dice - خمن الرقم التالي
• Wheel - عجلة الحظ
• Mines - تجنب الألغام

🃏 **ألعاب الطاولة:**
• Blackjack - 21
• Roulette - الروليت
• Baccarat - الباكارات
• Poker - البوكر

🎰 **ماكينات القمار:**
• Slots - مئات الألعاب
• Megaways - فوز ضخم
• Progressive - جاكبوت متراكم

🎪 **الكازينو المباشر:**
• موزعين حقيقيين
• بث مباشر عالي الجودة
• تفاعل مع اللاعبين

🔗 العب الآن على ichancy.com
        """
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                reply_markup=Keyboards.casino_games_menu()
            )
        else:
            await update.message.reply_text(
                message,
                reply_markup=Keyboards.casino_games_menu()
            )
    
    @staticmethod
    async def sports_betting(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """الرهانات الرياضية"""
        message = """
⚽ الرهانات الرياضية - ichancy.com

🏆 **الرياضات المتاحة:**

⚽ **كرة القدم:**
• الدوريات الأوروبية
• كأس العالم
• دوري أبطال أوروبا
• الدوريات المحلية

🏀 **كرة السلة:**
• NBA
• EuroLeague
• الدوريات المحلية

🎾 **التنس:**
• بطولات الجراند سلام
• ATP & WTA Tours

🏈 **رياضات أخرى:**
• كرة القدم الأمريكية
• الهوكي
• البيسبول
• الملاكمة

📊 **أنواع الرهانات:**
• نتيجة المباراة
• عدد الأهداف
• الهداف الأول
• رهانات مباشرة

🔗 راهن الآن على ichancy.com
        """
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                reply_markup=Keyboards.sports_betting_menu()
            )
        else:
            await update.message.reply_text(
                message,
                reply_markup=Keyboards.sports_betting_menu()
            )
    
    @staticmethod
    async def promotions_bonuses(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """العروض والمكافآت"""
        message = """
🎁 العروض والمكافآت - ichancy.com

🌟 **مكافآت الكازينو:**

💰 **مكافأة الترحيب:**
• 100% على أول إيداع
• حتى 1000 وحدة مجانية
• 50 دورة مجانية

🎰 **مكافآت يومية:**
• مكافأة إعادة التحميل
• دورات مجانية يومية
• كاش باك أسبوعي

⚽ **مكافآت الرياضة:**

🏆 **مكافأة الرهان الأول:**
• رهان مجاني بقيمة 100 وحدة
• تأمين على الرهان الأول

📈 **عروض خاصة:**
• مضاعف الأرباح
• رهانات مجانية
• مكافآت الكومبو

🎯 **برنامج الولاء:**
• نقاط مع كل رهان
• مستويات VIP
• مكافآت حصرية
• مدير حساب شخصي

🔗 احصل على مكافآتك من ichancy.com
        """
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                reply_markup=Keyboards.promotions_menu()
            )
        else:
            await update.message.reply_text(
                message,
                reply_markup=Keyboards.promotions_menu()
            )
    
    @staticmethod
    async def vip_program(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """برنامج VIP"""
        user = db.get_user(update.effective_user.id)
        
        # حساب مستوى VIP بناءً على إجمالي الرهانات
        session = db.get_session()
        try:
            total_bets = session.query(db.func.sum(Transaction.amount)).filter(
                Transaction.user_id == user.id,
                Transaction.transaction_type.in_(['bet_win', 'bet_loss', 'casino_win', 'casino_loss'])
            ).scalar() or 0
            
            # تحديد مستوى VIP
            if total_bets >= 100000:
                vip_level = "💎 Diamond"
                benefits = "• مدير حساب شخصي\n• مكافآت حصرية يومية\n• حدود سحب عالية\n• دعوات لأحداث خاصة"
            elif total_bets >= 50000:
                vip_level = "🥇 Gold"
                benefits = "• مكافآت أسبوعية\n• كاش باك 15%\n• دعم أولوية\n• حدود سحب مرتفعة"
            elif total_bets >= 20000:
                vip_level = "🥈 Silver"
                benefits = "• مكافآت شهرية\n• كاش باك 10%\n• دعم سريع\n• مكافآت إضافية"
            elif total_bets >= 5000:
                vip_level = "🥉 Bronze"
                benefits = "• مكافأة شهرية\n• كاش باك 5%\n• دعم محسن"
            else:
                vip_level = "🆕 مبتدئ"
                benefits = "• مكافأة ترحيب\n• دعم عادي\n• العب أكثر للترقية!"
            
            # حساب النقاط للمستوى التالي
            next_level_points = 0
            if total_bets < 5000:
                next_level_points = 5000 - total_bets
                next_level = "🥉 Bronze"
            elif total_bets < 20000:
                next_level_points = 20000 - total_bets
                next_level = "🥈 Silver"
            elif total_bets < 50000:
                next_level_points = 50000 - total_bets
                next_level = "🥇 Gold"
            elif total_bets < 100000:
                next_level_points = 100000 - total_bets
                next_level = "💎 Diamond"
            else:
                next_level = "أقصى مستوى"
                next_level_points = 0
            
            message = f"""
👑 برنامج VIP - ichancy.com

🏆 **مستواك الحالي:** {vip_level}
💰 **إجمالي رهاناتك:** {format_currency(total_bets)}

🎁 **مزاياك الحالية:**
{benefits}

📈 **التقدم للمستوى التالي:**
"""
            
            if next_level_points > 0:
                message += f"🎯 المستوى التالي: {next_level}\n"
                message += f"💪 تحتاج: {format_currency(next_level_points)} رهان إضافي\n"
            else:
                message += "🏆 لقد وصلت لأقصى مستوى!\n"
            
            message += f"""

🌟 **كيفية كسب النقاط:**
• كل رهان = نقاط VIP
• العب أكثر = مستوى أعلى
• مستوى أعلى = مزايا أكثر

🔗 ارتقِ بمستواك على ichancy.com
            """
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    message,
                    reply_markup=Keyboards.vip_program_menu()
                )
            else:
                await update.message.reply_text(
                    message,
                    reply_markup=Keyboards.vip_program_menu()
                )
        finally:
            session.close()
    
    @staticmethod
    async def live_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """الدعم المباشر"""
        message = """
💬 الدعم المباشر - ichancy.com

🕐 **متاح 24/7**

📞 **طرق التواصل:**

💬 **الدردشة المباشرة:**
• متاح على الموقع
• رد فوري
• دعم متعدد اللغات

📧 **البريد الإلكتروني:**
• support@ichancy.com
• رد خلال ساعة

📱 **التليجرام:**
• @ichancy_support
• دعم سريع

🔗 **الموقع الرسمي:**
• ichancy.com
• قسم المساعدة الشامل

❓ **الأسئلة الشائعة:**
• كيفية الإيداع والسحب
• قوانين الألعاب
• شروط المكافآت
• حل المشاكل التقنية

🛡️ **الأمان والخصوصية:**
• تشفير SSL
• حماية البيانات
• لعب مسؤول

🔗 تواصل معنا على ichancy.com
        """
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                reply_markup=Keyboards.support_menu()
            )
        else:
            await update.message.reply_text(
                message,
                reply_markup=Keyboards.support_menu()
            )
    
    @staticmethod
    async def open_ichancy_website(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """فتح موقع ichancy"""
        message = """
🌐 موقع ichancy.com

🔗 **الرابط الرسمي:**
https://www.ichancy.com/

🎯 **ما ستجده:**
• ألعاب كازينو متنوعة
• رهانات رياضية شاملة
• مكافآت وعروض حصرية
• دعم فني متميز

🎁 **عروض خاصة لمستخدمي البوت:**
• مكافأة ترحيب مضاعفة
• رهانات مجانية
• كاش باك إضافي

⚡ **ابدأ اللعب الآن:**
1. اضغط على الرابط أعلاه
2. سجل حسابك
3. اربط حسابك بالبوت
4. احصل على مكافآتك

🔒 **آمن ومرخص بالكامل**
        """
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                reply_markup=Keyboards.website_menu()
            )
        else:
            await update.message.reply_text(
                message,
                reply_markup=Keyboards.website_menu()
            )
    
    @staticmethod
    async def daily_jackpot_draw(context: ContextTypes.DEFAULT_TYPE):
        """سحب الجاكبوت اليومي (مجدول)"""
        session = db.get_session()
        try:
            # الحصول على قيمة الجاكبوت
            jackpot_amount = session.query(db.func.sum(Transaction.amount)).filter(
                Transaction.transaction_type == 'jackpot_contribution',
                Transaction.status == 'completed'
            ).scalar() or 0
            
            if jackpot_amount < Config.MIN_JACKPOT:
                return  # لا يوجد جاكبوت كافي
            
            # الحصول على جميع المشاركين في الجاكبوت
            participants = session.query(User).join(Transaction).filter(
                Transaction.transaction_type == 'jackpot_contribution',
                Transaction.created_at >= datetime.now() - timedelta(days=1)
            ).distinct().all()
            
            if not participants:
                return  # لا يوجد مشاركين
            
            # اختيار فائز عشوائي
            winner = random.choice(participants)
            
            # إضافة الجاكبوت للفائز
            winner.balance += jackpot_amount
            
            # تسجيل الفوز
            win_transaction = Transaction(
                user_id=winner.id,
                transaction_type='jackpot_win',
                amount=-jackpot_amount,  # سالب لأنه خرج من الجاكبوت
                status='completed',
                description=f'فوز بالجاكبوت اليومي'
            )
            session.add(win_transaction)
            
            # إعادة تعيين مساهمات الجاكبوت
            session.query(Transaction).filter(
                Transaction.transaction_type == 'jackpot_contribution'
            ).update({'status': 'processed'})
            
            session.commit()
            
            # إشعار الفائز
            try:
                await context.bot.send_message(
                    chat_id=winner.telegram_id,
                    text=f"🎉 مبروك! لقد فزت بالجاكبوت!\n💰 المبلغ: {format_currency(jackpot_amount)}\n🎲 تم إضافة المبلغ لرصيدك"
                )
            except TelegramError:
                logger.warning(f"لا يمكن إرسال إشعار الفوز للمستخدم {winner.telegram_id}")
            
            # إشعار عام للإدمن
            if Config.ADMIN_IDS:
                try:
                    await context.bot.send_message(
                        chat_id=Config.ADMIN_IDS[0],
                        text=f"🎲 سحب الجاكبوت اليومي\n🏆 الفائز: {get_user_display_name(winner)}\n💰 المبلغ: {format_currency(jackpot_amount)}"
                    )
                except TelegramError:
                    logger.warning("لا يمكن إرسال إشعار الجاكبوت للإدمن")
            
            logger.info(f"تم سحب الجاكبوت: الفائز {winner.telegram_id}, المبلغ {jackpot_amount}")
            
        except Exception as e:
            logger.error(f"خطأ في سحب الجاكبوت: {str(e)}")
            session.rollback()
        finally:
            session.close()
    
    @staticmethod
    async def add_jackpot_contribution(user_id, bet_amount):
        """إضافة مساهمة في الجاكبوت"""
        contribution = bet_amount * Config.JACKPOT_CONTRIBUTION_RATE
        
        session = db.get_session()
        try:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if user:
                contribution_transaction = Transaction(
                    user_id=user.id,
                    transaction_type='jackpot_contribution',
                    amount=contribution,
                    status='completed',
                    description=f'مساهمة في الجاكبوت من رهان {format_currency(bet_amount)}'
                )
                session.add(contribution_transaction)
                session.commit()
                
                logger.info(f"تمت إضافة مساهمة جاكبوت: المستخدم {user_id}, المبلغ {contribution}")
        except Exception as e:
            logger.error(f"خطأ في إضافة مساهمة الجاكبوت: {str(e)}")
            session.rollback()
        finally:
            session.close()

