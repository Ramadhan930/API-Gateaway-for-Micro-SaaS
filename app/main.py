from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import engine, get_db
from fastapi import BackgroundTasks

# Buat tabel otomatis
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Micro-SaaS Ticketing API")

@app.get("/")
def read_root():
    return {"message": "Let's cook? Your API is ready!"}

@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Cek apakah email sudah dipakai
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar!")
    
    # Buat user baru
    new_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=user.password # Untuk sekarang simpan teks biasa, nanti kita buat aman
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/events", response_model=schemas.EventResponse)
def create_event_endpoint(event: schemas.EventCreate, db: Session = Depends(get_db)):
    return crud.create_event(db=db, event=event)

@app.get("/events", response_model=list[schemas.EventResponse])
def list_events_endpoint(db: Session = Depends(get_db)):
    return crud.get_all_events(db)

from fastapi import BackgroundTasks # Tambahkan import ini

@app.post("/buy/{event_id}")
def buy_ticket_endpoint(
    event_id: int, 
    user_id: int, 
    background_tasks: BackgroundTasks, # Tambahkan ini di parameter
    db: Session = Depends(get_db)
):
    # 1. Jalankan proses booking seperti biasa
    booking = crud.process_ticket_purchase(db, event_id, user_id)
    
    # 2. Perintahkan petugas kebersihan untuk cek 15 menit lagi
    background_tasks.add_task(crud.cancel_expired_booking, db, booking.id)
    
    return {
        "status": "Success",
        "message": "Booking reserved. Please pay within 15 minutes.",
        "booking_id": booking.id
    }


@app.post("/pay/{booking_id}")
def pay_ticket_endpoint(booking_id: int, db: Session = Depends(get_db)):
    result = crud.confirm_payment(db, booking_id)
    return result