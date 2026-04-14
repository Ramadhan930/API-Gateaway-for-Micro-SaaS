from sqlalchemy.orm import Session
from . import models, schemas, utils
from datetime import datetime, timedelta
from fastapi import HTTPException


def create_event(db: Session, event: schemas.EventCreate):
    data = event.model_dump()
    db_event = models.Event(
        **event.model_dump(), # Shortcut untuk mengambil semua field dari schema
        available_seats=event.total_capacity
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_all_events(db: Session):
    return db.query(models.Event).all()

def process_ticket_purchase(db: Session, event_id: int, user_id: int):
    # 1. Cek apakah User ada
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan. Silakan register dulu.")

    # 2. Cek apakah Event ada
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event tidak ditemukan.")

    # 3. Lanjutkan proses update stok (Atomic)
    updated_rows = db.query(models.Event).filter(
        models.Event.id == event_id,
        models.Event.available_seats > 0
    ).update({"available_seats": models.Event.available_seats - 1})

    if not updated_rows:
        raise HTTPException(status_code=400, detail="Tiket habis!")

    # 4. Buat record booking
    new_booking = models.Booking(
        user_id=user_id,
        event_id=event_id,
        status="PENDING",
        expires_at=datetime.now() + timedelta(minutes=15)
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

import time
from sqlalchemy.orm import Session
from . import models

def cancel_expired_booking(db: Session, booking_id: int):
    # Tunggu 15 menit (untuk testing, ganti jadi 30 detik saja biar cepat kelihatan hasilnya)
    time.sleep(30) 
    
    # Refresh session agar dapat data terbaru
    db.expire_all()
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    
    # Jika masih PENDING, maka batalkan
    if booking and booking.status == "PENDING":
        booking.status = "EXPIRED"
        
        # Kembalikan stok ke Event
        event = db.query(models.Event).filter(models.Event.id == booking.event_id).first()
        if event:
            event.available_seats += 1
            
        db.commit()
        print(f"--- LOG: Booking {booking_id} hangus. ---")
    else:
        print(f"--- LOG: Booking {booking_id} sudah dibayar. ---")

def confirm_payment(db: Session, booking_id: int):
    # 1. Cari dulu data booking-nya di database
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    
    # 2. Cek apakah datanya ada dan statusnya masih PENDING
    if not booking:
        return {"error": "Booking tidak ditemukan"}
    
    if booking.status == "PENDING":
        booking.status = "PAID" # Ubah jadi PAID
        db.commit()
        db.refresh(booking)
        print(f"--- LOG: Booking {booking_id} SUDAH DIBAYAR. ---")
        return booking
    
    return {"message": "Booking sudah dalam status: " + booking.status}

def create_user(db: Session, user: schemas.UserCreate):
    # Hash password-nya!
    hashed_pwd = utils.hash_password(user.password)
    
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_pwd # Simpan versi aman
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user