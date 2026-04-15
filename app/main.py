from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer # Import sudah benar
from sqlalchemy.orm import Session

# Import internal dari folder app
from . import models, schemas, crud, utils
from .database import engine, get_db

# ---------------------------------------------------------
# [DATABASE INIT] Sinkronisasi Tabel Otomatis
# ---------------------------------------------------------
models.Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------
# [APP CONFIG] Inisialisasi Aplikasi
# ---------------------------------------------------------
app = FastAPI(
    title="NeuraTicket API",
    description="Micro-SaaS Ticketing System dengan Keamanan JWT & Background Tasks",
    version="1.0.0"
)

# ---------------------------------------------------------
# [SECURITY CONFIG] Inisialisasi Skema Keamanan (TAMBAHKAN DI SINI)
# ---------------------------------------------------------
# tokenUrl="login" merujuk ke path endpoint login kita di bawah
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ---------------------------------------------------------
# [SYSTEM 1] AUTHENTICATION & USER MANAGEMENT
# ---------------------------------------------------------

@app.get("/", tags=["Health Check"])
def read_root():
    """Cek apakah API berjalan dengan normal."""
    return {"status": "online", "message": "Let's cook? Your API is ready!"}

@app.post("/register", response_model=schemas.UserResponse, tags=["Auth"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Mendaftarkan user baru dan mengecek duplikasi email."""
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email sudah terdaftar!"
        )
    return crud.create_user(db=db, user=user)

@app.post("/login", response_model=schemas.Token, tags=["Auth"])
def login_for_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Sistem Login: Menukarkan email & password dengan JWT Access Token."""
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Email atau password salah",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = utils.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# ---------------------------------------------------------
# [SYSTEM 2] EVENT MANAGEMENT
# ---------------------------------------------------------

@app.post("/events", response_model=schemas.EventResponse, tags=["Events"])
def create_event_endpoint(
    event: schemas.EventCreate, 
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme) # (TAMBAHKAN INI) Agar bikin event harus login
):
    """Membuat acara/event baru untuk dijual tiketnya."""
    return crud.create_event(db=db, event=event)

@app.get("/events", response_model=list[schemas.EventResponse], tags=["Events"])
def list_events_endpoint(db: Session = Depends(get_db)):
    return crud.get_all_events(db)

# ---------------------------------------------------------
# [SYSTEM 3] TICKETING & TRANSACTION
# ---------------------------------------------------------

@app.post("/buy/{event_id}", tags=["Transactions"])
def buy_ticket_endpoint(
    event_id: int, 
    user_id: int, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme) # (TAMBAHKAN INI) Agar beli tiket harus login
):
    """
    Sistem Pembelian: Sekarang butuh 'Authorize' (Gembok) agar bisa diakses.
    """
    booking = crud.process_ticket_purchase(db, event_id, user_id)
    background_tasks.add_task(crud.cancel_expired_booking, db, booking.id)
    
    return {
        "status": "Success",
        "message": "Booking reserved. Please pay within 15 minutes.",
        "booking_id": booking.id,
        "expires_at": booking.expires_at
    }

@app.post("/pay/{booking_id}", tags=["Transactions"])
def pay_ticket_endpoint(
    booking_id: int, 
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme) # (TAMBAHKAN INI) Agar bayar harus login
):
    return crud.confirm_payment(db, booking_id)