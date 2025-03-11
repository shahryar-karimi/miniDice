from sqlalchemy import create_engine, Column, Integer, BigInteger, String, DateTime, ForeignKey, func, distinct, case, desc, Float
from sqlalchemy.orm import sessionmaker, relationship, declarative_base


# Define the base for the ORM
Base = declarative_base()

class Player(Base):
    __tablename__ = 'player'
    telegram_id = Column(Integer, primary_key=True)
    telegram_username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    telegram_language_code = Column(String)
    wallet_address = Column(String)
    wallet_insert_dt = Column(DateTime)
    insert_dt = Column(DateTime)

class Prediction(Base):
    __tablename__ = 'prediction'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.telegram_id'))
    insert_dt = Column(DateTime)
    countdown_id = Column(Integer)
    dice_number1 = Column(Integer)
    dice_number2 = Column(Integer)
    slot = Column(Integer)
    is_win = Column(Integer)
    is_active = Column(Integer)
    player_ref = relationship("Player", backref="predictions")

class UserReferral(Base):
    __tablename__ = 'user_referral'
    id = Column(Integer, primary_key=True)
    referrer_id = Column(Integer, ForeignKey('player.telegram_id'))
    referee_id = Column(Integer, ForeignKey('player.telegram_id'))
    insert_dt = Column(DateTime)
    referrer_ref = relationship("Player", backref="referrals", foreign_keys=[referrer_id])
    referee_ref = relationship("Player", backref="referred_by", foreign_keys=[referee_id])

class Asset(Base):
    __tablename__ = 'assets'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.telegram_id'))
    symbol = Column(String)
    balance = Column(BigInteger)
    decimal = Column(Integer)
    master_address = Column(String)
    usd_value = Column(Float)
    price = Column(Float)

class Report(Base):
    __tablename__ = 'report'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, unique=True)
    joined_players = Column(Integer)
    average_joined_players = Column(Float)
    connected_wallets = Column(Integer)
    average_connected_wallets = Column(Float)
    new_wallets_count = Column(Integer)
    referrals = Column(Integer)
    winners = Column(Integer)
    unique_players = Column(Integer)
    players_noref_wallet_connected = Column(Integer)
    unique_wallets_predictions = Column(Integer)
    players_joined_without_referral = Column(Integer)
    bot_blocks = Column(Integer)