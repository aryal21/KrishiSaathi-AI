"""Database models for KrishiSaathi AI: users, farm profiles, chats, claims, mood logs, product verifications."""
import json
import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, ForeignKey, String, Text, Float, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

def utcnow():
    return datetime.now(timezone.utc)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    mobile: Mapped[str] = mapped_column(String(15), unique=True, index=True)
    pin_hash: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    village: Mapped[str] = mapped_column(String(100), default="")
    district: Mapped[str] = mapped_column(String(100), default="")
    state: Mapped[str] = mapped_column(String(100), default="")
    land: Mapped[float] = mapped_column(Float, default=0.0)
    crops: Mapped[str] = mapped_column(Text, default="[]")  # JSON list
    language: Mapped[str] = mapped_column(String(10), default="hi")
    voice: Mapped[bool] = mapped_column(default=False)
    theme: Mapped[str] = mapped_column(String(10), default="auto")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    
    chats: Mapped[list["Chat"]] = relationship(cascade="all, delete-orphan", back_populates="user")
    claims: Mapped[list["InsuranceClaim"]] = relationship(cascade="all, delete-orphan", back_populates="user")
    mood_logs: Mapped[list["MoodLog"]] = relationship(cascade="all, delete-orphan", back_populates="user")
    farm_profile: Mapped["FarmProfile"] = relationship(cascade="all, delete-orphan", uselist=False, back_populates="user")

class FarmProfile(Base):
    __tablename__ = "farm_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    land_size: Mapped[float] = mapped_column(Float, default=0.0)
    main_crops: Mapped[str] = mapped_column(Text, default="[]")
    irrigation_source: Mapped[str] = mapped_column(String(100), default="Rain-fed")
    soil_type: Mapped[str] = mapped_column(String(100), default="Black soil")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    user: Mapped["User"] = relationship(back_populates="farm_profile")

class Chat(Base):
    __tablename__ = "chats"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    messages: Mapped[list["Message"]] = relationship(cascade="all, delete-orphan", order_by="Message.id", back_populates="chat")
    user: Mapped["User"] = relationship(back_populates="chats")

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), index=True)
    role: Mapped[str] = mapped_column(String(15))
    content: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    chat: Mapped["Chat"] = relationship(back_populates="messages")

class InsuranceClaim(Base):
    __tablename__ = "insurance_claims"
    id: Mapped[int] = mapped_column(primary_key=True)
    claim_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    crop: Mapped[str] = mapped_column(String(80))
    survey_number: Mapped[str] = mapped_column(String(80), default="")
    land_acres: Mapped[float] = mapped_column(Float, default=1.0)
    loss_cause: Mapped[str] = mapped_column(String(100))
    loss_percentage: Mapped[int] = mapped_column(Integer, default=50)
    estimated_payout: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(50), default="Submitted - Under Review")
    details_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    user: Mapped["User"] = relationship(back_populates="claims")

class ProductVerification(Base):
    __tablename__ = "product_verifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    batch_no: Mapped[str] = mapped_column(String(80), index=True)
    company: Mapped[str] = mapped_column(String(100))
    product_name: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(50))
    confidence: Mapped[int] = mapped_column(Integer, default=90)
    details_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class MoodLog(Base):
    __tablename__ = "mood_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    mood: Mapped[str] = mapped_column(String(50))
    score: Mapped[int] = mapped_column(Integer, default=5)
    category: Mapped[str] = mapped_column(String(80), default="General")
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    user: Mapped["User"] = relationship(back_populates="mood_logs")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "krishi.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(engine, expire_on_commit=False)

def get_db():
    with SessionLocal() as db:
        yield db

def init_db():
    Base.metadata.create_all(engine)
