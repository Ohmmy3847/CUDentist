/** Maps stored Thai symptom values → English display strings. */
export const SYMPTOM_VALUE_EN: Record<string, string> = {
  // Pain medication effect
  'ดีขึ้น': 'Better',
  'ไม่ดีขึ้น': 'Not better',
  'ไม่ได้ทานยาแก้ปวด': 'Did not take painkillers',

  // Swelling
  'ปัจจุบันหายบวมแล้ว': 'Swelling resolved',
  'บวมลดลง': 'Swelling reduced',
  'บวมเท่าเดิม': 'No change in swelling',
  'บวมมากขึ้น': 'Increased swelling',
  'บวมมากขึ้นมากๆจนกระทบการใช้ชีวิตประจำวัน': 'Severe swelling affecting daily life',

  // Breathing/swallowing
  'ไม่มี': 'None',
  'มี': 'Yes',

  // Bleeding
  'ไม่มีเลือดซึมหรือไหลแล้ว': 'No bleeding',
  'เลือดซึม แต่หยุดได้เอง': 'Slight oozing, stopped on its own',
  'เลือดสีแดงสดไหลไม่หยุดปริมาณมาก': 'Heavy bright-red bleeding, not stopping',

  // Fever
  'ไม่มีไข้': 'No fever',
  'มีไข้ (มากกว่า 38 องศาเซลเซียส)': 'Fever (> 38°C)',

  // Numbness
  'หายชาแล้วหลังทำหัตถการ': 'Resolved after procedure',
  'ยังชาอยู่แต่ชาน้อยลงเรื่อยๆ': 'Still numb but improving',
  'ยังรู้สึกชาเท่ากับตอนหลังทำหัตถการทันที': 'Same as right after procedure',

  // Phlebitis
  'ไม่มีอาการปวด/บวม/แดง รอบรอยเข็ม': 'No pain/swelling/redness at needle site',
  'มีอาการปวด/บวม/แดง รอบรอยเข็ม': 'Pain/swelling/redness at needle site',

  // Suture
  'ไหมแน่นดี / ไม่ได้สังเกต': 'Sutures intact / not observed',
  'ไหมหลุดหายไปบางส่วน แต่ไม่มีเลือดไหล': 'Some sutures loose, no bleeding',
  'ไหมหลุดหายไปบางส่วน และมีอาการเลือดสีแดงสดไหล': 'Sutures loose with active bleeding',

  // Antibiotic
  'ครบตามแพทย์สั่ง': 'Taken as prescribed',
  'ลืมทานบางครั้ง': 'Missed some doses',
  'ไม่ได้ทานเลย': 'Not taken at all',

  // Compress
  'ประคบเย็นอยู่': 'Cold compress',
  'ประคบอุ่นอยู่': 'Warm compress',
  'ไม่ได้ประคบอะไรเลย': 'No compress',
  'ประคบสลับ': 'Alternating compress',

  // IMF / wire
  'ลวด/ยางมัดฟันแน่นดี': 'Wire/rubber bands intact',
  'ลวด/ยางมัดฟันหลวม อ้าปากได้เล็กน้อย': 'Loose, can open slightly',
  'ยางมัดฟันขาดไปบางเส้น แต่ยังอ้าปากไม่ได้': 'Some rubber bands broken, still cannot open',

  // Walking
  'เดินได้ปกติ': 'Normal',
  'เดินไม่ถนัด': 'Difficulty walking',

  // Brushing
  'แปรงได้ปกติ': 'Normal brushing',
  'แปรงฟันไม่ถนัด': 'Difficulty brushing',
  'แปรงฟันไม่ได้เลย': 'Cannot brush',

  // Rinsing
  'บ้วนปากได้': 'Can rinse',
  'บ้วนปากไม่ได้': 'Cannot rinse',

  // Food amount
  'รับประทานอาหารปริมาณปกติ': 'Normal amount',
  'รับประทานอาหารได้น้อยกว่าปกติ': 'Less than normal',
  'รับประทานอาหารได้น้อยมาก': 'Very little',
  'ไม่สามารถรับประทานอาหารได้เลย': 'Cannot eat at all',

  // NG tube
  'สายอยู่ครบ': 'Tube intact',
  'สายหลุดหรือเลื่อน': 'Tube dislodged or shifted',

  // Other symptoms
  'ปวดหน่วงบริเวณหน้าแก้ม ร่วมกับมีน้ำมูกสีเหลือง/เขียว เหม็นลงคอ': 'Cheek pain with yellow/green nasal discharge',
  'คลื่นไส้/อาเจียน': 'Nausea/Vomiting',
  'ช้ำ': 'Bruising',
  'ปวดหัว': 'Headache',
  'เวียนหัว': 'Dizziness',
  'น้ำหนักลด': 'Weight loss',
  'ท้องเสีย': 'Diarrhea',
  'คัดแน่นจมูก': 'Stuffy nose',
  'มีน้ำมูก': 'Runny nose',
  'ไอ': 'Cough',
  'เจ็บคอ': 'Sore throat',

  // Boolean-like
  'ใช่': 'Yes',
  'ไม่ใช่': 'No',
}
