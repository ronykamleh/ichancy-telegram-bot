"""
قاعدة البيانات للبوت التليجرام
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid

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
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # العلاقات
    transactions = relationship("Transaction", back_populates="user")
    sent_gifts = relationship("Gift", foreign_keys="Gift.sender_id", back_populates="sender")
    received_gifts = relationship("Gift", foreign_keys="Gift.receiver_id", back_populates="receiver")

class Transaction(Base):
    """جدول المعاملات المالية"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # deposit, withdraw, referral, gift
    amount = Column(Float, nullable=False)
    method = Column(String(50))  # syriatel_cash, bank, usdt
    status = Column(String(20), default='pending')  # pending, completed, failed
    description = Column(Text)
    admin_notes = Column(Text)
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

class AdminMessage(Base):
    """جدول رسائل الإدمن"""
    __tablename__ = 'admin_messages'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    replied_at = Column(DateTime)
    reply_message = Column(Text)

class DatabaseManager:
    """مدير قاعدة البيانات"""
    
    def __init__(self, database_url="sqlite:///telegram_bot.db"):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
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
            return session.query(User).filter(User.telegram_id == str(telegram_id)).first()
        finally:
            session.close()
            
    def update_user_balance(self, telegram_id, amount, transaction_type="manual", description=""):
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
                    status="completed",
                    description=description
                )
                session.add(transaction)
                session.commit()
                return True
            return False
        finally:
            session.close()



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
    placed_at = Column(DateTime, default=datetime.utcnow)
    settled_at = Column(DateTime)
    
    # العلاقات
    user = relationship("User")

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
    user = relationship("User")
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
    user = relationship("User")

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

class VIPLevel(Base):
    """جدول مستويات VIP"""
    __tablename__ = 'vip_levels'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    level_name = Column(String(50), nullable=False)
    total_bets = Column(Float, default=0.0)
    total_deposits = Column(Float, default=0.0)
    cashback_earned = Column(Float, default=0.0)
    level_achieved_at = Column(DateTime, default=datetime.utcnow)
    
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

