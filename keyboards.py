"""
لوحات المفاتيح للبوت
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from config import Config

class Keyboards:
    """فئة لوحات المفاتيح"""
    
    @staticmethod
    def main_menu():
        """لوحة المفاتيح الرئيسية"""
        keyboard = []
        for row in Config.MAIN_BUTTONS:
            button_row = []
            for button in row:
                button_row.append(InlineKeyboardButton(
                    text=button["text"],
                    callback_data=button["callback"]
                ))
            keyboard.append(button_row)
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def payment_methods(operation_type="deposit"):
        """لوحة مفاتيح طرق الدفع"""
        keyboard = []
        methods = Config.get_payment_methods_buttons()
        
        for method in methods:
            keyboard.append([InlineKeyboardButton(
                text=method["text"],
                callback_data=f"{operation_type}_{method['callback'].split('_')[1]}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirm_transaction(transaction_id):
        """لوحة تأكيد المعاملة"""
        keyboard = [
            [
                InlineKeyboardButton("✅ تأكيد", callback_data=f"confirm_{transaction_id}"),
                InlineKeyboardButton("❌ إلغاء", callback_data=f"cancel_{transaction_id}")
            ],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_panel():
        """لوحة تحكم الإدمن"""
        keyboard = [
            [
                InlineKeyboardButton("💰 إضافة رصيد", callback_data="admin_add_balance"),
                InlineKeyboardButton("💸 خصم رصيد", callback_data="admin_deduct_balance")
            ],
            [
                InlineKeyboardButton("📊 إحصائيات", callback_data="admin_stats"),
                InlineKeyboardButton("📜 سجل المعاملات", callback_data="admin_transactions")
            ],
            [
                InlineKeyboardButton("🎁 إنشاء كود هدية", callback_data="admin_create_gift_code"),
                InlineKeyboardButton("📧 الرسائل", callback_data="admin_messages")
            ],
            [
                InlineKeyboardButton("👥 قائمة المستخدمين", callback_data="admin_users"),
                InlineKeyboardButton("⚙️ الإعدادات", callback_data="admin_settings")
            ],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_to_main():
        """زر العودة للقائمة الرئيسية"""
        keyboard = [[InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def cancel_operation():
        """زر إلغاء العملية"""
        keyboard = [
            [InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_operation")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def referral_menu():
        """قائمة الإحالات"""
        keyboard = [
            [InlineKeyboardButton("📊 إحصائيات الإحالات", callback_data="referral_stats")],
            [InlineKeyboardButton("🔗 مشاركة رابط الإحالة", callback_data="share_referral")],
            [InlineKeyboardButton("💰 سحب أرباح الإحالات", callback_data="withdraw_referral_earnings")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def transaction_history_menu():
        """قائمة سجل المعاملات"""
        keyboard = [
            [
                InlineKeyboardButton("💰 الإيداعات", callback_data="history_deposits"),
                InlineKeyboardButton("💸 السحوبات", callback_data="history_withdrawals")
            ],
            [
                InlineKeyboardButton("🎁 الهدايا", callback_data="history_gifts"),
                InlineKeyboardButton("👥 الإحالات", callback_data="history_referrals")
            ],
            [InlineKeyboardButton("📊 جميع المعاملات", callback_data="history_all")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def pagination(current_page, total_pages, callback_prefix):
        """أزرار التنقل بين الصفحات"""
        keyboard = []
        
        if total_pages > 1:
            nav_buttons = []
            
            if current_page > 1:
                nav_buttons.append(InlineKeyboardButton("⬅️ السابق", 
                                                      callback_data=f"{callback_prefix}_page_{current_page-1}"))
            
            nav_buttons.append(InlineKeyboardButton(f"{current_page}/{total_pages}", 
                                                  callback_data="page_info"))
            
            if current_page < total_pages:
                nav_buttons.append(InlineKeyboardButton("➡️ التالي", 
                                                      callback_data=f"{callback_prefix}_page_{current_page+1}"))
            
            keyboard.append(nav_buttons)
        
        keyboard.append([InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def contact_menu():
        """قائمة التواصل"""
        keyboard = [
            [InlineKeyboardButton("📧 إرسال رسالة للإدمن", callback_data="send_admin_message")],
            [InlineKeyboardButton("📞 معلومات التواصل", callback_data="contact_info")],
            [InlineKeyboardButton("❓ الأسئلة الشائعة", callback_data="faq")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)


    
    @staticmethod
    def jackpot_menu():
        """قائمة الجاكبوت"""
        keyboard = [
            [InlineKeyboardButton("🎲 معلومات الجاكبوت", callback_data="jackpot_info")],
            [InlineKeyboardButton("🏆 آخر الفائزين", callback_data="jackpot_winners")],
            [InlineKeyboardButton("🌐 العب على ichancy.com", callback_data="open_ichancy")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def betting_history_menu():
        """قائمة سجل الرهانات"""
        keyboard = [
            [
                InlineKeyboardButton("🎰 رهانات الكازينو", callback_data="casino_bets_history"),
                InlineKeyboardButton("⚽ الرهانات الرياضية", callback_data="sports_bets_history")
            ],
            [
                InlineKeyboardButton("🏆 الأرباح", callback_data="wins_history"),
                InlineKeyboardButton("❌ الخسائر", callback_data="losses_history")
            ],
            [InlineKeyboardButton("📊 إحصائيات شاملة", callback_data="betting_stats")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def casino_games_menu():
        """قائمة ألعاب الكازينو"""
        keyboard = [
            [
                InlineKeyboardButton("🎲 الألعاب السريعة", callback_data="fast_games"),
                InlineKeyboardButton("🃏 ألعاب الطاولة", callback_data="table_games")
            ],
            [
                InlineKeyboardButton("🎰 ماكينات القمار", callback_data="slot_games"),
                InlineKeyboardButton("🎪 الكازينو المباشر", callback_data="live_casino")
            ],
            [InlineKeyboardButton("🌐 العب على ichancy.com", callback_data="open_ichancy")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def sports_betting_menu():
        """قائمة الرهانات الرياضية"""
        keyboard = [
            [
                InlineKeyboardButton("⚽ كرة القدم", callback_data="football_betting"),
                InlineKeyboardButton("🏀 كرة السلة", callback_data="basketball_betting")
            ],
            [
                InlineKeyboardButton("🎾 التنس", callback_data="tennis_betting"),
                InlineKeyboardButton("🏈 رياضات أخرى", callback_data="other_sports")
            ],
            [InlineKeyboardButton("📊 الرهانات المباشرة", callback_data="live_betting")],
            [InlineKeyboardButton("🌐 راهن على ichancy.com", callback_data="open_ichancy")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def promotions_menu():
        """قائمة العروض والمكافآت"""
        keyboard = [
            [
                InlineKeyboardButton("🎰 مكافآت الكازينو", callback_data="casino_bonuses"),
                InlineKeyboardButton("⚽ مكافآت الرياضة", callback_data="sports_bonuses")
            ],
            [
                InlineKeyboardButton("💰 مكافأة الترحيب", callback_data="welcome_bonus"),
                InlineKeyboardButton("🔄 مكافآت يومية", callback_data="daily_bonuses")
            ],
            [InlineKeyboardButton("👑 برنامج VIP", callback_data="vip_program")],
            [InlineKeyboardButton("🌐 احصل على مكافآتك", callback_data="open_ichancy")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def vip_program_menu():
        """قائمة برنامج VIP"""
        keyboard = [
            [InlineKeyboardButton("📊 مستواي الحالي", callback_data="my_vip_level")],
            [InlineKeyboardButton("🎁 مزايا VIP", callback_data="vip_benefits")],
            [InlineKeyboardButton("📈 كيفية الترقية", callback_data="vip_upgrade")],
            [InlineKeyboardButton("🌐 ارتقِ بمستواك", callback_data="open_ichancy")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def support_menu():
        """قائمة الدعم"""
        keyboard = [
            [InlineKeyboardButton("💬 الدردشة المباشرة", callback_data="live_chat")],
            [InlineKeyboardButton("📧 البريد الإلكتروني", callback_data="email_support")],
            [InlineKeyboardButton("❓ الأسئلة الشائعة", callback_data="faq_support")],
            [InlineKeyboardButton("🌐 الدعم على الموقع", callback_data="open_ichancy")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def website_menu():
        """قائمة الموقع"""
        keyboard = [
            [InlineKeyboardButton("🌐 فتح ichancy.com", url="https://www.ichancy.com/")],
            [InlineKeyboardButton("📱 تطبيق الجوال", callback_data="mobile_app")],
            [InlineKeyboardButton("🎁 العروض الحصرية", callback_data="exclusive_offers")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def user_management_menu():
        """قائمة إدارة المستخدمين للإدمن"""
        keyboard = [
            [
                InlineKeyboardButton("💰 إضافة رصيد", callback_data="admin_add_balance"),
                InlineKeyboardButton("💸 خصم رصيد", callback_data="admin_deduct_balance")
            ],
            [
                InlineKeyboardButton("ℹ️ معلومات مستخدم", callback_data="admin_user_info"),
                InlineKeyboardButton("🚫 حظر مستخدم", callback_data="admin_ban_user")
            ],
            [
                InlineKeyboardButton("📊 إحصائيات المستخدمين", callback_data="admin_user_stats"),
                InlineKeyboardButton("📧 إرسال رسالة جماعية", callback_data="admin_broadcast")
            ],
            [InlineKeyboardButton("🔙 العودة للوحة الإدمن", callback_data="admin_panel")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def pending_transactions_menu():
        """قائمة المعاملات المعلقة للإدمن"""
        keyboard = [
            [
                InlineKeyboardButton("✅ الموافقة على معاملة", callback_data="admin_approve_transaction"),
                InlineKeyboardButton("❌ رفض معاملة", callback_data="admin_reject_transaction")
            ],
            [InlineKeyboardButton("📊 عرض جميع المعاملات المعلقة", callback_data="admin_view_pending")],
            [InlineKeyboardButton("🔙 العودة للوحة الإدمن", callback_data="admin_panel")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_back_menu():
        """زر العودة للوحة الإدمن"""
        keyboard = [[InlineKeyboardButton("🔙 العودة للوحة الإدمن", callback_data="admin_panel")]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def cancel_admin_operation():
        """زر إلغاء عملية الإدمن"""
        keyboard = [
            [InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_admin_operation")],
            [InlineKeyboardButton("🔙 العودة للوحة الإدمن", callback_data="admin_panel")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def contact_back_menu():
        """زر العودة لقائمة التواصل"""
        keyboard = [[InlineKeyboardButton("🔙 العودة لقائمة التواصل", callback_data="contact")]]
        return InlineKeyboardMarkup(keyboard)

