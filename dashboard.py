import streamlit as st
import requests
from datetime import datetime

# --- 1. ตั้งค่า URL ของ Backend (เดี๋ยวเราจะแก้บรรทัดนี้ตอน Render เสร็จ) ---
# ตอนนี้ใช้ localhost ไปก่อน หรือถ้า Render เสร็จแล้ว ให้เอาลิงก์มาใส่แทนที่นี่
# เช่น: API_URL = "https://crm-api-chach1501.onrender.com"
API_URL = "https://crm-management-aals.onrender.com" # <--- เดี๋ยวกลับมาแก้ตรงนี้บรรทัดเดียวจบ!

st.set_page_config(page_title="Niche CRM", page_icon="🚗")

# --- 2. สร้างระบบ Login แบบง่าย (Simple Password) ---
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == "admin1234": # <--- ตั้งรหัสผ่านตรงนี้
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "🔒 กรุณาใส่รหัสผ่านเพื่อเข้าใช้งาน", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "🔒 กรุณาใส่รหัสผ่านเพื่อเข้าใช้งาน", type="password", on_change=password_entered, key="password"
        )
        st.error("❌ รหัสผ่านไม่ถูกต้อง")
        return False
    else:
        # Password correct.
        return True

# --- เริ่มการทำงานของแอป ---
if check_password():
    # ถ้าใส่รหัสถูก ถึงจะโชว์เนื้อหาข้างล่างนี้
    st.title("🚗 Niche Service CRM")
    st.write(f"เชื่อมต่อกับ Server: `{API_URL}`")
    
    # สร้าง Tab แยกหน้าทำงาน
    tab1, tab2 = st.tabs(["📝 บันทึกบริการ", "🔔 ตรวจสอบแจ้งเตือน"])

    # --- Tab 1: หน้าบันทึกงาน ---
    with tab1:
        st.header("บันทึกการเข้ารับบริการ")
        try:
            response = requests.get(f"{API_URL}/activities/")
            if response.status_code == 200:
                activities = response.json()
                options = {act['name']: act['id'] for act in activities}
                selected_activity_name = st.selectbox("เลือกบริการที่ทำ", list(options.keys()))
                selected_activity_id = options[selected_activity_name]
                
                customer_id = st.text_input("ทะเบียนรถ / รหัสลูกค้า", placeholder="เช่น กข-9999")
                service_date = st.date_input("วันที่เข้ารับบริการ", datetime.now())

                if st.button("บันทึกข้อมูล", type="primary"):
                    if customer_id and selected_activity_id:
                        payload = {
                            "customer_identifier": customer_id,
                            "service_date": service_date.strftime("%Y-%m-%dT%H:%M:%S"),
                            "activity_id": selected_activity_id
                        }
                        res = requests.post(f"{API_URL}/services/", json=payload)
                        if res.status_code == 200:
                            result = res.json()
                            next_date = result['next_due_date'].split("T")[0]
                            st.success(f"✅ บันทึกสำเร็จ! นัดครั้งถัดไปคือ: **{next_date}**")
                        else:
                            st.error(f"เกิดข้อผิดพลาด: {res.text}")
                    else:
                        st.warning("กรุณากรอกข้อมูลให้ครบ")
            else:
                st.error("เชื่อมต่อ Backend ได้ แต่ดึงข้อมูลไม่ได้ (เช็ค Database)")
        except:
            st.error("❌ ไม่สามารถเชื่อมต่อกับ Backend ได้ (กำลังรอ Render หรือยังไม่ได้แก้ URL)")

    # --- Tab 2: หน้าแจ้งเตือน ---
    with tab2:
        st.header("📅 รายชื่อลูกค้าที่ครบกำหนด")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("เริ่มวันที่", datetime.now())
        with col2:
            end_date = st.date_input("ถึงวันที่")

        if st.button("ค้นหาลูกค้า"):
            params = {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            }
            try:
                res = requests.get(f"{API_URL}/reminders/", params=params)
                if res.status_code == 200:
                    data = res.json()
                    if len(data) > 0:
                        st.info(f"พบลูกค้าจำนวน {len(data)} ราย")
                        st.table(data)
                        
                        st.write("---")
                        if st.button("📢 ส่งรายงานเข้า LINE ทันที", type="primary"):
                            msg = f"\n📊 สรุปรายการแจ้งเตือน ({datetime.now().date()})\n"
                            msg += f"พบลูกค้าครบกำหนด {len(data)} ราย:\n"
                            for i, item in enumerate(data, 1):
                                due = item['next_due_date'].split("T")[0] 
                                msg += f"{i}. {item['customer_identifier']} (นัด: {due})\n"
                            msg += "\nโปรดติดต่อลูกค้าเพื่อยืนยันนัดหมาย"

                            res_line = requests.post(f"{API_URL}/broadcast/", params={"message": msg})
                            if res_line.status_code == 200:
                                st.balloons()
                                st.success("✅ ส่งข้อมูลเข้ามือถือเรียบร้อย!")
                            else:
                                st.error("❌ ส่งไม่ผ่าน เช็ค Backend")
                    else:
                        st.warning("ไม่พบลูกค้าที่ครบกำหนดในช่วงเวลานี้")
            except:
                st.error("❌ เชื่อมต่อ Backend ไม่ได้")