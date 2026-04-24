import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------
# [CONFIG] Load Environment Variables
# ---------------------------------------------------------
# Mencari file .env di folder root (satu tingkat di atas folder app)
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# ---------------------------------------------------------
# [ENGINE] Database Connection Setup
# ---------------------------------------------------------
# Membuat mesin koneksi ke PostgreSQL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Cek dulu koneksinya sebelum dipakai
    connect_args={"connect_timeout": 10}
)

# Factory untuk membuat sesi database setiap kali ada request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------------------------------------------------------
# [BASE] ORM Foundation
# ---------------------------------------------------------
# Kelas utama yang akan di-inherit oleh semua model tabel di models.py
Base = declarative_base()

# ---------------------------------------------------------
# [DEPENDENCY] Database Session Generator
# ---------------------------------------------------------
def get_db():
    """Fungsi pembantu untuk membuka dan menutup koneksi secara otomatis."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()