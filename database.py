from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. เปลี่ยนจาก Postgres เป็น SQLite (เป็นไฟล์ Database ธรรมดา)
# สังเกตว่าไม่ต้องดึง os.getenv มาใช้แล้ว
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# 2. สร้าง Engine
# connect_args={"check_same_thread": False} จำเป็นต้องใส่เฉพาะตอนใช้ SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. สร้าง SessionLocal (ตัวจัดการการเชื่อมต่อ)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. สร้าง Base Class (แม่แบบของตารางต่างๆ)
Base = declarative_base()
