"""
ملف الإعدادات للبوت
"""

import os
from typing import Dict, Any

class Config:
    """إعدادات البوت"""
    
    # إعدادات التليجرام
    BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
    
    # إعدادات قاعدة البيانات
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///telegram_bot.db")
    
    # إعدادات الإحالات
    REFERRAL_PERCENTAGE = float(os.getenv("REFERRAL_PERCENTAGE", "10"))  # نسبة الربح من الإحالات
    
    # إعدادات الدفع
    PAYMENT_METHODS = {
        "syriatel_cash": {
            "name": "سيريتل كاش",
            "emoji": "📱",
            "auto_enabled": False,
            "api_config": {}
        },
        "bank": {
            "name": "البنك",
            "emoji": "🏦",
            "auto_enabled": False,
            "api_config": {}
        },
        "usdt": {
            "name": "USDT",
            "emoji": "💰",
            "auto_enabled": False,
            "api_config": {}
        }
    }
    
    # الحد الأدنى والأقصى للمعاملات
    MIN_DEPOSIT = float(os.getenv("MIN_DEPOSIT", "10"))
    MAX_DEPOSIT = float(os.getenv("MAX_DEPOSIT", "10000"))
    MIN_WITHDRAWAL = float(os.getenv("MIN_WITHDRAWAL", "20"))
    MAX_WITHDRAWAL = float(os.getenv("MAX_WITHDRAWAL", "5000"))
    MIN_GIFT = float(os.getenv("MIN_GIFT", "5"))
    
    # رسائل البوت
    MESSAGES = {
        "welcome": """
🎉 أهلاً وسهلاً بك في بوت الدفع الإلكتروني! 

💰 يمكنك من خلال هذا البوت:
• شحن وسحب الرصيد
• الحصول على أرباح من الإحالات
• إهداء الرصيد للأصدقاء
• استخدام أكواد الهدايا

🔗 كود الإحالة الخاص بك: {referral_code}
💵 رصيدك الحالي: {balance} ل.س

اختر من القائمة أدناه:
        """,
        
        "main_menu": """
🏠 القائمة الرئيسية

💵 رصيدك الحالي: {balance} ل.س
👥 عدد إحالاتك: {referral_count}
💰 أرباح الإحالات: {referral_earnings} ل.س

اختر الخدمة المطلوبة:
        """,
        
        "balance_updated": "✅ تم تحديث رصيدك بنجاح!\n💵 الرصيد الجديد: {balance} ل.س",
        "insufficient_balance": "❌ رصيدك غير كافي لإتمام هذه العملية",
        "invalid_amount": "❌ المبلغ المدخل غير صحيح",
        "user_not_found": "❌ المستخدم غير موجود",
        "operation_cancelled": "❌ تم إلغاء العملية",
        "operation_completed": "✅ تم إتمام العملية بنجاح"
    }
    
    # أزرار الواجهة الرئيسية
    MAIN_BUTTONS = [
        [
            {"text": "💌 سحب رصيد من البوت", "callback": "withdraw"},
            {"text": "💌 شحن رصيد في البوت", "callback": "deposit"}
        ],
        [
            {"text": "💰 نظام الإحالات", "callback": "referrals"},
            {"text": "🎁 إهداء رصيد", "callback": "gift_balance"}
        ],
        [
            {"text": "🎁 كود هدية", "callback": "gift_code"},
            {"text": "📧 تواصل معنا", "callback": "contact"}
        ],
        [
            {"text": "📩 رسالة للإدمن", "callback": "message_admin"},
            {"text": "📜 سجل العمليات", "callback": "transactions"}
        ],
        [
            {"text": "📜 سجل الرهانات", "callback": "bets_history"},
            {"text": "🎲 الجاكبوت", "callback": "jackpot"}
        ],
        [
            {"text": "📌 الشروط والأحكام", "callback": "terms"}
        ]
    ]
    
    @classmethod
    def get_payment_methods_buttons(cls):
        """الحصول على أزرار طرق الدفع"""
        buttons = []
        for method_id, method_info in cls.PAYMENT_METHODS.items():
            buttons.append({
                "text": f"{method_info['emoji']} {method_info['name']}",
                "callback": f"payment_{method_id}"
            })
        return buttons


    
    # إعدادات الجاكبوت والألعاب
    MIN_JACKPOT = float(os.getenv("MIN_JACKPOT", "1000"))  # الحد الأدنى لسحب الجاكبوت
    JACKPOT_CONTRIBUTION_RATE = float(os.getenv("JACKPOT_CONTRIBUTION_RATE", "0.01"))  # 1% من كل رهان
    JACKPOT_DRAW_TIME = os.getenv("JACKPOT_DRAW_TIME", "23:59")  # وقت سحب الجاكبوت اليومي
    
    # إعدادات ichancy.com
    ICHANCY_CONFIG = {
        "website_url": "https://www.ichancy.com/",
        "api_base_url": os.getenv("ICHANCY_API_URL", "https://api.ichancy.com/v1"),
        "api_key": os.getenv("ICHANCY_API_KEY", ""),
        "partner_id": os.getenv("ICHANCY_PARTNER_ID", ""),
        "webhook_secret": os.getenv("ICHANCY_WEBHOOK_SECRET", "")
    }
    
    # معلومات الدعم الفني
    SUPPORT_INFO = {
        "phone": os.getenv("SUPPORT_PHONE", "+963912345678"),
        "email": os.getenv("SUPPORT_EMAIL", "support@ichancy.com"),
        "hours": os.getenv("SUPPORT_HOURS", "24/7"),
        "telegram": os.getenv("SUPPORT_TELEGRAM", "@ichancy_support"),
        "website_support": "https://www.ichancy.com/support"
    }
    
    # أنواع الألعاب المدعومة
    GAME_TYPES = {
        "casino": {
            "name": "ألعاب الكازينو",
            "emoji": "🎰",
            "categories": {
                "slots": "ماكينات القمار",
                "table_games": "ألعاب الطاولة", 
                "live_casino": "الكازينو المباشر",
                "fast_games": "الألعاب السريعة"
            }
        },
        "sports": {
            "name": "الرهانات الرياضية",
            "emoji": "⚽",
            "categories": {
                "football": "كرة القدم",
                "basketball": "كرة السلة",
                "tennis": "التنس",
                "other_sports": "رياضات أخرى"
            }
        }
    }
    
    # مستويات VIP
    VIP_LEVELS = {
        "beginner": {
            "name": "🆕 مبتدئ",
            "min_bets": 0,
            "max_bets": 4999,
            "cashback": 0,
            "benefits": ["مكافأة ترحيب", "دعم عادي"]
        },
        "bronze": {
            "name": "🥉 Bronze",
            "min_bets": 5000,
            "max_bets": 19999,
            "cashback": 5,
            "benefits": ["مكافأة شهرية", "كاش باك 5%", "دعم محسن"]
        },
        "silver": {
            "name": "🥈 Silver", 
            "min_bets": 20000,
            "max_bets": 49999,
            "cashback": 10,
            "benefits": ["مكافآت شهرية", "كاش باك 10%", "دعم سريع", "مكافآت إضافية"]
        },
        "gold": {
            "name": "🥇 Gold",
            "min_bets": 50000,
            "max_bets": 99999,
            "cashback": 15,
            "benefits": ["مكافآت أسبوعية", "كاش باك 15%", "دعم أولوية", "حدود سحب مرتفعة"]
        },
        "diamond": {
            "name": "💎 Diamond",
            "min_bets": 100000,
            "max_bets": float('inf'),
            "cashback": 20,
            "benefits": ["مدير حساب شخصي", "مكافآت حصرية يومية", "حدود سحب عالية", "دعوات لأحداث خاصة"]
        }
    }
    
    # رسائل الألعاب
    GAMING_MESSAGES = {
        "jackpot_win": "🎉 مبروك! لقد فزت بالجاكبوت!\n💰 المبلغ: {amount}\n🎲 تم إضافة المبلغ لرصيدك",
        "bet_placed": "🎯 تم وضع الرهان بنجاح\n💰 المبلغ: {amount}\n🎮 اللعبة: {game}",
        "bet_won": "🏆 مبروك! لقد فزت!\n💰 الربح: {amount}\n🎮 اللعبة: {game}",
        "bet_lost": "😔 للأسف لم تفز هذه المرة\n💰 المبلغ: {amount}\n🎮 اللعبة: {game}",
        "vip_upgrade": "🎉 مبروك! تم ترقيتك إلى مستوى {level}\n🎁 استمتع بالمزايا الجديدة!"
    }
    
    # إعدادات الأمان
    SECURITY_CONFIG = {
        "max_daily_withdrawals": int(os.getenv("MAX_DAILY_WITHDRAWALS", "3")),
        "max_daily_deposits": int(os.getenv("MAX_DAILY_DEPOSITS", "10")),
        "withdrawal_cooldown": int(os.getenv("WITHDRAWAL_COOLDOWN", "3600")),  # ثانية
        "require_admin_approval": os.getenv("REQUIRE_ADMIN_APPROVAL", "true").lower() == "true",
        "auto_ban_threshold": int(os.getenv("AUTO_BAN_THRESHOLD", "10"))  # عدد المحاولات الفاشلة
    }
    
    # إعدادات التسجيل
    LOGGING_CONFIG = {
        "level": os.getenv("LOG_LEVEL", "INFO"),
        "file_path": os.getenv("LOG_FILE_PATH", "logs/bot.log"),
        "max_file_size": int(os.getenv("LOG_MAX_FILE_SIZE", "10485760")),  # 10MB
        "backup_count": int(os.getenv("LOG_BACKUP_COUNT", "5"))
    }
    
    @classmethod
    def get_vip_level(cls, total_bets):
        """تحديد مستوى VIP بناءً على إجمالي الرهانات"""
        for level_id, level_info in cls.VIP_LEVELS.items():
            if level_info["min_bets"] <= total_bets <= level_info["max_bets"]:
                return level_id, level_info
        return "beginner", cls.VIP_LEVELS["beginner"]
    
    @classmethod
    def get_next_vip_level(cls, current_level):
        """الحصول على المستوى التالي في VIP"""
        levels = list(cls.VIP_LEVELS.keys())
        try:
            current_index = levels.index(current_level)
            if current_index < len(levels) - 1:
                next_level = levels[current_index + 1]
                return next_level, cls.VIP_LEVELS[next_level]
        except ValueError:
            pass
        return None, None

