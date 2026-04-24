import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv

# Import tambahan untuk email
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

# ---------------------------------------------------------
# [CONFIG] Load Security & Email Settings
# ---------------------------------------------------------
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-untuk-keamanan-lokal")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# ---------------------------------------------------------
# [HASHING] Password Encryption System
# ---------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ---------------------------------------------------------
# [TOKEN] JWT (JSON Web Token) System
# ---------------------------------------------------------

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ---------------------------------------------------------
# [EMAIL SYSTEM] Notification System (TAMBAHKAN DI SINI)
# ---------------------------------------------------------

# Konfigurasi koneksi ke SMTP Gmail
conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_FROM_NAME = "NeuraTicket Admin",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def send_transaction_email(email_to: str, username: str, event_name: str, booking_id: int):
    """Mengirim email HTML cantik ke user setelah booking."""
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2 style="color: #4CAF50;">🎟️ Konfirmasi Reservasi Tiket</h2>
            <p>Halo <strong>{username}</strong>,</p>
            <p>Pesanan kamu untuk acara <strong>{event_name}</strong> telah kami terima.</p>
            <div style="background-color: #f4f4f4; padding: 15px; border-radius: 8px; border: 1px solid #ddd;">
                <p style="margin: 0;"><strong>Detail Pesanan:</strong></p>
                <hr>
                <p>Booking ID: #{booking_id}</p>
                <p>Status: <span style="color: #ff9800;">PENDING (Menunggu Pembayaran)</span></p>
            </div>
            <p>Segera upload bukti bayar di aplikasi sebelum waktu booking kamu berakhir (15 menit).</p>
            <p>Terima kasih telah menggunakan NeuraTicket!</p>
        </body>
    </html>
    """
    
    message = MessageSchema(
        subject=f"[NeuraTicket] Pesanan #{booking_id} Berhasil Dibuat",
        recipients=[email_to],
        body=html,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)