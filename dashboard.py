import streamlit as st
import requests
from datetime import datetime

# URL ของ Backend เรา (FastAPI)
API_URL = "http://127.0.0.1:8000"

st.title("🚗 Niche Service CRM")
st.write("ระบบจัดการและแจ้งเตือนลูกค้าอัตโนมัติ")

# สร้าง Tab แยกหน้าทำงาน
tab1, tab2 = st.tabs(["📝 บันทึกบริการ", "🔔 ตรวจสอบแจ้งเตือน"])

# --- Tab 1: หน้าบันทึกงาน (Service Recording) ---
with tab1:
    st.header("บันทึกการเข้ารับบริการ")
    
    # 1. ดึงข้อมูล Activity มาให้เลือก (Dropdown)
    try:
        response = requests.get(f"{API_URL}/activities/")
        if response.status_code == 200:
            activities = response.json()
            # สร้างตัวเลือก เช่น "1: Service Change Oil"
            options = {act['name']: act['id'] for act in activities}
            selected_activity_name = st.selectbox("เลือกบริการที่ทำ", list(options.keys()))
            selected_activity_id = options[selected_activity_name]
        else:
            st.error("ไม่สามารถดึงข้อมูลบริการได้")
            activities = []
    except:
        st.error("เชื่อมต่อ Backend ไม่ได้ กรุณาเช็คว่ารัน uvicorn อยู่ไหม")

    # 2. กรอกข้อมูลลูกค้า
    customer_id = st.text_input("ทะเบียนรถ / รหัสลูกค้า", placeholder="เช่น กข-9999")
    service_date = st.date_input("วันที่เข้ารับบริการ", datetime.now())

    # 3. ปุ่มบันทึก
    if st.button("บันทึกข้อมูล", type="primary"):
        if customer_id and selected_activity_id:
            # เตรียมข้อมูลส่งไป Backend
            payload = {
                "customer_identifier": customer_id,
                "service_date": service_date.strftime("%Y-%m-%dT%H:%M:%S"),
                "activity_id": selected_activity_id
            }
            
            # ยิง API ไปที่ POST /services/
            res = requests.post(f"{API_URL}/services/", json=payload)
            
            if res.status_code == 200:
                result = res.json()
                # แปลงวันที่กลับมาโชว์ให้สวยๆ
                next_date = result['next_due_date'].split("T")[0]
                st.success(f"✅ บันทึกสำเร็จ! นัดครั้งถัดไปคือ: **{next_date}**")
            else:
                st.error(f"เกิดข้อผิดพลาด: {res.text}")
        else:
            st.warning("กรุณากรอกข้อมูลให้ครบ")

# --- Tab 2: หน้าแจ้งเตือน (Reminder Report) ---
with tab2:
    st.header("📅 รายชื่อลูกค้าที่ครบกำหนด")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("เริ่มวันที่", datetime.now())
    with col2:
        end_date = st.date_input("ถึงวันที่")

    if st.button("ค้นหาลูกค้า"):
        # ยิง API ไปที่ GET /reminders/
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        res = requests.get(f"{API_URL}/reminders/", params=params)
        
        if res.status_code == 200:
            data = res.json()
            if len(data) > 0:
                st.info(f"พบลูกค้าจำนวน {len(data)} ราย")
                # แสดงเป็นตารางสวยๆ
                st.table(data) 
            else:
                st.warning("ไม่พบลูกค้าที่ครบกำหนดในช่วงเวลานี้")
        else:
            st.error("เกิดข้อผิดพลาดในการดึงข้อมูล")
