/**
 * Form Data Types
 * Patient form data structure based on 27 questions
 */

export interface PatientFormData {
  // 1. อายุ
  age?: number;
  
  // 2. เพศ
  gender?: 'ชาย' | 'หญิง' | string;
  
  // 3. HN
  hn?: string;
  
  // 4. หัตถการที่ทำ (multiple choice)
  procedures?: string[];
  
  // 5. วันที่ผ่าตัด
  surgery_date?: string;
  
  // Note: หมายเหตุสำหรับหมอ (เหตุการณ์พิเศษ เช่น แพ้ยา เลือดออกมาก)
  note?: string;
  
  // 6. ระดับความปวด (0-10)
  pain_score?: number;
  
  // 7. ทานยาแก้ปวดแล้วดีขึ้นหรือไม่
  pain_medication_effective?: 'ดีขึ้น' | 'ไม่ดีขึ้น' | 'ไม่ได้ทานยาแก้ปวด';
  
  // 8. อาการบวม
  swelling_status?: 'ปัจจุบันหายบวมแล้ว' | 'บวมลดลง' | 'บวมเท่าเดิม' | 'บวมมากขึ้น' | 'บวมมากขึ้นมากๆจนกระทบการใช้ชีวิตประจำวัน' | string;
  swelling_description?: string;
  
  // 9. หายใจลำบาก หรือ กลืนลำบาก
  breathing_or_swallowing_difficulty?: 'ไม่มี' | 'มี' | string;
  breathing_description?: string;
  
  // 10. เลือดซึม/เลือดออก
  bleeding_status?: 'ไม่มีเลือดซึมหรือไหลแล้ว' | 'เลือดซึม แต่หยุดได้เอง' | 'เลือดสีแดงสดไหลไม่หยุดปริมาณมาก' | string;
  bleeding_description?: string;
  
  // 11. ไข้
  fever_status?: 'ไม่มีไข้' | 'มีไข้ (มากกว่า 38 องศาเซลเซียส)' | string;
  fever_description?: string;
  
  // 12. อาการชา
  numbness_status?: 'หายชาแล้วหลังทำหัตถการ' | 'ยังชาอยู่แต่ชาน้อยลงเรื่อยๆ' | 'ยังรู้สึกชาเท่ากับตอนหลังทำหัตถการทันที' | string;
  numbness_description?: string;
  
  // 13. Phlebitis (บริเวณรอยเข็ม)
  phlebitis?: 'ไม่มีอาการปวด/บวม/แดง รอบรอยเข็ม' | 'มีอาการปวด/บวม/แดง รอบรอยเข็ม' | string;
  phlebitis_description?: string;
  
  // 14. ไหมเย็บแผล
  suture_status?: 'ไหมแน่นดี / ไม่ได้สังเกต' | 'ไหมหลุดหายไปบางส่วน แต่ไม่มีเลือดไหล' | 'ไหมหลุดหายไปบางส่วน และมีอาการเลือดสีแดงสดไหล' | string;
  suture_description?: string;
  
  // 15. อาการอื่นๆ (multiple choice)
  other_symptoms?: string[];
  
  // 16. รับประทานยาฆ่าเชื้อ
  antibiotic_compliance?: 'ครบตามแพทย์สั่ง' | 'ลืมทานบางครั้ง' | 'ไม่ได้ทานเลย' | string;
  antibiotic_description?: string;
  
  // 17. ประคบ
  compress_type?: 'ประคบเย็นอยู่' | 'ประคบอุ่นอยู่' | 'ไม่ได้ประคบอะไรเลย';
  
  // 18. มัดฟัน (IMF)
  has_imf?: 'ไม่มีการมัดฟัน' | 'มีการมัดฟัน';
  
  // 19. ลวด/ยางมัดฟัน
  imf_wire_status?: 'ลวด/ยางมัดฟันแน่นดี' | 'ลวด/ยางมัดฟันหลวม อ้าปากได้เล็กน้อย' | 'ยางมัดฟันขาดไปบางเส้น แต่ยังอ้าปากไม่ได้' | string;
  imf_wire_description?: string;
  
  // 20. การเดิน (iliac crest bone graft)
  walking_status?: 'ไม่ได้ทำหัตถการ การรักษาการแหว่งของสันเหงือกโดยการนำกระดูกสะโพกมาปลูก' | 'เดินได้ปกติ' | 'เดินไม่ถนัด' | string;
  walking_description?: string;
  
  // 21. การแปรงฟัน
  brushing_teeth?: 'แปรงฟันได้' | 'แปรงฟันไม่ได้' | string;
  brushing_description?: string;
  
  // 22. การบ้วนปาก
  mouth_rinsing?: 'บ้วนปากได้' | 'บ้วนปากไม่ได้' | string;
  rinsing_description?: string;
  
  // 23. วิธีการรับประทานอาหาร
  feeding_method?: 'รับประทานอาหารผ่านกระบอกฉีดยา (syringe)' | 'รับประทานอาหารผ่านสายยาง (nasogastric tube)' | 'รับประทานอาหารได้ปกติ' | string;
  feeding_description?: string;
  
  // 24. ประเภทอาหาร (multiple choice)
  food_types?: string[];
  
  // 25. ปริมาณอาหาร
  food_amount?: 'รับประทานอาหารปริมาณปกติ' | 'รับประทานอาหารได้น้อยลง' | string;
  food_amount_description?: string;
  
  // 26. คำถามเพิ่มเติม
  additional_questions?: string;
  
  // 27. สายยางให้อาหาร (NG tube)
  ng_tube_position?: 'สายยางอยู่ในตำแหน่งเดิม,  เทปยึดจมูกกับสายแน่นดี ไม่เลื่อนหลุด' | 'สายยางเลื่อนตำแหน่ง, เทปยึดจมูกกับสายไม่แน่น, เลื่อนหลุด' | string;
  ng_tube_description?: string;
}

/**
 * Form Options Constants
 */
export const GENDER_OPTIONS = ['ชาย', 'หญิง'] as const;

export const PROCEDURE_OPTIONS = [
  'ผ่าตัดขากรรไกรบน  (Lefort I)',
  'ผ่าตัดขากรรไกรล่าง (BSSRO-bilateral sagittal split osteotomy)',
  'ผ่าตัดถอนฟัน (Surgical removal of tooth)',
  'ถอนฟัน (Extraction)',
  'การตัดชิ้นเนื้อตรวจ (Biopsy)',
  'การตัดถุงน้ำออก (Cyst Enucleation)',
  'การกรีดและระบายหนอง (Incision and drainage)',
  'การรักษาการแหว่งของสันเหงือกโดยการนำกระดูกสะโพกมาปลูก (Repair alveolar cleft with Iliac crest bone graft)',
  'ผ่าตัดปุ่มกระดูก (Torectomy)',
  'การผ่าตัดเพื่อนำแผ่นโลหะและสกรูออก (Off plate and screws)',
] as const;

export const PAIN_MEDICATION_OPTIONS = ['ดีขึ้น', 'ไม่ดีขึ้น', 'ไม่ได้ทานยาแก้ปวด'] as const;

export const SWELLING_OPTIONS = [
  'ปัจจุบันหายบวมแล้ว',
  'บวมลดลง',
  'บวมเท่าเดิม',
  'บวมมากขึ้น',
  'บวมมากขึ้นมากๆจนกระทบการใช้ชีวิตประจำวัน',
] as const;

export const BLEEDING_OPTIONS = [
  'ไม่มีเลือดซึมหรือไหลแล้ว',
  'เลือดซึม แต่หยุดได้เอง',
  'เลือดสีแดงสดไหลไม่หยุดปริมาณมาก',
] as const;

export const NUMBNESS_OPTIONS = [
  'หายชาแล้วหลังทำหัตถการ',
  'ยังชาอยู่แต่ชาน้อยลงเรื่อยๆ',
  'ยังรู้สึกชาเท่ากับตอนหลังทำหัตถการทันที',
] as const;

export const PHLEBITIS_OPTIONS = [
  'ไม่มีอาการปวด/บวม/แดง รอบรอยเข็ม',
  'มีอาการปวด/บวม/แดง รอบรอยเข็ม',
] as const;

export const SUTURE_OPTIONS = [
  'ไหมแน่นดี / ไม่ได้สังเกต',
  'ไหมหลุดหายไปบางส่วน แต่ไม่มีเลือดไหล',
  'ไหมหลุดหายไปบางส่วน และมีอาการเลือดสีแดงสดไหล',
] as const;

export const OTHER_SYMPTOMS_OPTIONS = [
  'ปวดหน่วงบริเวณหน้าแก้ม ร่วมกับมีน้ำมูกสีเหลือง/เขียว เหม็นลงคอ',
  'คลื่นไส้/อาเจียน',
  'ช้ำบริเวณแผลผ่าตัด',
  'ปวดหัว',
  'เวียนหัว',
  'น้ำหนักลด',
  'ท้องเสีย',
  'คัดแน่นจมูก',
  'มีน้ำมูก',
  'ไอ',
  'เจ็บคอ',
] as const;

export const ANTIBIOTIC_OPTIONS = [
  'ครบตามแพทย์สั่ง',
  'ลืมทานบางครั้ง',
  'ไม่ได้ทานเลย',
] as const;

export const COMPRESS_OPTIONS = [
  'ประคบเย็นอยู่',
  'ประคบอุ่นอยู่',
  'ไม่ได้ประคบอะไรเลย',
] as const;

export const IMF_OPTIONS = [
  'ไม่มีการมัดฟัน',
  'มีการมัดฟัน',
] as const;

export const IMF_WIRE_OPTIONS = [
  'ลวด/ยางมัดฟันแน่นดี',
  'ลวด/ยางมัดฟันหลวม อ้าปากได้เล็กน้อย',
  'ยางมัดฟันขาดไปบางเส้น แต่ยังอ้าปากไม่ได้',
] as const;

export const WALKING_OPTIONS = [
  'ไม่ได้ทำหัตถการ การรักษาการแหว่งของสันเหงือกโดยการนำกระดูกสะโพกมาปลูก',
  'เดินได้ปกติ',
  'เดินไม่ถนัด',
] as const;

export const FEEDING_METHOD_OPTIONS = [
  'รับประทานอาหารผ่านกระบอกฉีดยา (syringe)',
  'รับประทานอาหารผ่านสายยาง (nasogastric tube)',
  'รับประทานอาหารได้ปกติ',
] as const;

export const FOOD_AMOUNT_OPTIONS = [
  'รับประทานอาหารปริมาณปกติ',
  'รับประทานอาหารได้น้อยลง',
] as const;

export const NG_TUBE_OPTIONS = [
  'สายยางอยู่ในตำแหน่งเดิม,  เทปยึดจมูกกับสายแน่นดี ไม่เลื่อนหลุด',
  'สายยางเลื่อนตำแหน่ง, เทปยึดจมูกกับสายไม่แน่น, เลื่อนหลุด',
] as const;
