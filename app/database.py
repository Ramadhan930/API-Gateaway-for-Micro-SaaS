import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Load file .env dengan path absolut agar tidak 'None' lagi
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 3. Definisikan Engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 4. Buat SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Definisikan Base (SANGAT PENTING: Jangan sampai hilang!)
Base = declarative_base()

# 6. Fungsi Dependency untuk get_db
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()