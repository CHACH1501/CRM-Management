from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Activity Schemas ---
# ใช้สำหรับรับส่งข้อมูลกิจกรรม (Service)
class ActivityBase(BaseModel):
    name: str
    description: Optional[str] = None

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: int
    
    class Config:
        from_attributes = True  # ช่วยให้แปลงข้อมูลจาก Database เป็น JSON ได้

# --- Rule Schemas ---
# ใช้สำหรับรับส่งข้อมูลเงื่อนไข (Smart Reminder)
class RuleBase(BaseModel):
    name: str
    condition_json: Dict[str, Any] # เก็บเงื่อนไขเป็น JSON เช่น {"months": 6}
    activity_id: int

class RuleCreate(RuleBase):
    pass

class Rule(RuleBase):
    id: int

    class Config:
        from_attributes = True

# --- User Schemas ---
# ใช้สำหรับรับส่งข้อมูล User (ส่วนที่ Error อยู่ตอนนี้คือขาดอันนี้ครับ)
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    # ถ้าอยากให้ User แสดง activities หรือ rules ที่เกี่ยวข้องด้วย ให้เพิ่ม field ตรงนี้ในอนาคต

    class Config:
        from_attributes = True
        
# เพิ่มต่อท้ายสุด
class ServiceHistoryBase(BaseModel):
    customer_identifier: str
    service_date: datetime
    activity_id: int

class ServiceHistoryCreate(ServiceHistoryBase):
    pass

class ServiceHistory(ServiceHistoryBase):
    id: int
    next_due_date: datetime # field นี้ User ไม่ต้องกรอก ระบบจะตอบกลับมาเอง

    class Config:
        from_attributes = True