from database import engine
import models

print("กำลังล้างข้อมูลเก่าใน Database...")

# คำสั่งนี้จะลบตาราง activities, rules, users เก่าทิ้งทั้งหมด
models.Base.metadata.drop_all(bind=engine)

print("✅ ล้างเสร็จแล้ว! Database สะอาดพร้อมใช้งาน")