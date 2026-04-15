from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# =========================================================
# SYSTEM 1: USER SCHEMAS (Identity & Auth)
# =========================================================

class UserBase(BaseModel):
    """Base schema untuk data umum user."""
    username: str = Field(..., min_length=3, max_length=50, example="yo_madhan")
    email: EmailStr

class UserCreate(UserBase):
    """Schema untuk pendaftaran user baru (mengandung password)."""
    password: str = Field(..., min_length=6, example="rahasia123")

class UserResponse(UserBase):
    """Schema untuk mengirim data user ke client (tanpa password)."""
    id: int
    created_at: datetime

    # Pydantic v2 style untuk ORM compatibility
    model_config = ConfigDict(from_attributes=True)


# =========================================================
# SYSTEM 2: AUTHENTICATION SCHEMAS (Tokens)
# =========================================================

class Token(BaseModel):
    """Format balasan setelah login berhasil."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Data yang tersimpan di dalam 'gelang' JWT (payload)."""
    username: Optional[str] = None


# =========================================================
# SYSTEM 3: EVENT SCHEMAS (Inventory)
# =========================================================

class EventBase(BaseModel):
    """Base schema untuk data dasar acara."""
    title: str = Field(..., example="Konser Tulus Padang")
    description: Optional[str] = Field(None, example="Konser eksklusif di GOR H. Agus Salim")
    price: Decimal = Field(..., gt=0, example=150000.00)
    event_date: datetime

class EventCreate(EventBase):
    """Schema untuk membuat event baru."""
    total_capacity: int = Field(..., gt=0, example=100)

class EventResponse(EventBase):
    """Schema untuk menampilkan data event ke publik."""
    id: int
    available_seats: int
    
    model_config = ConfigDict(from_attributes=True)


# =========================================================
# SYSTEM 4: TRANSACTION SCHEMAS (Booking)
# =========================================================

class BookingResponse(BaseModel):
    """Schema untuk melihat status transaksi."""
    id: int
    user_id: int
    event_id: int
    status: str
    created_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)