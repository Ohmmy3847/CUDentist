from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
import asyncio
import aiohttp
from typing import List
from tqdm import tqdm

from flow import FLOWS
import pandas as pd
import os


# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------
# Mapping ระหว่าง field name กับชื่อคำถามที่อ่านง่าย
FIELD_LABELS = {
    # Basic Info (ข้อ 1-5)
    'age': 'อายุ',
    'gender': 'เพศ',
    'hn': 'HN',
    'procedures': 'หัตถการที่ทำ',
    'surgery_date': 'ได้รับการผ่าตัดเมื่อวันที่',
    
    # Symptoms (ข้อ 6-20)
    'pain_score': 'ระดับความปวด (Pain score)',
    'pain_medication_effective': 'ทานยาแก้ปวดแล้วดีขึ้นหรือไม่',
    'swelling_status': 'อาการบวม',
    'breathing_or_swallowing_difficulty': 'มีอาการหายใจลำบาก หรือ กลืนลำบากหรือไม่',
    'bleeding_status': 'อาการเลือดซึม หรือ เลือดออก',
    'fever_status': 'อาการไข้',
    'numbness_status': 'อาการชา',
    'phlebitis': 'บริเวณที่เอาเข็มน้ำเกลือออก',
    'suture_status': 'ไหมเย็บแผล',
    'other_symptoms': 'อาการอื่นๆ',
    'antibiotic_compliance': 'รับประทานยาฆ่าเชื้อ',
    'compress_type': 'ประคบเย็น หรือ อุ่นอยู่หรือไม่',
    'has_imf': 'มีการมัดฟันบนและล่างเข้าด้วยกัน (IMF)',
    'imf_wire_status': 'ลวด/ยางมัดฟันแน่นดีหรือไม่',
    'walking_status': 'การเดิน',
    
    # Daily Life (ข้อ 21-27)
    'brushing_teeth': 'การแปรงฟัน',
    'mouth_rinsing': 'การบ้วนปาก',
    'feeding_method': 'วิธีการรับประทานอาหาร',
    'food_types': 'ประเภทอาหารที่ทาน',
    'food_amount': 'ปริมาณอาหารที่ทาน',
    'additional_questions': 'ผู้ป่วยมีคำถามที่จะสอบถามพยาบาลเพิ่มเติม',
    'ng_tube_position': 'ตำแหน่งสายยางให้อาหาร',
}

# Mapping ระหว่าง main field กับ description field
FIELD_WITH_DESCRIPTION = {
    'swelling_status': 'swelling_description',
    'breathing_or_swallowing_difficulty': 'breathing_description',
    'bleeding_status': 'bleeding_description',
    'fever_status': 'fever_description',
    'numbness_status': 'numbness_description',
    'phlebitis': 'phlebitis_description',
    'suture_status': 'suture_description',
    'antibiotic_compliance': 'antibiotic_description',
    'imf_wire_status': 'imf_wire_description',
    'walking_status': 'walking_description',
    'brushing_teeth': 'brushing_description',
    'mouth_rinsing': 'rinsing_description',
    'feeding_method': 'feeding_description',
    'food_amount': 'food_amount_description',
    'ng_tube_position': 'ng_tube_description',
}

# Mapping ชื่อ description field ที่อ่านง่าย
DESCRIPTION_LABELS = {
    'swelling_description': 'คำอธิบายเพิ่มเติมสำหรับอาการบวม',
    'breathing_description': 'คำอธิบายเพิ่มเติมสำหรับอาการหายใจ/กลืนลำบาก',
    'bleeding_description': 'คำอธิบายเพิ่มเติมสำหรับอาการเลือดซึม/เลือดออก',
    'fever_description': 'คำอธิบายเพิ่มเติมสำหรับอาการไข้',
    'numbness_description': 'คำอธิบายเพิ่มเติมสำหรับอาการชา',
    'phlebitis_description': 'คำอธิบายเพิ่มเติมสำหรับบริเวณเข็มน้ำเกลือ',
    'suture_description': 'คำอธิบายเพิ่มเติมสำหรับไหมเย็บแผล',
    'antibiotic_description': 'จำนวนครั้งที่ลืมทาน',
    'imf_wire_description': 'คำอธิบายเพิ่มเติมสำหรับลวด/ยางมัดฟัน',
    'walking_description': 'คำอธิบายเพิ่มเติมสำหรับการเดิน',
    'brushing_description': 'คำอธิบายเพิ่มเติมสำหรับการแปรงฟัน',
    'rinsing_description': 'คำอธิบายเพิ่มเติมสำหรับการบ้วนปาก',
    'feeding_description': 'คำอธิบายเพิ่มเติมสำหรับวิธีการรับประทานอาหาร',
    'food_amount_description': 'คำอธิบายเพิ่มเติมสำหรับปริมาณอาหาร',
    'ng_tube_description': 'คำอธิบายเพิ่มเติมสำหรับตำแหน่งสายยางให้อาหาร',
}


# ------------------------------------------------------------
# 1) Pydantic Model
# ------------------------------------------------------------
class OutputRiskClassification(BaseModel):
    risk_level: str = Field(description="ระดับความเสี่ยงของผู้ป่วย [ความเสี่ยงต่ำ, ความเสี่ยงกลาง, ความเสี่ยงสูง]")
    recommendation: str = Field(description="คำแนะนำการดูแลตนเองสำหรับผู้ป่วย เขียนเป็นภาษาไทย ต้องบอกชัดว่าควรทำอะไร")
    reason: str = Field(description="เหตุผลที่ประเมินระดับความเสี่ยงนี้ เขียนเป็นภาษาไทย")


# ------------------------------------------------------------
# 2) Utility: Load CSV and convert first row to text
# ------------------------------------------------------------
def load_first_row_as_text(csv_path: str) -> str:
  
    df = pd.read_csv(csv_path)
    row = df.iloc[0]

    text_parts = []
    for col in df.columns:
        value = row[col]
        if pd.isna(value) or value == "":
            value = "ไม่ได้ระบุ"
        text_parts.append(f"{col}\n{value}")

    return "\n".join(text_parts)


# ------------------------------------------------------------
# Helper Functions for Data Conversion
# ------------------------------------------------------------
def convert_value_to_string(value) -> str:
    """แปลงค่าต่างๆ ให้เป็น string ที่อ่านได้"""
    if value is None or value == "":
        return "ไม่ได้ระบุ"
    
    # Handle list/tuple
    if isinstance(value, (list, tuple)):
        if len(value) == 0:
            return "ไม่ได้ระบุ"
        return ", ".join(str(v) for v in value)
    
    # Handle other iterables (numpy arrays, etc.)
    if hasattr(value, '__iter__') and not isinstance(value, str):
        try:
            if len(value) == 0:
                return "ไม่ได้ระบุ"
            return ", ".join(str(v) for v in value)
        except:
            return str(value)
    
    # Handle pandas NA
    try:
        if pd.isna(value):
            return "ไม่ได้ระบุ"
    except (TypeError, ValueError):
        pass
    
    return str(value)


def format_field_with_description(label: str, value: str, description: str = "", desc_field: str = "") -> str:
    """Format field พร้อมคำอธิบายเพิ่มเติม"""
    if description and description != "":
        # ใช้ชื่อ description field ที่อ่านง่าย
        desc_label = DESCRIPTION_LABELS.get(desc_field, "เพิ่มเติม")
        return f"{label}: {value} ({desc_label}: {description})"
    return f"{label}: {value}"


def dict_as_text(data: dict) -> str:
    """แปลง dictionary ข้อมูลผู้ป่วยเป็น text ที่อ่านง่าย"""
    processed_fields = set()
    text_parts = []
    
    for col, value in data.items():
        # ข้าม field ที่เป็น description (จะรวมเข้ากับ main field)
        if col in processed_fields or col.endswith('_description'):
            continue
        
        # แปลง value เป็น string
        value_str = convert_value_to_string(value)
        
        # ใช้ชื่อคำถามที่อ่านง่าย
        label = FIELD_LABELS.get(col, col)
        
        # ถ้า field นี้มี description คู่กัน
        if col in FIELD_WITH_DESCRIPTION:
            desc_field = FIELD_WITH_DESCRIPTION[col]
            desc_value = data.get(desc_field, "")
            formatted_text = format_field_with_description(label, value_str, desc_value, desc_field)
            text_parts.append(formatted_text)
            processed_fields.add(desc_field)
        else:
            text_parts.append(f"{label}: {value_str}")
    
    result = "\n".join(text_parts)
    
    # เขียนลง temp.txt เพื่อ debug
    save_debug_output(result)
    
    return result


def save_debug_output(text: str, filename: str = "temp.txt"):
    """บันทึก output สำหรับ debug"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        # Ignore errors in debug output
        pass


# ------------------------------------------------------------
# 3) Build LLM Model
# ------------------------------------------------------------
def build_llm(api_key: str):
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=api_key
    )

def build_llm_local():
    return ChatOllama(
        model="qwen2:latest",
        temperature=0.0,
    )

# ------------------------------------------------------------
# 4) Create the Prompt + Chain
# ------------------------------------------------------------
def build_risk_chain(llm, pain_flow: str):
    parser = PydanticOutputParser(pydantic_object=OutputRiskClassification)

    prompt = PromptTemplate(
        template=(
            "คุณเป็นพยาบาลที่ให้คำปรึกษาผู้ป่วยหลังผ่าตัด\n\n"
            "**สำคัญ: ประเมินเฉพาะตามเกณฑ์การประเมินที่กำหนดให้เท่านั้น อย่าวิเคราะห์อาการอื่นๆ**\n\n"
            
            "เกณฑ์การประเมิน (ให้ประเมินเฉพาะเกณฑ์นี้):\n{syntom_flow}\n\n"
            "ข้อมูลผู้ป่วย:\n{result_text}\n\n"
            
            "วิธีการประเมิน:\n"
            "1. ดูเฉพาะข้อมูลที่เกี่ยวข้องกับเกณฑ์การประเมินด้านบน\n"
            "2. ประเมินระดับความเสี่ยง [ความเสี่ยงต่ำ, ความเสี่ยงกลาง, ความเสี่ยงสูง]\n"
            "3. เหตุผล (reason): อธิบายสั้นๆ ตามเกณฑ์ที่ประเมิน (ไม่เกิน 2-3 ประโยค)\n"
            "4. คำแนะนำ (recommendation): ให้คำแนะนำที่เกี่ยวข้องกับเกณฑ์ที่ประเมินเท่านั้น\n\n"
            
            "คำแนะนำ (recommendation) ที่ดี:\n"
            "- กระชับ ตรงประเด็น (2-4 ข้อ)\n"
            "- บอกชัดว่าควรทำอะไร ไม่ใช่สรุปอาการ\n"
            "- ตัวอย่าง:\n"
            "  * ความเสี่ยงสูง: ควรติดต่อแพทย์/พยาบาลโดยเร็ว\n"
            "  * ความเสี่ยงกลาง: ควรสังเกตอาการ หากแย่ลงให้ติดต่อแพทย์\n"
            "  * ความเสี่ยงต่ำ: ดูแลตามคำแนะนำทั่วไป\n\n"
            
            "กรณีไม่มีข้อมูล: risk_level = 'ความเสี่ยงต่ำ', reason = 'ไม่ได้ระบุข้อมูล', recommendation = 'ไม่มีคำแนะนำเฉพาะ กรุณาปฏิบัติตามคำแนะนำทั่วไปหลังผ่าตัด'\n\n"
            
            "{format_instructions}\n"
        ),
        input_variables=["syntom_flow", "result_text"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser
    return chain


# ------------------------------------------------------------
# 5) Main Risk Classification Function
# ------------------------------------------------------------
def classify_risk(input_data: dict, api_key: str = None, flow: str = None, llm=None):
    """
    Classify risk with option to reuse LLM instance
    Args:
        input_data: Patient data dictionary
        api_key: Google API key (not needed if llm is provided)
        flow: Risk flow criteria
        llm: Pre-built LLM instance (optional, will create new if not provided)
    """
    if llm is None:
        if api_key is None:
            raise ValueError("Either llm or api_key must be provided")
        os.environ["GOOGLE_API_KEY"] = api_key
        llm = build_llm(api_key)

    # Prepare model + data
    result_text = dict_as_text(input_data)
    chain = build_risk_chain(llm, flow)

    # Run prediction
    result = chain.invoke({
        "syntom_flow": flow,
        "result_text": result_text
    })

    return result

# Async version for concurrent processing
async def classify_risk_async(input_data: dict, llm, flow: str, flow_name: str, semaphore):
    async with semaphore:
        result_text = dict_as_text(input_data)
        chain = build_risk_chain(llm, flow)

        # Run prediction in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: chain.invoke({
                "syntom_flow": flow,
                "result_text": result_text
            })
        )
        
        return flow_name, result

async def _process_all_rows(df: pd.DataFrame, llm, output_file: str, max_concurrent: int):
    """Process all rows with concurrent API calls"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    # Process each row
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
        input_data = row.to_dict()
        
        # Create tasks for all flows for this row
        tasks = [
            classify_risk_async(input_data, llm, flow, flow_name, semaphore)
            for flow_name, flow in FLOWS.items()
        ]
        
        # Run all flow classifications concurrently for this row
        results = await asyncio.gather(*tasks)
        
        # Update dataframe with results
        for flow_name, output in results:
            df.at[idx, f"{flow_name}_risk_level"] = output.risk_level
            df.at[idx, f"{flow_name}_risk_reason"] = output.reason
            df.at[idx, f"{flow_name}_recommendation"] = output.recommendation
    
    # Save results
    df.to_csv(output_file, index=False)
    print(f"\nResults saved to {output_file}")

def csv_to_risk_classification(csv_file: str, api_key: str, output_file: str = "result_with_risk.csv", max_concurrent: int = 10):
    """Optimized version using async processing
    
    Args:
        csv_file: Path to input CSV
        api_key: Google API key
        output_file: Path to output CSV
        max_concurrent: Maximum concurrent API calls (default: 10)
    """
    os.environ["GOOGLE_API_KEY"] = api_key
    
    df = pd.read_csv(csv_file)
    for flow_name in FLOWS.keys():
        df[f"{flow_name}_risk_level"] = ""
        df[f"{flow_name}_risk_reason"] = ""
        df[f"{flow_name}_recommendation"] = ""

    # สร้าง LLM instance เพียงครั้งเดียว
    llm = build_llm(api_key)
    
    # Run async processing
    asyncio.run(_process_all_rows(df, llm, output_file, max_concurrent))


if __name__ == "__main__":
    df = pd.read_csv("data/66.csv")
    input_data = df.iloc[5].to_dict()
    

    
    api_key = "AIzaSyA2AffQ9M_21x0GwOrJyMiYk6f5Xo5j4ZI"
    
    # สร้าง LLM instance ครั้งเดียว
    llm = build_llm(api_key)

    all_risk = {}
    for i in FLOWS.keys():
        all_risk[i] = classify_risk(
            input_data=input_data,
            flow=FLOWS[i],
            llm=llm  # ส่ง LLM ที่สร้างไว้แล้ว
        )
    
    df = pd.DataFrame(all_risk)
    
    
    df.to_csv("risk_classification.csv", index=False)
