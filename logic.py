from datetime import datetime, timedelta

def calculate_next_date(last_date: datetime, rule_json: dict):
    """
    ฟังก์ชันคำนวณวันนัดหมายครั้งถัดไป
    รับค่า: วันที่ล่าสุด (last_date) และ กฎเงื่อนไข (rule_json)
    คืนค่า: วันที่นัดหมายครั้งถัดไป
    """
    next_date = last_date

    # 1. กรณีระบุเป็น "จำนวนวัน" (days)
    if "days" in rule_json:
        days_to_add = rule_json["days"]
        next_date = next_date + timedelta(days=days_to_add)

    # 2. กรณีระบุเป็น "จำนวนเดือน" (months) 
    # (คิดแบบง่าย: 1 เดือน = 30 วัน เพื่อลดความซับซ้อนไม่ต้องลง library เพิ่ม)
    if "months" in rule_json:
        months_to_add = rule_json["months"]
        next_date = next_date + timedelta(days=months_to_add * 30)

    return next_date
