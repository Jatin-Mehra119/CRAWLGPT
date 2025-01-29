# crawlgpt/src/crawlgpt/core/database.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from passlib.context import CryptContext
import os

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password_hash = Column(String(60))
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    chats = relationship("ChatHistory", back_populates="user")

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(Text)
    role = Column(String(20))  # 'user' or 'assistant'
    context = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="chats")

engine = create_engine(os.getenv('DATABASE_URL', 'sqlite:///crawlgpt.db'))
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

# Database operations
def create_user(username: str, password: str, email: str):
    with Session() as session:
        if session.query(User).filter(User.username == username).first():
            return False
        hashed = pwd_context.hash(password)
        user = User(username=username, password_hash=hashed, email=email)
        session.add(user)
        session.commit()
    return True

def authenticate_user(username: str, password: str):
    with Session() as session:
        user = session.query(User).filter(User.username == username).first()
        if user and pwd_context.verify(password, user.password_hash):
            return user
    return None

def save_chat_message(user_id: int, message: str, role: str, context: str):
    with Session() as session:
        chat = ChatHistory(
            user_id=user_id,
            message=message,
            role=role,
            context=context
        )
        session.add(chat)
        session.commit()

def get_chat_history(user_id: int):
    with Session() as session:
        return session.query(ChatHistory).filter(
            ChatHistory.user_id == user_id
        ).order_by(ChatHistory.timestamp).all()
        
def delete_user_chat_history(user_id: int):
    with Session() as session:
        session.query(ChatHistory).filter(
            ChatHistory.user_id == user_id
        ).delete()
        session.commit()
        
def restore_chat_history(user_id: int):
    """Restores chat history from database to session state"""
    with Session() as session:
        history = session.query(ChatHistory).filter(
            ChatHistory.user_id == user_id
        ).order_by(ChatHistory.timestamp).all()
        
    return [{
        "role": msg.role,
        "content": msg.message,
        "context": msg.context,
        "timestamp": msg.timestamp
    } for msg in history]