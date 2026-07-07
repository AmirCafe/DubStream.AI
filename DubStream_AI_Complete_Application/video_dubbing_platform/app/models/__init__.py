from app.db.session import Base
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
import enum

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    stripe_subscription_id = Column(String, unique=True)
    stripe_customer_id = Column(String)
    status = Column(String)
    current_period_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class Job(Base):
    __tablename__ = "jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    status = Column(String, default="pending")
    progress = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
