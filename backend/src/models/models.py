from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.src.db.database import Base

# ---------- USER MODEL ----------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    research_interests = Column(String, index=True)
    major = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    embeddings = relationship("UserEmbedding", back_populates="user", cascade="all, delete-orphan")
    chatlogs = relationship("ChatLog", back_populates="user", cascade="all, delete-orphan")


class UserEmbedding(Base):
    __tablename__ = "user_embeddings"

    user_id = Column(Integer, ForeignKey("users.id"))
    embedding = Column(ARRAY(Float), nullable=False)

    user = relationship("User", back_populates="embeddings")


# ---------- PROFESSOR MODEL ----------
class Professor(Base):
    __tablename__ = "professors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    department = Column(String, index=True)
    research_areas = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    embeddings = relationship("ProfessorEmbedding", back_populates="professor", cascade="all, delete-orphan")


class ProfessorEmbedding(Base):
    __tablename__ = "professor_embeddings"

    professor_id = Column(Integer, ForeignKey("professors.id"))
    embedding = Column(ARRAY(Float), nullable=False)

    professor = relationship("Professor", back_populates="embeddings")


# ---------- CHAT LOG MODEL ----------
class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    matched_professors = Column(ARRAY(Integer))  # store matched professor IDs
    user = relationship("User", back_populates="chatlogs")
