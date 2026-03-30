from sqlalchemy import Column, String, Integer, DateTime, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class ProcessingStatus(str, enum.Enum):
    PENDING = "PENDING"
    CLONING = "CLONING"
    PARSING = "PARSING"
    INDEXING = "INDEXING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Repository(Base):
    __tablename__ = "repositories"
    
    id = Column(String, primary_key=True, index=True)
    url = Column(String, index=True)
    name = Column(String)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ScrapedSource(Base):
    __tablename__ = "scraped_sources"
    
    id = Column(String, primary_key=True, index=True)
    repository_id = Column(String, index=True)
    url = Column(String)
    title = Column(String)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
