"""
قاعدة البيانات المحدثة للبوت التليجرام - ichancy.com
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid
import os

Base = declarative_base()

class User(Base):
    """جدول المستخدمين"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(50), unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    balance = Column(Float, default=0.0)
    referral_code = Column(String(20), unique=True)
    referred_by = Column(String(20))
    referral_count = Column(Integer, default=0)
    referral_earnings = Column(Float, default=0.0)
    total_bets = Column(Float, default=0.0)
    total_wins = Column(Float, default=0.0)
    vip_level = Column(String(20), default='beginner')
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # العلاقات
    transactions = relationship("Transaction", back_populates="user")
    sent_gifts = relationship("Gift", foreign_keys="Gift.sender_id", back_populates="sender")
    received_gifts = relationship("Gift", foreign_keys="Gift.receiver_id", back_populates="receiver")
    bets = relationship("Bet", back_populates="user")
    jackpot_entries = relationship("JackpotEntry", back_populates="user")
    jackpot_wins = relationship("JackpotWin", back_populates="user")

class Transaction(Base):
    """جدول المعاملات المالية"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    transaction_type = Column(String(30), nullable=False)  # deposit, withdraw, referral, gift, bet_win, bet_loss, jackpot_win, jackpot_contribution
    amount = Column(Float, nullable=False)
    method = Column(String(50))  # syriatel_cash, bank, usdt
    status = Column(String(20), default='pending')  # pending, completed, failed, cancelled
    description = Column(Text)
    admin_notes = Column(Text)
    external_transaction_id = Column(String(100))  # معرف المعاملة الخارجية
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # العلاقات
    user = relationship("User", back_populates="transactions")

class Gift(Base):
    """جدول الهدايا بين المستخدمين"""
    __tablename__ = 'gifts'
    
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # العلاقات
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_gifts")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_gifts")

class GiftCode(Base):
    """جدول أكواد الهدايا"""
    __tablename__ = 'gift_codes'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    max_uses = Column(Integer, default=1)
    current_uses = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class GiftCodeUsage(Base):
    """جدول استخدام أكواد الهدايا"""
    __tablename__ = 'gift_code_usage'
    
    id = Column(Integer, primary_key=True)
    code_id = Column(Integer, ForeignKey('gift_codes.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    used_at = Column(DateTime, default=datetime.utcnow)

class Bet(Base):
    """جدول الرهانات"""
    __tablename__ = 'bets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    game_type = Column(String(50), nullable=False)  # casino, sports
    game_category = Column(String(50))  # slots, football, etc.
    game_name = Column(String(100))
    bet_amount = Column(Float, nullable=False)
    potential_win = Column(Float)
    actual_win = Column(Float, default=0.0)
    odds = Column(Float)
    status = Column(String(20), default='pending')  # pending, won, lost, cancelled
    bet_details = Column(Text)  # JSON string with bet details
    ichancy_bet_id = Column(String(100))  # معرف الرهان في ichancy
    placed_at = Column(DateTime, default=datetime.utcnow)
    settled_at = Column(DateTime)
    
    # العلاقات
    user = relationship("User", back_populates="bets")

class JackpotEntry(Base):
    """جدول مشاركات الجاكبوت"""
    __tablename__ = 'jackpot_entries'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    bet_id = Column(Integer, ForeignKey('bets.id'))
    contribution_amount = Column(Float, nullable=False)
    jackpot_pool_id = Column(String(50))  # معرف مجموعة الجاكبوت
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # العلاقات
    user = relationship("User", back_populates="jackpot_entries")
    bet = relationship("Bet")

class JackpotWin(Base):
    """جدول أرباح الجاكبوت"""
    __tablename__ = 'jackpot_wins'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    jackpot_pool_id = Column(String(50), nullable=False)
    win_amount = Column(Float, nullable=False)
    total_pool = Column(Float, nullable=False)
    participants_count = Column(Integer, default=0)
    win_date = Column(DateTime, default=datetime.utcnow)
    
    # العلاقات
    user = relationship("User", back_populates="jackpot_wins")

class GameSession(Base):
    """جدول جلسات الألعاب"""
    __tablename__ = 'game_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_id = Column(String(100), unique=True)
    game_type = Column(String(50), nullable=False)
    start_balance = Column(Float, nullable=False)
    end_balance = Column(Float)
    total_bets = Column(Float, default=0.0)
    total_wins = Column(Float, default=0.0)
    session_duration = Column(Integer)  # بالثواني
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    
    # العلاقات
    user = relationship("User")

class Promotion(Base):
    """جدول العروض والمكافآت"""
    __tablename__ = 'promotions'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    promo_type = Column(String(50), nullable=False)  # welcome, deposit, cashback, etc.
    bonus_amount = Column(Float)
    bonus_percentage = Column(Float)
    min_deposit = Column(Float)
    max_bonus = Column(Float)
    wagering_requirement = Column(Float)
    is_active = Column(Boolean, default=True)
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserPromotion(Base):
    """جدول استخدام المستخدمين للعروض"""
    __tablename__ = 'user_promotions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    promotion_id = Column(Integer, ForeignKey('promotions.id'), nullable=False)
    bonus_amount = Column(Float, nullable=False)
    wagering_completed = Column(Float, default=0.0)
    wagering_required = Column(Float, nullable=False)
    status = Column(String(20), default='active')  # active, completed, expired
    claimed_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # العلاقات
    user = relationship("User")
    promotion = relationship("Promotion")

class Message(Base):
    """جدول الرسائل بين المستخدمين والإدمن"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    admin_id = Column(Integer, ForeignKey('users.id'))
    message_type = Column(String(20), nullable=False)  # user_to_admin, admin_to_user
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # العلاقات
    user = relationship("User", foreign_keys=[user_id])
    admin = relationship("User", foreign_keys=[admin_id])

class SystemLog(Base):
    """جدول سجلات النظام"""
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True)
    log_type = Column(String(50), nullable=False)  # error, warning, info
    module = Column(String(100))
    message = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    ip_address = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # العلاقات
    user = relationship("User")

class DatabaseManager:
    """مدير قاعدة البيانات"""
    
    def __init__(self, database_url=None):
        if database_url is None:
            database_url = os.getenv("DATABASE_URL", "sqlite:///data/telegram_bot.db")
        
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.func = func  # إضافة func للاستعلامات المتقدمة
        
    def create_tables(self):
        """إنشاء الجداول"""
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self):
        """الحصول على جلسة قاعدة البيانات"""
        return self.SessionLocal()
        
    def generate_referral_code(self):
        """توليد كود إحالة فريد"""
        return str(uuid.uuid4())[:8].upper()
        
    def create_user(self, telegram_id, username=None, first_name=None, last_name=None):
        """إنشاء مستخدم جديد"""
        session = self.get_session()
        try:
            # التحقق من وجود المستخدم
            existing_user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
            if existing_user:
                return existing_user
                
            # إنشاء مستخدم جديد
            referral_code = self.generate_referral_code()
            while session.query(User).filter(User.referral_code == referral_code).first():
                referral_code = self.generate_referral_code()
                
            user = User(
                telegram_id=str(telegram_id),
                username=username,
                first_name=first_name,
                last_name=last_name,
                referral_code=referral_code
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        finally:
            session.close()
            
    def get_user(self, telegram_id):
        """الحصول على مستخدم بواسطة telegram_id"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
            if user:
                # تحديث آخر نشاط
                user.last_activity = datetime.utcnow()
                session.commit()
            return user
        finally:
            session.close()
            
    def update_user_balance(self, telegram_id, amount, transaction_type="manual", description="", method=None):
        """تحديث رصيد المستخدم"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
            if user:
                user.balance += amount
                
                # إضافة معاملة
                transaction = Transaction(
                    user_id=user.id,
                    transaction_type=transaction_type,
                    amount=amount,
                    method=method,
                    status="completed",
                    description=description
                )
                session.add(transaction)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def add_bet(self, user_id, game_type, bet_amount, game_category=None, game_name=None, odds=None, bet_details=None):
        """إضافة رهان جديد"""
        session = self.get_session()
        try:
            bet = Bet(
                user_id=user_id,
                game_type=game_type,
                game_category=game_category,
                game_name=game_name,
                bet_amount=bet_amount,
                odds=odds,
                bet_details=bet_details
            )
            session.add(bet)
            session.commit()
            session.refresh(bet)
            return bet
        finally:
            session.close()
    
    def settle_bet(self, bet_id, status, actual_win=0.0):
        """تسوية الرهان"""
        session = self.get_session()
        try:
            bet = session.query(Bet).filter(Bet.id == bet_id).first()
            if bet:
                bet.status = status
                bet.actual_win = actual_win
                bet.settled_at = datetime.utcnow()
                
                # تحديث رصيد المستخدم إذا فاز
                if status == 'won' and actual_win > 0:
                    user = session.query(User).filter(User.id == bet.user_id).first()
                    if user:
                        user.balance += actual_win
                        user.total_wins += actual_win
                        
                        # إضافة معاملة الفوز
                        transaction = Transaction(
                            user_id=user.id,
                            transaction_type='bet_win',
                            amount=actual_win,
                            status='completed',
                            description=f'فوز في {bet.game_name or bet.game_type}'
                        )
                        session.add(transaction)
                
                # تحديث إجمالي الرهانات
                user = session.query(User).filter(User.id == bet.user_id).first()
                if user:
                    user.total_bets += bet.bet_amount
                
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def add_jackpot_contribution(self, user_id, bet_id, contribution_amount):
        """إضافة مساهمة في الجاكبوت"""
        session = self.get_session()
        try:
            # تحديد معرف مجموعة الجاكبوت (يومي)
            today = datetime.utcnow().date()
            jackpot_pool_id = f"daily_{today.strftime('%Y%m%d')}"
            
            entry = JackpotEntry(
                user_id=user_id,
                bet_id=bet_id,
                contribution_amount=contribution_amount,
                jackpot_pool_id=jackpot_pool_id
            )
            session.add(entry)
            
            # إضافة معاملة المساهمة
            transaction = Transaction(
                user_id=user_id,
                transaction_type='jackpot_contribution',
                amount=contribution_amount,
                status='completed',
                description=f'مساهمة في الجاكبوت اليومي'
            )
            session.add(transaction)
            
            session.commit()
            return True
        finally:
            session.close()
    
    def get_current_jackpot(self):
        """الحصول على قيمة الجاكبوت الحالية"""
        session = self.get_session()
        try:
            today = datetime.utcnow().date()
            jackpot_pool_id = f"daily_{today.strftime('%Y%m%d')}"
            
            total = session.query(func.sum(JackpotEntry.contribution_amount)).filter(
                JackpotEntry.jackpot_pool_id == jackpot_pool_id
            ).scalar() or 0
            
            return total
        finally:
            session.close()
    
    def get_user_betting_stats(self, user_id):
        """الحصول على إحصائيات رهانات المستخدم"""
        session = self.get_session()
        try:
            stats = {
                'total_bets': 0,
                'total_wins': 0,
                'total_losses': 0,
                'win_rate': 0,
                'biggest_win': 0,
                'recent_bets': []
            }
            
            # إجمالي الرهانات
            total_bet_amount = session.query(func.sum(Bet.bet_amount)).filter(
                Bet.user_id == user_id
            ).scalar() or 0
            
            # إجمالي الأرباح
            total_win_amount = session.query(func.sum(Bet.actual_win)).filter(
                Bet.user_id == user_id,
                Bet.status == 'won'
            ).scalar() or 0
            
            # عدد الرهانات الفائزة والخاسرة
            won_bets = session.query(Bet).filter(
                Bet.user_id == user_id,
                Bet.status == 'won'
            ).count()
            
            lost_bets = session.query(Bet).filter(
                Bet.user_id == user_id,
                Bet.status == 'lost'
            ).count()
            
            total_settled_bets = won_bets + lost_bets
            
            # أكبر فوز
            biggest_win = session.query(func.max(Bet.actual_win)).filter(
                Bet.user_id == user_id,
                Bet.status == 'won'
            ).scalar() or 0
            
            # آخر الرهانات
            recent_bets = session.query(Bet).filter(
                Bet.user_id == user_id
            ).order_by(Bet.placed_at.desc()).limit(10).all()
            
            stats.update({
                'total_bets': total_bet_amount,
                'total_wins': total_win_amount,
                'total_losses': total_bet_amount - total_win_amount,
                'win_rate': (won_bets / total_settled_bets * 100) if total_settled_bets > 0 else 0,
                'biggest_win': biggest_win,
                'recent_bets': recent_bets
            })
            
            return stats
        finally:
            session.close()
    
    def update_vip_level(self, user_id):
        """تحديث مستوى VIP للمستخدم"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                from config import Config
                level_id, level_info = Config.get_vip_level(user.total_bets)
                
                old_level = user.vip_level
                user.vip_level = level_id
                
                session.commit()
                
                # إرجاع True إذا تم الترقية
                return old_level != level_id
            return False
        finally:
            session.close()
    
    def log_system_event(self, log_type, module, message, user_id=None):
        """تسجيل حدث في النظام"""
        session = self.get_session()
        try:
            log = SystemLog(
                log_type=log_type,
                module=module,
                message=message,
                user_id=user_id
            )
            session.add(log)
            session.commit()
        finally:
            session.close()

