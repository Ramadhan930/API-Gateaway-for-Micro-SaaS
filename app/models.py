from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# =========================================================
# SYSTEM 1: USER ACCOUNT MODEL
# =========================================================
class User(Base):
    """Model untuk menyimpan identitas pengguna dan kredensial."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship: Menghubungkan user ke semua booking yang pernah ia buat
    bookings = relationship("Booking", back_populates="user")


# =========================================================
# SYSTEM 2: EVENT & INVENTORY MODEL
# =========================================================
class Event(Base):
    """Model untuk menyimpan data acara dan stok ketersediaan tiket."""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String)
    price = Column(Numeric(12, 2), nullable=False) # Presisi tinggi untuk keuangan
    total_capacity = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)
    event_date = Column(DateTime)

    # Relationship: Menghubungkan event ke daftar booking yang masuk
    bookings = relationship("Booking", back_populates="event")


# =========================================================
# SYSTEM 3: TRANSACTION & BOOKING MODEL
# =========================================================
class Booking(Base):
    """Model transaksi yang menghubungkan User dengan Event (Junction Table)."""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"))
    
    # Status: PENDING, PAID, EXPIRED, CANCELLED
    status = Column(String(20), default="PENDING")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime, nullable=False)

    # Relationships: Mempermudah akses data (Lazy Loading)
    user = relationship("User", back_populates="bookings")
    event = relationship("Event", back_populates="bookings")