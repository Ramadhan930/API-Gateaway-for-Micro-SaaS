import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from . import models, schemas, utils

# ==========================================
# USER MANAGEMENT SYSTEM
# ==========================================

def create_user(db: Session, user: schemas.UserCreate):
    """Mendaftarkan user baru dengan hashing password otomatis."""
    hashed_pwd = utils.hash_password(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_pwd 
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    """Sistem verifikasi login: Mencocokkan email & hash password."""
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not utils.verify_password(password, user.password_hash):
        return False
    return user

# ==========================================
# EVENT MANAGEMENT SYSTEM
# ==========================================

def create_event(db: Session, event: schemas.EventCreate):
    """Membuat event baru dan inisialisasi kursi yang tersedia."""
    db_event = models.Event(
        **event.model_dump(),
        available_seats=event.total_capacity
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_all_events(db: Session):
    """Mengambil list semua event yang tersedia."""
    return db.query(models.Event).all()

# ==========================================
# TICKETING & TRANSACTION SYSTEM
# ==========================================

def process_ticket_purchase(db: Session, event_id: int, user_id: int):
    """
    Sistem Pembelian Tiket Utama.
    Menggunakan ATOMIC UPDATE untuk mencegah overbooking.
    """
    # 1. Validasi Keberadaan Resource
    event = db.query(models.Event).get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event tidak ditemukan.")

    # 2. Atomic Update: Kurangi stok hanya jika stok > 0
    # Ini sangat krusial untuk mencegah 2 orang dapat 1 tiket terakhir.
    updated_rows = db.query(models.Event).filter(
        models.Event.id == event_id,
        models.Event.available_seats > 0
    ).update({"available_seats": models.Event.available_seats - 1})

    if not updated_rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Maaf, tiket sudah habis terjual!"
        )

    # 3. Buat Booking dengan masa berlaku (Expired)
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

def confirm_payment(db: Session, booking_id: int):
    """Sistem Konfirmasi: Mengubah status PENDING menjadi PAID."""
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking ID salah.")
    
    if booking.status != "PENDING":
        return {"message": f"Status booking saat ini adalah: {booking.status}"}

    booking.status = "PAID"
    db.commit()
    db.refresh(booking)
    print(f"--- LOG: Payment Success for Booking #{booking_id} ---")
    return booking

# ==========================================
# AUTOMATION & BACKGROUND SYSTEM
# ==========================================

def cancel_expired_booking(db: Session, booking_id: int):
    """
    Sistem Cleanup Otomatis.
    Membatalkan booking yang tidak dibayar & mengembalikan stok kursi.
    """
    time.sleep(30) # Delay simulasi masa tunggu bayar
    
    db.expire_all() # Ambil data paling fresh dari database
    booking = db.query(models.Booking).get(booking_id)
    
    if booking and booking.status == "PENDING":
        booking.status = "EXPIRED"
        
        # Kembalikan kursi yang tadi sudah sempat 'dipesan'
        db.query(models.Event).filter(
            models.Event.id == booking.event_id
        ).update({"available_seats": models.Event.available_seats + 1})
            
        db.commit()
        print(f"--- LOG: Booking #{booking_id} EXPIRED. Stock recovered. ---")
    else:
        print(f"--- LOG: Booking #{booking_id} safe (Paid or handled). ---")