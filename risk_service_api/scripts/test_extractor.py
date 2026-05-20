import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.rag.chunker import extract_text_from_markdown

# Test doc 064
doc064 = "risk_service_api/data/document/markdown_th/064_ข้อแนะนำในการปฏิบัติตัวหลังการถอนฟันหรือผ่าฟันคุด, แผนกทันตกรรมโรงพยาบาลเปาโล ;.md"
results = extract_text_from_markdown(doc064)
print(f"Doc 064: Extracted {len(results)} text items:")
for i, item in enumerate(results):
    text = item["text"][:120]
    print(f"  [{i+1}] ({item['heading'][:30]}) {text}")

print()

# Test doc 005
doc005 = "risk_service_api/data/document/markdown_th/005_การผ่าตัดขากรรไกรร่วมกับการจัดฟัน (Orthognatic Surgery).md"
results2 = extract_text_from_markdown(doc005)
print(f"Doc 005: Extracted {len(results2)} items (first 5):")
for i, item in enumerate(results2[:5]):
    text = item["text"][:100]
    print(f"  [{i+1}] ({item['heading'][:30]}) {text}")

print()

# Test doc 002
doc002 = "risk_service_api/data/document/markdown_th/002_เคลียร์ทุกคำถามเรื่อง \"การผ่าตัดกระดูกขากรรไกรร่วมกับการจัดฟัน\" ที่คุณควรรู้.md"
results3 = extract_text_from_markdown(doc002)
print(f"Doc 002: Extracted {len(results3)} items (first 5):")
for i, item in enumerate(results3[:5]):
    text = item["text"][:100]
    print(f"  [{i+1}] ({item['heading'][:30]}) {text}")
