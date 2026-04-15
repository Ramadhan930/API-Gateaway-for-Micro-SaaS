import shutil
import os
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from jose import JWTError, jwt

# Import internal
from . import models, schemas, crud, utils
from .database import engine, get_db

# ---------------------------------------------------------
# [INIT] Database & Folders
# ---------------------------------------------------------
models.Base.metadata.create_all(bind=engine)

# Otomatis buat folder uploads jika belum ada
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------------------------------------------------
# [APP CONFIG]
# ---------------------------------------------------------
app = FastAPI(
    title="NeuraTicket API",
    description="Micro-SaaS Ticketing System dengan Bukti Pembayaran",
    version="1.1.0"
)

# Mount folder static AGAR foto bisa dibuka di browser (URL: /static/...)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------------------------------------------------
# [SECURITY] JWT Authentication Logic
# ---------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesi telah berakhir, silakan login ulang.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, utils.SECRET_KEY, algorithms=[utils.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# ---------------------------------------------------------
# [SYSTEM 1] AUTHENTICATION
# ---------------------------------------------------------

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "online", "message": "Let's cook? Your API is ready!"}

@app.post("/register", response_model=schemas.UserResponse, tags=["Auth"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar!")
    return crud.create_user(db=db, user=user)

@app.post("/login", response_model=schemas.Token, tags=["Auth"])
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email atau password salah")
    
    access_token = utils.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# ---------------------------------------------------------
# [SYSTEM 2] EVENT MANAGEMENT
# ---------------------------------------------------------

@app.post("/events", response_model=schemas.EventResponse, tags=["Events"])
def create_event_endpoint(event: schemas.EventCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return crud.create_event(db=db, event=event)

@app.get("/events", response_model=list[schemas.EventResponse], tags=["Events"])
def list_events_endpoint(db: Session = Depends(get_db)):
    return crud.get_all_events(db)

# ---------------------------------------------------------
# [SYSTEM 3] TRANSACTIONS (BUY & PAY)
# ---------------------------------------------------------

@app.post("/buy/{event_id}", tags=["Transactions"])
def buy_ticket_endpoint(
    event_id: int, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) 
):
    booking = crud.process_ticket_purchase(db, event_id, current_user.id)
    background_tasks.add_task(crud.cancel_expired_booking, db, booking.id)
    
    return {
        "status": "Success",
        "message": f"Halo {current_user.username}, tiket dipesan!",
        "booking_id": booking.id
    }

@app.post("/pay/{booking_id}", tags=["Transactions"])
async def pay_ticket_endpoint(
    booking_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Cek kepemilikan booking
    booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id, 
        models.Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking tidak ditemukan atau bukan milik Anda.")

    if booking.status == "PAID":
        return {"message": "Booking ini sudah dibayar sebelumnya."}

    # 2. Simpan file bukti bayar
    extension = file.filename.split(".")[-1]
    filename = f"proof_{booking_id}_{current_user.id}.{extension}"
    save_path = os.path.join(UPLOAD_DIR, filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. Update DB
    booking.status = "PAID"
    booking.payment_proof = f"/static/uploads/{filename}"
    db.commit()

    return {
        "message": "Pembayaran berhasil di-upload!",
        "proof_url": booking.payment_proof
    }