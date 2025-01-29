# This module provides SQLAlchemy models and database utilities for user management 
# and chat history persistence.

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from passlib.context import CryptContext
import os

# SQLAlchemy models
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    """User model for authentication and chat history tracking.
    
    Attributes:
        id (int): Primary key
        username (str): Unique username, max 50 chars
        password_hash (str): BCrypt hashed password, 60 chars
        email (str): User email, max 100 chars
        created_at (datetime): Account creation timestamp
        chats (relationship): One-to-many relationship to ChatHistory
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password_hash = Column(String(60))
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    chats = relationship("ChatHistory", back_populates="user")

class ChatHistory(Base):
    """ChatHistory model for storing chat messages.
    
    Attributes:
        id (int): Primary key
        user_id (int): Foreign key to User
        message (str): Chat message content
        role (str): Role of the message sender ('user' or 'assistant')
        context (str): Context of the chat message
        timestamp (datetime): Timestamp of the message
        user (relationship): Many-to-one relationship to User
    """
    __tablename__ = 'chat_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(Text)
    role = Column(String(20))  # 'user' or 'assistant'
    context = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="chats")

# Database initialization
engine = create_engine(os.getenv('DATABASE_URL', 'sqlite:///crawlgpt.db'))
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

# Database operations
def create_user(username: str, password: str, email: str):
    """
    Creates a new user in the database
    Args:
        username (str): Username
        password (str): Password
        email (str): Email
    Returns:
        bool: True if user is created, False if username is taken
    """
    with Session() as session:
        if session.query(User).filter(User.username == username).first():
            return False
        hashed = pwd_context.hash(password)
        user = User(username=username, password_hash=hashed, email=email)
        session.add(user)
        session.commit()
    return True

def authenticate_user(username: str, password: str):
    """
    Authenticates a user with a username and password
    Args:
        username (str): Username
        password (str): Password
    Returns:
        User: User object if authentication is successful, None otherwise
    """
    with Session() as session:
        user = session.query(User).filter(User.username == username).first()
        if user and pwd_context.verify(password, user.password_hash):
            return user
    return None

def save_chat_message(user_id: int, message: str, role: str, context: str):
    """Saves a chat message to the database

    Args:
        user_id (int): User ID
        message (str): Chat message content
        role (str): Role of the message sender ('user' or 'assistant')
        context (str): Context of the chat message

    Returns:
        None
    """
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
    """
    Retrieves chat history for a user
    Args:
        user_id (int): User ID
        
    Returns:
        List[ChatHistory]: List of chat messages
    """
    with Session() as session:
        return session.query(ChatHistory).filter(
            ChatHistory.user_id == user_id
        ).order_by(ChatHistory.timestamp).all()
        
def delete_user_chat_history(user_id: int):
    """Deletes all chat history for a user
    Args:
        user_id (int): User ID
    
    Returns:
        None
    """
    with Session() as session:
        session.query(ChatHistory).filter(
            ChatHistory.user_id == user_id
        ).delete()
        session.commit()
        
def restore_chat_history(user_id: int):
    """Restores chat history from database to session state
    Args:
        user_id (int): User ID
    
    Returns:
        List[Dict]: List of chat messages in the format:
            {
                "role": str,
                "content": str,
                "context": str,
                "timestamp": datetime
            }
        """
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