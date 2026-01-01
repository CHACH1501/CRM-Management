from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from logic import calculate_next_date  # ดึงสมองที่เราเพิ่งสร้างมาใช้
from datetime import datetime          # ใช้สำหรับจัดการวันที่

# Import ไฟล์ที่เราสร้างไว้ก่อนหน้านี้
import models
import schemas
from database import SessionLocal, engine

# บรรทัดนี้สำคัญมาก: สั่งให้สร้าง Table ใน Database ตามที่เขียนใน models.py (ถ้ายังไม่มี)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency: ฟังก์ชันสำหรับเชื่อมต่อและตัดการเชื่อมต่อ Database ในแต่ละ Request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints ---
@app.post("/services/", response_model=schemas.ServiceHistory)
def create_service_record(service: schemas.ServiceHistoryCreate, db: Session = Depends(get_db)):
    # 1. หา Rule ของ Activity นี้ก่อน
    rule = db.query(models.Rule).filter(models.Rule.activity_id == service.activity_id).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="ไม่พบกฎการแจ้งเตือนสำหรับบริการนี้ (กรุณาสร้าง Rule ก่อน)")

    # 2. ใช้สมอง (logic.py) คำนวณวันนัดถัดไป
    calculated_due_date = calculate_next_date(service.service_date, rule.condition_json)

    # 3. บันทึกลง Database
    db_service = models.ServiceHistory(
        customer_identifier=service.customer_identifier,
        service_date=service.service_date,
        next_due_date=calculated_due_date, # บันทึกวันที่คำนวณได้
        activity_id=service.activity_id
    )
    
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    
    return db_service

@app.get("/services/", response_model=List[schemas.ServiceHistory])
def read_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    services = db.query(models.ServiceHistory).offset(skip).limit(limit).all()
    return services


@app.get("/")
def read_root():
    return {"message": "Welcome to Niche Service CRM API"}

# 1. Users (เผื่อไว้สำหรับการสร้าง User หลัก)
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # สร้าง User ใหม่
    fake_hashed_password = user.password + "notreallyhashed" # Phase ต่อไปเราจะมาทำ Hash จริงๆ กัน
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password, is_active=True)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

# 2. Activities (บริการต่างๆ เช่น "เปลี่ยนถ่ายน้ำมันเครื่อง", "ตรวจสุขภาพฟัน")
@app.post("/activities/", response_model=schemas.Activity)
def create_activity(activity: schemas.ActivityCreate, db: Session = Depends(get_db)):
    # เช็คว่ามี User (Tenant) นี้อยู่จริงไหม (สมมติว่า activity ผูกกับ user_id)
    # ในขั้นตอนนี้เราจะสร้าง Activity เลย
    db_activity = models.Activity(**activity.dict())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@app.get("/activities/", response_model=List[schemas.Activity])
def read_activities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    activities = db.query(models.Activity).offset(skip).limit(limit).all()
    return activities

# 3. Rules (เงื่อนไขการแจ้งเตือน เช่น "ครบ 6 เดือน")
@app.post("/rules/", response_model=schemas.Rule)
def create_rule(rule: schemas.RuleCreate, db: Session = Depends(get_db)):
    # เช็คว่า activity_id ที่ส่งมามีอยู่จริงไหม
    db_activity = db.query(models.Activity).filter(models.Activity.id == rule.activity_id).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    db_rule = models.Rule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@app.get("/rules/", response_model=List[schemas.Rule])
def read_rules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rules = db.query(models.Rule).offset(skip).limit(limit).all()
    return rules

# --- Test Logic Endpoint ---
# API นี้ไว้ทดสอบการคำนวณวันเล่นๆ (ยังไม่เก็บลง DB)
@app.post("/test-calculation/")
def test_calculation(activity_id: int, last_service_date: datetime, db: Session = Depends(get_db)):
    # 1. หา Rule ที่ผูกกับ Activity นี้
    rule = db.query(models.Rule).filter(models.Rule.activity_id == activity_id).first()

    if not rule:
        return {"error": "ไม่พบกฎการแจ้งเตือนสำหรับบริการนี้"}

    # 2. ส่งให้สมอง (logic.py) คำนวณ
    next_due_date = calculate_next_date(last_service_date, rule.condition_json)

    return {
        "activity": rule.activity.name,
        "rule_name": rule.name,
        "last_service": last_service_date,
        "next_due_date": next_due_date,
        "message": f"คุณต้องกลับมาใช้บริการอีกครั้งวันที่ {next_due_date.date()}"
    }

# --- Reminder Endpoint ---
# API สำหรับดึงรายชื่อลูกค้าที่ "ถึงกำหนด" ในช่วงเวลาที่ระบุ
@app.get("/reminders/", response_model=List[schemas.ServiceHistory])
def get_upcoming_reminders(
    start_date: datetime, 
    end_date: datetime, 
    db: Session = Depends(get_db)
):
    """
    ค้นหาลูกค้าที่ next_due_date อยู่ในช่วงวันที่ระบุ
    เช่น: หาคนที่ครบกำหนดตั้งแต่ 1 ก.ค. ถึง 31 ก.ค.
    """
    reminders = db.query(models.ServiceHistory).filter(
        models.ServiceHistory.next_due_date >= start_date,
        models.ServiceHistory.next_due_date <= end_date
    ).all()
    
    return reminders

