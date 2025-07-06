from sqlalchemy import create_engine, String, Float, Integer, DateTime, ForeignKey, Text, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from datetime import datetime
from typing import List, Optional
import os
from pathlib import Path

# Database configuration
BASE_DIR = Path(__file__).parent.parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR}/data/app.db"

# Ensure data directory exists
os.makedirs(f"{BASE_DIR}/data", exist_ok=True)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models using SQLAlchemy 2.0+ syntax
class Base(DeclarativeBase):
    pass

# Models
class Category(Base):
    __tablename__ = "categories"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    emoji: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    seed_keyword: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    practicality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    interest_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    contents: Mapped[List["Content"]] = relationship("Content", back_populates="category")
    subcategories: Mapped[List["Subcategory"]] = relationship("Subcategory", back_populates="category")

class Paper(Base):
    __tablename__ = "papers"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    journal: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    publication_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    doi: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    impact_factor: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    citations: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    paper_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality_grade: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    subcategory_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("subcategories.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    contents: Mapped[List["Content"]] = relationship("Content", back_populates="paper")

class Content(Base):
    __tablename__ = "contents"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    category_id: Mapped[str] = mapped_column(String, ForeignKey("categories.id"), nullable=False)
    paper_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("papers.id"), nullable=True)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'shorts', 'article', 'report'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    thinking_process: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    category: Mapped["Category"] = relationship("Category", back_populates="contents")
    paper: Mapped["Paper"] = relationship("Paper", back_populates="contents")


class Subcategory(Base):
    __tablename__ = "subcategories"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    category_id: Mapped[str] = mapped_column(String, ForeignKey("categories.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_effect: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality_grade: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    category: Mapped["Category"] = relationship("Category", back_populates="subcategories")
    papers: Mapped[List["Paper"]] = relationship("Paper", backref="subcategory")

# Database initialization
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at: {DATABASE_URL}")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions for health checks
def check_db_connection():
    """Check if database connection is working"""
    try:
        db = SessionLocal()
        # Try a simple query
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception:
        return False

def get_db_size():
    """Get the size of the database file in bytes"""
    try:
        db_path = Path(DATABASE_URL.replace("sqlite:///", ""))
        if db_path.exists():
            return db_path.stat().st_size
        return 0
    except Exception:
        return 0