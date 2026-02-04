/**
 * Symptom Key Mappings
 * Centralized mapping between symptom keys and their labels (TH/EN)
 */

export interface SymptomOption {
  key: string;
  labelTH: string;
  labelEN: string;
}

// Other Symptoms Mappings
export const OTHER_SYMPTOMS_MAPPINGS: SymptomOption[] = [
  {
    key: 'sinus_pain',
    labelTH: 'ปวดหน่วงบริเวณหน้าแก้ม ร่วมกับมีน้ำมูกสีเหลือง/เขียว เหม็นลงคอ',
    labelEN: 'Cheek pain with yellow/green mucus and bad smell'
  },
  {
    key: 'nausea_vomiting',
    labelTH: 'คลื่นไส้/อาเจียน',
    labelEN: 'Nausea/Vomiting'
  },
  {
    key: 'bruising',
    labelTH: 'ช้ำ',
    labelEN: 'Bruising'
  },
  {
    key: 'headache',
    labelTH: 'ปวดหัว',
    labelEN: 'Headache'
  },
  {
    key: 'dizziness',
    labelTH: 'เวียนหัว',
    labelEN: 'Dizziness'
  },
  {
    key: 'weight_loss',
    labelTH: 'น้ำหนักลด',
    labelEN: 'Weight loss'
  },
  {
    key: 'diarrhea',
    labelTH: 'ท้องเสีย',
    labelEN: 'Diarrhea'
  },
  {
    key: 'stuffy_nose',
    labelTH: 'คัดแน่นจมูก',
    labelEN: 'Stuffy nose'
  },
  {
    key: 'runny_nose',
    labelTH: 'มีน้ำมูก',
    labelEN: 'Runny nose'
  },
  {
    key: 'cough',
    labelTH: 'ไอ',
    labelEN: 'Cough'
  },
  {
    key: 'sore_throat',
    labelTH: 'เจ็บคอ',
    labelEN: 'Sore throat'
  },
];

// Helper functions
export const getSymptomLabel = (key: string, language: 'th' | 'en'): string => {
  const symptom = OTHER_SYMPTOMS_MAPPINGS.find(s => s.key === key);
  if (!symptom) return key;
  return language === 'en' ? symptom.labelEN : symptom.labelTH;
};

export const getSymptomKey = (label: string): string => {
  const symptom = OTHER_SYMPTOMS_MAPPINGS.find(
    s => s.labelTH === label || s.labelEN === label
  );
  return symptom?.key || label;
};

export const getSymptomKeys = (): string[] => {
  return OTHER_SYMPTOMS_MAPPINGS.map(s => s.key);
};

export const getSymptomLabels = (language: 'th' | 'en'): string[] => {
  return OTHER_SYMPTOMS_MAPPINGS.map(s => 
    language === 'en' ? s.labelEN : s.labelTH
  );
};
