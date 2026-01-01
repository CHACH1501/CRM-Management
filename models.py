from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON, DateTime
from sqlalchemy.orm import relationship
from database import Base


# ตาราง Users
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

# ตาราง Activities (ที่เป็นปัญหาเมื่อกี้ คือขาด name กับ description)
class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)       # บรรทัดนี้สำคัญ!
    description = Column(String, nullable=True) # บรรทัดนี้ด้วย

# ตาราง Rules
class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    condition_json = Column(JSON)
    activity_id = Column(Integer, ForeignKey("activities.id"))

    # สร้างความสัมพันธ์กลับไปหา Activity
    activity = relationship("Activity")
    
# เพิ่มตารางนี้ต่อท้ายสุด
class ServiceHistory(Base):
    __tablename__ = "service_history"

    id = Column(Integer, primary_key=True, index=True)
    customer_identifier = Column(String, index=True) # เช่น ทะเบียนรถ, เบอร์โทร, หรือ HN คนไข้
    service_date = Column(DateTime)      # วันที่มาใช้บริการ
    next_due_date = Column(DateTime)     # วันที่นัดครั้งต่อไป (ระบบคิดให้)
    
    activity_id = Column(Integer, ForeignKey("activities.id"))
    activity = relationship("Activity")
