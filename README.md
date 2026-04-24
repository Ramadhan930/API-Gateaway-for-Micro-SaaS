# NeuraTicket - Micro-SaaS Ticketing API

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com/)

**NeuraTicket** adalah backend API tangguh untuk sistem penjualan tiket berbasis Micro-SaaS. Dibangun dengan fokus pada **keamanan, otomasi, dan integritas data**, project ini mensimulasikan alur bisnis nyata mulai dari reservasi hingga verifikasi pembayaran otomatis.

---

## Fitur Unggulan

* ** Secure Authentication**: Sistem login & register menggunakan **OAuth2 dengan JWT Token** dan enkripsi password menggunakan **Bcrypt**.
* ** Atomic Inventory System**: Mencegah *overbooking* tiket menggunakan teknik **Atomic Update** pada level database PostgreSQL.
* ** Auto-Cleanup Background Tasks**: Pembatalan otomatis pesanan yang tidak dibayar dalam batas waktu tertentu untuk mengembalikan stok tiket secara real-time.
* ** Payment Proof Upload**: Integrasi penanganan file statis untuk upload dan penyimpanan bukti transfer pembayaran.
* ** Dockerized Environment**: Seluruh sistem (App & Database) sudah terkonfigurasi menggunakan **Docker Compose** untuk kemudahan *deployment*.

---

##  Tech Stack

- **Framework:** FastAPI (Python 3.12+)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Security:** Passlib (Bcrypt), PyJWT (HS256)
- **Containerization:** Docker & Docker Compose
- **Static Storage:** FastAPI StaticFiles

---

## Struktur Proyek (Clean Architecture)
```text
.
├── app/
│   ├── main.py          # Entry point & API Router
│   ├── crud.py          # Logika Bisnis & Database Query
│   ├── models.py        # Definisi Tabel SQLAlchemy
│   ├── schemas.py       # Validasi Data Pydantic
│   ├── database.py      # Konfigurasi Koneksi Database
│   └── utils.py         # Kriptografi & Token JWT
├── static/uploads       # Penyimpanan Bukti Pembayaran
├── .env                 # Konfigurasi Environment (Hidden)
├── docker-compose.yml   # Konfigurasi Container
└── requirements.txt     # Library Python
```

---

## Cara Menjalankan
## 1. Clone Repository
```Bash
git clone [https://github.com/username/NeuraTicket.git](https://github.com/username/NeuraTicket.git)
cd NeuraTicket
```

## 2. Setup Environment
Buat file .env di folder root dan isi:
```Cuplikan kode
DATABASE_URL=postgresql://user_admin:password_rahasia@db:5432/ticket_saas_db
SECRET_KEY=ganti_dengan_key_rahasia_kamu
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 3. Jalankan dengan Docker
```Bash
docker-compose up -d --build
```

## 4. Jalankan API (Local)
```Bash
uvicorn app.main:app --reload
```
Akses Dokumentasi API di: http://localhost:8000/docs

Alur Kerja API (Workflow)
1. Register/Login: User mendapatkan JWT Token.
2. Explore Events: User melihat daftar acara yang tersedia.
3. Buy Ticket: User memesan tiket (Stok berkurang, status PENDING).
4. Auto-Expiration: Jika dalam waktu tertentu tidak dibayar, Background Task menghanguskan pesanan dan mengembalikan stok.
5. Payment: User upload bukti bayar, status berubah menjadi PAID.

Created with 🔥 by Ramadhan
