from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True
        
class EventCreate(BaseModel):
    title: str = Field(..., example="Konser Tulus")
    description: Optional[str] = Field(None, example="Konser eksklusif di Padang")
    price: float = Field(..., gt=0) # gt=0 artinya 'greater than 0' (harga tak boleh 0/minus)
    total_capacity: int = Field(..., gt=0)
    event_date: datetime

class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    price: float
    available_seats: int
    
    class Config:
        from_attributes = True # Ini wajib agar Pydantic bisa baca data dari SQLAlchemy