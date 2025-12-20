"""
Setup Google Sheets with proper headers
Run this script once to create the necessary sheets and headers
"""
import os
import json
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

# Get credentials
service_account_info = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)
client = gspread.authorize(credentials)

# Open spreadsheet
spreadsheet_id = os.getenv("SPREADSHEET_ID")
spreadsheet = client.open_by_key(spreadsheet_id)

# Form columns (from risk_service.py)
FORM_COLUMNS = [
    'Timestamp',
    'อายุ',
    'เพศ',
    'HN',
    'หัตถการที่ทำ',
    'ได้รับการผ่าตัดเมื่อวันที่',
    'ระดับความปวด (Pain score)',
    'ทานยาแก้ปวดแล้วดีขึ้นหรือไม่',
    'อาการบวม',
    'มีอาการหายใจลำบาก หรือ กลืนลำบากหรือไม่',
    'อาการเลือดซึม หรือ เลือดออก',
    'อาการไข้',
    'อาการชา',
    'บริเวณที่เอาเข็มน้ำเกลือออก',
    'ไหมเย็บแผล',
    'อาการอื่นๆ',
    'รับประทานยาฆ่าเชื้อ',
    'ประคบเย็น หรือ อุ่นอยู่หรือไม่',
    'มีการมัดฟันบนและล่างเข้าด้วยกัน (IMF)',
    'ลวด/ยางมัดฟันแน่นดีหรือไม่',
    'การเดิน',
    'การแปรงฟัน',
    'การบ้วนปาก',
    'วิธีการรับประทานอาหาร',
    'ประเภทอาหารที่ทาน',
    'ปริมาณอาหารที่ทาน',
    'ผู้ป่วยมีคำถามที่จะสอบถามพยาบาลเพิ่มเติม',
    'ตำแหน่งสายยางให้อาหาร',
]

# Flow names (18 flows)
FLOW_NAMES = [
    'อาการปวด',
    'อาการบวม',
    'อาการเลือดออก',
    'อาการไข้',
    'อาการชา',
    'Phlebitis',
    'ไหมเย็บแผล',
    'อาการอื่นๆ',
    'การทานยาปฏิชีวนะ',
    'การประคบ',
    'IMF',
    'ลวดหรือยางมัดฟัน',
    'การเดิน',
    'การแปรงฟัน',
    'การบ้วนปาก',
    'การรับประทานอาหาร',
    'ปริมาณอาหาร',
    'ตำแหน่งสายยาง NG tube',
]

print("Setting up Google Sheets...")

# 1. Setup raw_input sheet
print("\n1. Creating 'raw_input' sheet...")
try:
    raw_sheet = spreadsheet.worksheet("raw_input")
    print("   Sheet 'raw_input' already exists. Clearing and updating headers...")
    raw_sheet.clear()
except gspread.exceptions.WorksheetNotFound:
    print("   Creating new sheet 'raw_input'...")
    raw_sheet = spreadsheet.add_worksheet(title="raw_input", rows=1000, cols=len(FORM_COLUMNS))

# Add headers to raw_input
raw_sheet.append_row(FORM_COLUMNS, value_input_option="USER_ENTERED")
print(f"   ✓ Added {len(FORM_COLUMNS)} columns to 'raw_input'")

# 2. Setup input_with_result sheet
print("\n2. Creating 'input_with_result' sheet...")
result_columns = FORM_COLUMNS.copy()

# Add columns for each flow (flow_name, risk_level, reason, recommendation)
for flow_name in FLOW_NAMES:
    result_columns.extend([
        f"{flow_name}_flow_name",
        f"{flow_name}_risk_level",
        f"{flow_name}_reason",
        f"{flow_name}_recommendation"
    ])

# Add metadata columns
result_columns.extend(['model_name', 'logged_timestamp'])

try:
    result_sheet = spreadsheet.worksheet("input_with_result")
    print("   Sheet 'input_with_result' already exists. Clearing and updating headers...")
    result_sheet.clear()
except gspread.exceptions.WorksheetNotFound:
    print("   Creating new sheet 'input_with_result'...")
    result_sheet = spreadsheet.add_worksheet(
        title="input_with_result", 
        rows=1000, 
        cols=len(result_columns)
    )

# Add headers to input_with_result
result_sheet.append_row(result_columns, value_input_option="USER_ENTERED")
print(f"   ✓ Added {len(result_columns)} columns to 'input_with_result'")

print("\n" + "="*60)
print("✓ Setup completed successfully!")
print("="*60)
print(f"\nSpreadsheet URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
print("\nSheets created:")
print(f"  1. raw_input: {len(FORM_COLUMNS)} columns")
print(f"  2. input_with_result: {len(result_columns)} columns")
print(f"     - Form data: {len(FORM_COLUMNS)} columns")
print(f"     - AI results: {len(FLOW_NAMES)} flows × 4 columns = {len(FLOW_NAMES) * 4} columns")
print(f"     - Metadata: 2 columns")
print("\nYou can now run the application and data will be logged automatically!")
