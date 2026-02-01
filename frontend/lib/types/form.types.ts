/**
 * Form Data Types
 * Patient form data structure based on 27 questions
 */

export interface PatientFormData {
  // ข้อมูลส่วนตัว
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  birth_year?: number;

  // 1. อายุ
  age?: number;

  // 2. เพศ
  gender?: 'ชาย' | 'หญิง' | string;

  // 3. HN
  hn?: string;

  // 4. หัตถการที่ทำ (multiple choice)
  procedures?: string[];

  // 4.1 Sub-options สำหรับ Lefort I
  lefort_sub_options?: string[];  // advancement, setback, impaction, etc.

  // 4.2 Sub-options สำหรับ BSSRO
  bssro_sub_options?: string[];  // setback, advancement, rotation

  // 4.3 หมายเลขซี่ฟันสำหรับผ่าตัดถอนฟัน
  surgical_tooth_numbers?: string;

  // 4.4 หมายเลขซี่ฟันสำหรับถอนฟัน
  extraction_tooth_numbers?: string;

  // 4.5 Sub-options สำหรับ Biopsy
  biopsy_sub_options?: string[];  // excisional, incisional, enucleation

  // 5. วันที่ผ่าตัด
  surgery_date?: string;

  // 5.1 วันที่ discharge
  discharge_date?: string;


  // 6. Special Procedures (หัตถการย่อยที่ทำ)
  has_imf?: 'มีการมัดฟัน' | 'ไม่มีการมัดฟัน';
  imf_type?: 'มัดลวด' | 'มัดยาง';
  imf_wire?: boolean;  // IMF มัดลวด
  imf_elastic?: boolean;  // IMF มัดยาง
  imf_loops?: number;

  special_icbg?: 'มี' | 'ไม่ทำ';
  special_icbg_description?: string;

  special_ng_tube?: 'มี' | 'ไม่ทำ';
  special_ng_tube_description?: string;

  // Note: หมายเหตุสำหรับหมอ (เหตุการณ์พิเศษ เช่น แพ้ยา เลือดออกมาก)
  note?: string;

  // 6. ระดับความปวด (0-10)
  pain_score?: number;
  pain_description?: string;
  pain_score_description?: string;

  // 7. ทานยาแก้ปวดแล้วดีขึ้นหรือไม่
  pain_medication_effect?: 'ดีขึ้น' | 'ไม่ดีขึ้น' | 'ไม่ได้ทานยาแก้ปวด';

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
  other_symptoms_custom?: string[]; // Custom free text array

  // 16. รับประทานยาฆ่าเชื้อ
  antibiotic_compliance?: 'ครบตามแพทย์สั่ง' | 'ลืมทานบางครั้ง' | 'ไม่ได้ทานเลย' | string;
  antibiotic_description?: string;

  // 17. ประคบ
  compress_type?: 'ประคบเย็นอยู่' | 'ประคบอุ่นอยู่' | 'ไม่ได้ประคบอะไรเลย';

  // 19. ลวด/ยางมัดฟัน
  imf_wire_status?: 'ลวด/ยางมัดฟันแน่นดี' | 'ลวด/ยางมัดฟันหลวม อ้าปากได้เล็กน้อย' | 'ยางมัดฟันขาดไปบางเส้น แต่ยังอ้าปากไม่ได้' | string;
  imf_wire_description?: string;

  // 20. การเดิน (iliac crest bone graft)
  walking_status?: 'เดินได้ปกติ' | 'เดินไม่ถนัด' | string;
  walking_description?: string;

  // 21. การแปรงฟัน
  brushing_teeth?: 'แปรงฟันได้' | 'แปรงฟันไม่ถนัด' | string;
  brushing_description?: string;

  // 22. การบ้วนปาก
  mouth_rinsing?: 'บ้วนปากได้' | 'บ้วนปากไม่ได้' | string;
  rinsing_description?: string;

  // 23. วิธีการรับประทานอาหาร
  feeding_method?: 'รับประทานอาหารผ่านกระบอกฉีดยา (syringe)' | 'รับประทานอาหารผ่านสายยาง (nasogastric tube)' | 'รับประทานอาหารได้ปกติ' | string;
  feeding_description?: string;

  // 24. ประเภทอาหาร (multiple choice)
  food_types?: string[];
  food_types_custom?: string[]; // Custom free text array

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
  'ช้ำ',
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
  'เดินได้ปกติ',
  'เดินไม่ถนัด',
] as const;

export const FEEDING_METHOD_OPTIONS = [
  'รับประทานอาหารผ่านกระบอกฉีดยา (syringe)',
  'รับประทานอาหารผ่านสายยาง (nasogastric tube)',
  'รับประทานอาหารได้ปกติ',
] as const;

export const FOOD_TYPE_OPTIONS = [
  'อาหารเหลวใสไม่มีกาก เช่น น้ำซุปใส น้ำผลไม้กรอง นม',
  'อาหารปั่นเหลวมีกาก เช่น โจ๊กปั่นเหลว ไก่ปั่น',
  'อาหารอ่อน เช่น โจ๊ก ข้าวต้ม ไข่ลวก ผักนึ่ง',
  'อาหารปกติแต่เว้นอาหารรสจัด เผ็ด ร้อน แข็ง เหนียว',
] as const;

export const FOOD_AMOUNT_OPTIONS = [
  'รับประทานอาหารปริมาณปกติ',
  'รับประทานอาหารได้น้อยลง',
] as const;

export const NG_TUBE_OPTIONS = [
  'สายยางอยู่ในตำแหน่งเดิม,  เทปยึดจมูกกับสายแน่นดี ไม่เลื่อนหลุด',
  'สายยางเลื่อนตำแหน่ง, เทปยึดจมูกกับสายไม่แน่น, เลื่อนหลุด',
] as const;

// Procedure Sub-options
export const LEFORT_SUB_OPTIONS = [
  'advancement',
  'setback',
  'osteotomy',
  '2pieces',
  'impaction',
  'correct midline',
  'correct canting',
] as const;

export const BSSRO_SUB_OPTIONS = [
  'setback',
  'advancement',
  'rotation',
] as const;
