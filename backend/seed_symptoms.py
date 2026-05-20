"""Seed symptoms from CSV data into PostgreSQL."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.symptom import Symptom
from app.core.config import settings

SYMPTOMS = [
    {"symptom_name": "ปากแห้ง", "risk_level": "low", "recommendation": "ทาวาสลีน"},
    {"symptom_name": "ไอ", "risk_level": "low", "recommendation": "จิบน้ำอุ่นบ่อยๆ และหากมีอาการทางเดินหายใจมากขึ้นแนะนำตรวจ atk"},
    {"symptom_name": "ระคายเคืองคอ", "risk_level": "low", "recommendation": "จิบน้ำบ่อยๆ และหากมีอาการทางเดินหายใจมากขึ้นแนะนำตรวจ atk"},
    {"symptom_name": "ผู้ป่วยที่ได้รับการรักษาด้วย ICBG วิ่งเล่น", "risk_level": "low", "recommendation": "ระวังอุบัติเหตุ และยังไม่ให้วิ่งเล่น เนื่องจากมีแผลที่สะโพกจาก ICBG"},
    {"symptom_name": "แผลที่สะโพกพลาสเตอร์หลุด", "risk_level": "low", "recommendation": "ทำแผลที่โรงพยาบาลใกล้บ้าน และระวังแผลเปียกน้ำ"},
    {"symptom_name": "ลวดจัดฟันเกี่ยวครูดปาก", "risk_level": "low", "recommendation": "รอพบทันตแพทย์ในวันที่นัดหมายติดตามอาการ หรือขอwax จากคลินิกจัดฟันมาติดบนลวด"},
    {"symptom_name": "ลวดมัดฟันเกี่ยวครูดปาก", "risk_level": "low", "recommendation": "รอพบทันตแพทย์ในวันที่นัดหมายติดตามอาการ หรือขอwax จากคลินิกจัดฟันมาติดบนลวด"},
    {"symptom_name": "ลวดทิ่มกระพุ้งแก้ม", "risk_level": "low", "recommendation": "รอพบทันตแพทย์ในวันที่นัดหมายติดตามอาการ หรือขอwax จากคลินิกจัดฟันมาติดบนลวด"},
    {"symptom_name": "มีแผลคล้ายร้อนใน เนื่องจากถูกลวดมัดฟันเกี่ยว", "risk_level": "low", "recommendation": "ขอwax จากคลินิกจัดฟันมาติดบนลวด และซื้อยาทาแผลจากร้านขายยาได้"},
    {"symptom_name": "กินยา ibuprofen แล้วแสบคอ", "risk_level": "low", "recommendation": "ผสมยา ibuprofen กับน้ำก่อนทานเพื่อลดอาการแสบคอ"},
    {"symptom_name": "ยาขม", "risk_level": "low", "recommendation": "ผสมน้ำหวานทาน และแปรงฟันทำความสะอาดช่องปากหลังทานยาผสมน้ำหวาน"},
    {"symptom_name": "ปวดท้องหลังทานยา Brufen", "risk_level": "low", "recommendation": "รับประทานยาทันทีหลังทานอาหาร และดื่มน้ำตามเยอะ ๆ หรือเปลี่ยนมาทานยา paracetamol แทนในกรณีที่ปวดไม่มาก"},
    {"symptom_name": "มีก้อนเลือดที่แผลผ่าตัด", "risk_level": "low", "recommendation": "อย่าใช้ลิ้นดุนแผล หากก้อนเลือดมีขนาดใหญ่กว่าปกติโดยไม่สามารถทานข้าวหรือพูดได้หรือปิดทางเดินหายใจ แนะนำให้มาพบทันตแพทย์ก่อนนัดหมายได้"},
    {"symptom_name": "มีเลือดปนน้ำมูก", "risk_level": "low", "recommendation": "ใช้ทิชชู่ซับด้านนอก ไม่สั่งน้ำมูกแรง ๆ"},
    {"symptom_name": "กินอาหารอ่อนแล้วมีเลือดซึม", "risk_level": "low", "recommendation": "ทานอาหารเหลวข้นแทนได้ เช่น โจ๊กปั่น อกไก่ปั่น ซุปฟักทอง"},
    {"symptom_name": "เลือดซึมเวลาแปรงฟัน", "risk_level": "low", "recommendation": "แปรงฟันเบา ๆ ด้วยแปรงขนนุ่ม และหลีกเลี่ยงการแปรงโดนเหงือกที่มีแผลโดยใช้น้ำเกลือฉีดล้างแทน"},
    {"symptom_name": "ยังไม่กล้าแปรงฟัน", "risk_level": "low", "recommendation": "แปรงฟันได้เบา ๆ ทุกครั้งหลังทานอาหาร และหลีกเลี่ยงการแปรงโดนเหงือกที่มีแผลโดยใช้น้ำเกลือฉีดล้างแทน"},
    {"symptom_name": "เศษอาหารติดฟัน", "risk_level": "low", "recommendation": "กลั้วปากด้วยน้ำอุ่นเพื่อให้เศษอาหารนิ่มลง หลุดง่าย และใช้ไหมขัดฟันเพื่อทำความสะอาดบริเวณซอกฟัน"},
    {"symptom_name": "เคี้ยวแล้วเจ็บ", "risk_level": "low", "recommendation": "ลดการเคี้ยวทานอาหารนิ่ม ๆ"},
    {"symptom_name": "แน่นท้องหลังกินข้าว", "risk_level": "low", "recommendation": "รับประทานอาหารเสร็จแล้วเดินย่อย อย่าพึ่งนอน และแบ่งกินมื้อละน้อยๆแต่บ่อยครั้ง"},
    {"symptom_name": "ปวดกรามเวลาฝึกอ้าปาก", "risk_level": "low", "recommendation": "ประคบอุ่นก่อนฝึกอ้าปาก"},
    {"symptom_name": "คันบริเวณที่เอาเข็มน้ำเกลือออก", "risk_level": "low", "recommendation": "หลีกเลี่ยงการเกาบริเวณที่คัน และประคบเย็นบริเวณที่เอาเข็มน้ำเกลือออก"},
    {"symptom_name": "มีน้ำเหลืองไหลออกมาจากรูจมูก", "risk_level": "medium", "recommendation": None},
    {"symptom_name": "มีแผลที่ลิ้น", "risk_level": "medium", "recommendation": None},
    {"symptom_name": "บริเวณลิ้นเป็นตุ่มใส ๆ", "risk_level": "medium", "recommendation": None},
    {"symptom_name": "มีแผลที่มุมปาก", "risk_level": "medium", "recommendation": None},
    {"symptom_name": "หูอื้อ", "risk_level": "medium", "recommendation": None},
    {"symptom_name": "จมูกไม่ได้กลิ่น", "risk_level": "medium", "recommendation": None},
    {"symptom_name": "ผื่นแดงขึ้นตามตัว", "risk_level": "medium", "recommendation": None},
    {"symptom_name": "ผื่นคัน", "risk_level": "medium", "recommendation": None},
    {"symptom_name": "ผื่นขึ้น", "risk_level": "medium", "recommendation": None},
    {"symptom_name": "อาเจียนเป็นอาหารปั่นผสมที่ให้ผ่านทางสายยาง", "risk_level": "medium", "recommendation": "ให้อาหารผ่านทางสายยางช้าลง"},
]


async def main():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        for data in SYMPTOMS:
            symptom = Symptom(
                symptom_name=data["symptom_name"],
                risk_level=data["risk_level"],
                recommendation=data.get("recommendation"),
                management_guidance=None,
                aliases=[],
            )
            session.add(symptom)
        await session.commit()
        print(f"✅ Inserted {len(SYMPTOMS)} symptoms")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
