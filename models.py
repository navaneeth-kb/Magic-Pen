from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'
    token = Column(String, primary_key=True)
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    viewed_at = Column(DateTime, nullable=True)
    is_viewed = Column(Boolean, default=False)
