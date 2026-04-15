import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv

# ---------------------------------------------------------
# [CONFIG] Load Security Settings
# ---------------------------------------------------------
load_dotenv()

# Konfigurasi Utama Keamanan (Ambil dari .env)
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-untuk-keamanan-lokal")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# ---------------------------------------------------------
# [HASHING] Password Encryption System
# ---------------------------------------------------------
# Menggunakan algoritma Bcrypt (Standar Industri)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Mengubah password teks biasa menjadi kode hash yang tidak bisa dibaca."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Membandingkan input user dengan hash yang tersimpan di database."""
    return pwd_context.verify(plain_password, hashed_password)

# ---------------------------------------------------------
# [TOKEN] JWT (JSON Web Token) System
# ---------------------------------------------------------

def create_access_token(data: dict) -> str:
    """
    Membuat 'Gelang Sakti' (Access Token) untuk user yang berhasil login.
    Masa berlaku otomatis diatur berdasarkan waktu saat ini.
    """
    to_encode = data.copy()
    
    # Menggunakan UTC agar waktu konsisten di server mana pun
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Memasukkan data identitas (sub) dan waktu kedaluwarsa (exp) ke dalam token
    to_encode.update({"exp": expire})
    
    # Proses 'Giling' data menjadi token JWT menggunakan HS256
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt