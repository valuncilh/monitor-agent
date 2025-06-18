from sqlalchemy import (
    create_engine, Column, Integer, String,
    ForeignKey, DateTime, Float, BigInteger, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://monitoring:monitoring@localhost:5432/monitoring")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id         = Column(Integer, primary_key=True, index=True)
    username   = Column(String, unique=True, nullable=False)
    full_name  = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    devices    = relationship("Device", back_populates="owner", cascade="all, delete")

class Device(Base):
    __tablename__ = "devices"
    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_name = Column(String, nullable=False)
    device_id   = Column(String, unique=True, nullable=False, index=True)
    created_at  = Column(DateTime, server_default=func.now())
    owner       = relationship("User", back_populates="devices")
    metrics     = relationship("Metric", back_populates="device", cascade="all, delete")

class Metric(Base):
    __tablename__ = "metrics"
    id            = Column(Integer, primary_key=True, index=True)
    device_id     = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    timestamp     = Column(DateTime, nullable=False)
    cpu_percent   = Column(Float, nullable=False)
    ram_percent   = Column(Float, nullable=False)
    disk_percent  = Column(Float, nullable=False)
    net_in_bytes  = Column(BigInteger, nullable=False)
    net_out_bytes = Column(BigInteger, nullable=False)
    device        = relationship("Device", back_populates="metrics")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 