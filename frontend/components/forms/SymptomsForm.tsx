import React from 'react';
import { Plus, X } from 'lucide-react';
import type { PatientFormData } from '@/lib';
import {
  PAIN_MEDICATION_OPTIONS,
  SWELLING_OPTIONS,
  BLEEDING_OPTIONS,
  NUMBNESS_OPTIONS,
  PHLEBITIS_OPTIONS,
  SUTURE_OPTIONS,
  OTHER_SYMPTOMS_OPTIONS,
  ANTIBIOTIC_OPTIONS,
  COMPRESS_OPTIONS,
  IMF_WIRE_OPTIONS,
  WALKING_OPTIONS,
} from '@/lib';
import { getSymptomLabel } from '@/lib/symptomMappings';
import { th, en } from '@/lib/locales';

interface SymptomsFormProps {
  data: PatientFormData;
  onChange: (data: Partial<PatientFormData>) => void;
  onValidationChange?: (isValid: boolean) => void;
  startingQuestionNumber?: number;
  lang?: 'th' | 'en';
}

export function validateSymptoms(_data: PatientFormData): boolean {
  // const hasIMF = data.imf_wire || data.imf_elastic;
  // const hasPain = (data.pain_score || 0) > 0;
  // const forgotAntibiotic = data.antibiotic_compliance === 'ลืมทานบางครั้ง';

  // return !!(
  //   data.pain_score !== undefined &&
  //   (!hasPain || data.pain_medication_effect) &&
  //   data.swelling_status &&
  //   data.breathing_or_swallowing_difficulty &&
  //   data.bleeding_status &&
  //   data.fever_status &&
  //   data.numbness_status &&
  //   data.phlebitis &&
  //   data.suture_status &&
  //   data.antibiotic_compliance &&
  //   (!forgotAntibiotic || data.antibiotic_description) &&
  //   data.compress_type &&
  //   (!hasIMF || data.imf_wire_status) &&
  //   data.walking_status
  // );
  return true
}

// Helper to map Thai values to English display


export default function SymptomsForm({
  data,
  onChange,
  onValidationChange,
  startingQuestionNumber = 5,
  lang = 'th'
}: SymptomsFormProps) {
  const t = lang === 'th' ? th.form.symptoms : en.form.symptoms;

  const getOptionLabel = (option: string): string => {
    if (lang === 'th') return option;

    const map: Record<string, string> = {
      // Pain Med
      'ดีขึ้น': t.painMed.better,
      'ไม่ดีขึ้น': t.painMed.notBetter,
      'ไม่ได้ทานยาแก้ปวด': t.painMed.notTaken,

      // Swelling
      'ปัจจุบันหายบวมแล้ว': t.swelling.gone,
      'บวมลดลง': t.swelling.reduced,
      'บวมเท่าเดิม': t.swelling.noChange,
      'บวมมากขึ้น': t.swelling.increased,
      'บวมมากขึ้นมากๆจนกระทบการใช้ชีวิตประจำวัน': t.swelling.severe,

      // Breathing
      'ไม่มี': t.breathing.no,
      'มี': t.breathing.yes,

      // Bleeding
      'ไม่มีเลือดซึมหรือไหลแล้ว': t.bleeding.no,
      'เลือดซึม แต่หยุดได้เอง': t.bleeding.slight,
      'เลือดสีแดงสดไหลไม่หยุดปริมาณมาก': t.bleeding.heavy,

      // Fever
      'ไม่มีไข้': t.fever.no,
      'มีไข้ (มากกว่า 38 องศาเซลเซียส)': t.fever.yes,

      // Numbness
      'หายชาแล้วหลังทำหัตถการ': t.numbness.resolved,
      'ยังชาอยู่แต่ชาน้อยลงเรื่อยๆ': t.numbness.improving,
      'ยังรู้สึกชาเท่ากับตอนหลังทำหัตถการทันที': t.numbness.unchanged,

      // Phlebitis
      'ไม่มีอาการปวด/บวม/แดง รอบรอยเข็ม': t.phlebitis.no,
      'มีอาการปวด/บวม/แดง รอบรอยเข็ม': t.phlebitis.yes,

      // Suture
      'ไหมแน่นดี / ไม่ได้สังเกต': t.suture.secure,
      'ไหมหลุดหายไปบางส่วน แต่ไม่มีเลือดไหล': t.suture.loose,
      'ไหมหลุดหายไปบางส่วน และมีอาการเลือดสีแดงสดไหล': t.suture.bleeding,

      // Antibiotic
      'ครบตามแพทย์สั่ง': t.antibiotic.all,
      'ลืมทานบางครั้ง': t.antibiotic.missed,
      'ไม่ได้ทานเลย': t.antibiotic.none,

      // Compress
      'ประคบเย็นอยู่': t.compress.cold,
      'ประคบอุ่นอยู่': t.compress.warm,
      'ไม่ได้ประคบอะไรเลย': t.compress.none,

      // IMF
      'ลวด/ยางมัดฟันแน่นดี': t.imfWire.tight,
      'ลวด/ยางมัดฟันหลวม อ้าปากได้เล็กน้อย': t.imfWire.loose,
      'ยางมัดฟันขาดไปบางเส้น แต่ยังอ้าปากไม่ได้': t.imfWire.broken,

      // Walking
      'เดินได้ปกติ': t.walking.normal,
      'เดินไม่ถนัด': t.walking.difficult,

      // Other Symptoms
      'ปวดหน่วงบริเวณหน้าแก้ม ร่วมกับมีน้ำมูกสีเหลือง/เขียว เหม็นลงคอ': 'Cheek pain with yellow/green discharge',
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
    };

    return map[option] || option;
  };

  const [customSymptoms, setCustomSymptoms] = React.useState<Array<{ symptom: string, detail: string }>>([]);

  // Sync customSymptoms from data.other_symptoms_custom when component mounts or data changes
  React.useEffect(() => {
    if (
      data.other_symptoms_custom &&
      data.other_symptoms_custom.length > 0 &&
      customSymptoms.length === 0
    ) {
      setCustomSymptoms(data.other_symptoms_custom);
    }
  }, [data.other_symptoms_custom, customSymptoms.length]);

  // Clear conditional fields when parent field changes
  React.useEffect(() => {
    const hasPain = (data.pain_score || 0) > 0;
    const hasIMF = data.imf_wire || data.imf_elastic;
    const forgotAntibiotic = data.antibiotic_compliance === 'ลืมทานบางครั้ง';

    const updates: Partial<PatientFormData> = {};

    if (!hasPain && data.pain_medication_effect) {
      updates.pain_medication_effect = undefined;
    }
    if (data.pain_score === undefined && data.pain_score_description) {
      updates.pain_score_description = undefined;
    }
    if (!hasIMF && (data.imf_wire_status || data.imf_wire_description)) {
      updates.imf_wire_status = undefined;
      updates.imf_wire_description = undefined;
    }
    if (!forgotAntibiotic && data.antibiotic_description) {
      updates.antibiotic_description = undefined;
    }
    if (!data.swelling_status && data.swelling_description) {
      updates.swelling_description = undefined;
    }
    if (!data.breathing_or_swallowing_difficulty && data.breathing_description) {
      updates.breathing_description = undefined;
    }
    if (!data.bleeding_status && data.bleeding_description) {
      updates.bleeding_description = undefined;
    }
    if (!data.fever_status && data.fever_description) {
      updates.fever_description = undefined;
    }
    if (!data.numbness_status && data.numbness_description) {
      updates.numbness_description = undefined;
    }
    if (!data.phlebitis && data.phlebitis_description) {
      updates.phlebitis_description = undefined;
    }
    if (!data.suture_status && data.suture_description) {
      updates.suture_description = undefined;
    }
    if (!data.walking_status && data.walking_description) {
      updates.walking_description = undefined;
    }

    if (Object.keys(updates).length > 0) {
      onChange(updates);
    }
  }, [
    data.pain_score,
    data.imf_wire,
    data.imf_elastic,
    data.antibiotic_compliance,
    data.antibiotic_description,
    data.swelling_status,
    data.swelling_description,
    data.breathing_or_swallowing_difficulty,
    data.breathing_description,
    data.bleeding_status,
    data.bleeding_description,
    data.fever_status,
    data.fever_description,
    data.numbness_status,
    data.numbness_description,
    data.phlebitis,
    data.phlebitis_description,
    data.suture_status,
    data.suture_description,
    data.walking_status,
    data.walking_description,
    data.imf_wire_status,
    data.imf_wire_description,
    data.pain_score_description,
    data.pain_medication_effect,
    onChange
  ]);

  React.useEffect(() => {
    if (onValidationChange) {
      onValidationChange(validateSymptoms(data));
    }
  }, [data, onValidationChange]);

  const handleOtherSymptomsChange = (symptom: string, checked: boolean) => {
    const current = data.other_symptoms || [];
    const updated = checked
      ? [...current, symptom]
      : current.filter(s => s !== symptom);
    onChange({ other_symptoms: updated });
  };

  const handleAddSymptomField = () => {
    if (customSymptoms.length === 0 || (customSymptoms[customSymptoms.length - 1].symptom.trim() !== '' || customSymptoms[customSymptoms.length - 1].detail.trim() !== '')) {
      setCustomSymptoms([...customSymptoms, { symptom: '', detail: '' }]);
    }
  };

  const handleRemoveSymptomField = (index: number) => {
    const updated = customSymptoms.filter((_, i) => i !== index);

    setCustomSymptoms(updated);

    // กรองเฉพาะอันที่มีข้อมูลจริง
    const filtered = updated.filter(
      s => s.symptom.trim() || s.detail.trim()
    );

    onChange({
      other_symptoms_custom: filtered,
    });
  }

  const handleCustomSymptomChange = (
    index: number,
    field: 'symptom' | 'detail',
    value: string
  ) => {
    const updatedCustom = [...customSymptoms];

    updatedCustom[index] = {
      ...updatedCustom[index],
      [field]: value,
    };

    setCustomSymptoms(updatedCustom);

    // กรองเฉพาะอันที่มีข้อมูลจริง
    const filtered = updatedCustom.filter(
      s => s.symptom.trim() || s.detail.trim()
    );

    onChange({
      other_symptoms_custom: filtered,
    });
  }

  // Dynamic question numbering
  const questionNumbers = React.useMemo(() => {
    let num = startingQuestionNumber;
    const numbers: Record<string, number> = {};

    numbers.pain = ++num;
    if ((data.pain_score || 0) > 0) numbers.painMed = ++num;
    numbers.swelling = ++num;
    numbers.breathing = ++num;
    numbers.bleeding = ++num;
    numbers.fever = ++num;
    numbers.numbness = ++num;
    numbers.phlebitis = ++num;
    numbers.suture = ++num;
    numbers.otherSymptoms = ++num;
    numbers.antibiotic = ++num;
    numbers.compress = ++num;

    if (data.imf_wire || data.imf_elastic) numbers.imfWire = ++num;
    if (data.special_icbg) numbers.walking = ++num;

    return numbers;
  }, [startingQuestionNumber, data.pain_score, data.imf_wire, data.imf_elastic, data.special_icbg]);

  return (
    <div className="space-y-6">
      <h2 className="text-xl sm:text-2xl font-bold text-gray-800 mb-6">
        {t.title}
      </h2>

      {/* Pain Score */}
      <div>
        <label className="block text-gray-700 font-medium mb-3">
          {questionNumbers.pain}. {t.pain.label} <span className="text-red-500">*</span>
        </label>
        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs sm:text-sm text-gray-600 mb-2">
            <span>{t.pain.min}</span>
            <span className="text-right">{t.pain.max}</span>
          </div>
          <div className="grid grid-cols-11 gap-1 sm:gap-2">
            {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(score => (
              <button
                key={score}
                type="button"
                onClick={() => onChange({ pain_score: score })}
                className={`
                  h-12 sm:h-14 md:h-16 flex items-center justify-center rounded-lg font-bold text-sm sm:text-base md:text-lg transition-all
                  ${data.pain_score === score
                    ? 'bg-blue-600 text-white shadow-lg scale-105 sm:scale-110'
                    : 'bg-gray-100 text-gray-700 hover:bg-blue-100 hover:text-blue-600'
                  }
                `}
              >
                {score}
              </button>
            ))}
          </div>
        </div>
        <div className="text-center mt-3">
          {data.pain_score !== undefined ? (
            <>
              <span className="text-3xl font-bold text-blue-600">{data.pain_score}</span>
              <span className="text-gray-600"> / 10</span>
            </>
          ) : (
            <span className="text-gray-400">-</span>
          )}
        </div>

        {data.pain_score !== undefined && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              {t.pain.desc}
            </label>
            <textarea
              value={data.pain_score_description || ''}
              onChange={(e) => onChange({ pain_score_description: e.target.value })}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
              rows={1}
            />
          </div>
        )}
      </div>

      {/* Pain Medication Effect (Conditional) */}
      {(data.pain_score || 0) > 0 && (
        <div className="animate-in fade-in slide-in-from-top-2">
          <label className="block text-sm sm:text-base text-gray-700 font-medium mb-2">
            {questionNumbers.painMed}. {t.painMed.label} <span className="text-red-500">*</span>
          </label>
          <div className="space-y-2">
            {PAIN_MEDICATION_OPTIONS.map(option => (
              <label key={option} className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  name="pain_medication"
                  value={option}
                  checked={data.pain_medication_effect === option}
                  onChange={(e) => onChange({ pain_medication_effect: e.target.value as typeof data.pain_medication_effect })}
                  className="w-4 h-4 text-blue-600"
                />
                <span className="ml-2 text-sm sm:text-base text-gray-700">{getOptionLabel(option)}</span>
              </label>
            ))}
          </div>

          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              {t.painMed.desc}
            </label>
            <textarea
              value={data.pain_description || ''}
              onChange={(e) => onChange({ pain_description: e.target.value })}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
              rows={1}
            />
          </div>
        </div>
      )}

      {/* Swelling */}
      <div>
        <label className="block text-sm sm:text-base text-gray-700 font-medium mb-2">
          {questionNumbers.swelling}. {t.swelling.label} <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {SWELLING_OPTIONS.map(option => (
            <label key={option} className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="swelling"
                value={option}
                checked={data.swelling_status === option}
                onChange={(e) => onChange({ swelling_status: e.target.value as typeof data.swelling_status })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-sm sm:text-base text-gray-700">{getOptionLabel(option)}</span>
            </label>
          ))}
        </div>
        {data.swelling_status && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              {t.swelling.desc}
            </label>
            <textarea
              value={data.swelling_description || ''}
              onChange={(e) => onChange({ swelling_description: e.target.value })}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
              rows={1}
            />
          </div>
        )}
      </div>

      {/* Breathing */}
      <div>
        <label className="block text-sm sm:text-base text-gray-700 font-medium mb-2">
          {questionNumbers.breathing}. {t.breathing.label} <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              name="breathing"
              value="ไม่มี"
              checked={data.breathing_or_swallowing_difficulty === 'ไม่มี'}
              onChange={(e) => onChange({ breathing_or_swallowing_difficulty: e.target.value })}
              className="w-4 h-4 text-blue-600"
            />
            <span className="ml-2 text-sm sm:text-base text-gray-700">{t.breathing.no}</span>
          </label>
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              name="breathing"
              value="มี"
              checked={data.breathing_or_swallowing_difficulty === 'มี'}
              onChange={(e) => onChange({ breathing_or_swallowing_difficulty: e.target.value })}
              className="w-4 h-4 text-blue-600"
            />
            <span className="ml-2 text-sm sm:text-base text-gray-700">{t.breathing.yes}</span>
          </label>
        </div>
        {data.breathing_or_swallowing_difficulty && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              {t.breathing.desc}
            </label>
            <textarea
              value={data.breathing_description || ''}
              onChange={(e) => onChange({ breathing_description: e.target.value })}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
              rows={1}
            />
          </div>
        )}
      </div>

      {/* Bleeding */}
      <div>
        <label className="block text-sm sm:text-base text-gray-700 font-medium mb-2">
          {questionNumbers.bleeding}. {t.bleeding.label} <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {BLEEDING_OPTIONS.map(option => (
            <label key={option} className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="bleeding"
                value={option}
                checked={data.bleeding_status === option}
                onChange={(e) => onChange({ bleeding_status: e.target.value as typeof data.bleeding_status })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-sm sm:text-base text-gray-700">{getOptionLabel(option)}</span>
            </label>
          ))}
        </div>
        {data.bleeding_status && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              {t.bleeding.desc}
            </label>
            <textarea
              value={data.bleeding_description || ''}
              onChange={(e) => onChange({ bleeding_description: e.target.value })}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
              rows={1}
            />
          </div>
        )}
      </div>

      {/* Fever */}
      <div>
        <label className="block text-sm sm:text-base text-gray-700 font-medium mb-2">
          {questionNumbers.fever}. {t.fever.label} <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              name="fever"
              value="ไม่มีไข้"
              checked={data.fever_status === 'ไม่มีไข้'}
              onChange={(e) => onChange({ fever_status: e.target.value })}
              className="w-4 h-4 text-blue-600"
            />
            <span className="ml-2 text-sm sm:text-base text-gray-700">{t.fever.no}</span>
          </label>
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              name="fever"
              value="มีไข้ (มากกว่า 38 องศาเซลเซียส)"
              checked={data.fever_status === 'มีไข้ (มากกว่า 38 องศาเซลเซียส)'}
              onChange={(e) => onChange({ fever_status: e.target.value })}
              className="w-4 h-4 text-blue-600"
            />
            <span className="ml-2 text-sm sm:text-base text-gray-700">{t.fever.yes}</span>
          </label>
        </div>
        {data.fever_status && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              {t.fever.desc}
            </label>
            <textarea
              value={data.fever_description || ''}
              onChange={(e) => onChange({ fever_description: e.target.value })}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
              rows={1}
            />
          </div>
        )}
      </div>

      {/* Numbness */}
      <div>
        <label className="block text-sm sm:text-base text-gray-700 font-medium mb-2">
          {questionNumbers.numbness}. {t.numbness.label} <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {NUMBNESS_OPTIONS.map(option => (
            <label key={option} className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="numbness"
                value={option}
                checked={data.numbness_status === option}
                onChange={(e) => onChange({ numbness_status: e.target.value as typeof data.numbness_status })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-sm sm:text-base text-gray-700">{getOptionLabel(option)}</span>
            </label>
          ))}
        </div>
        {data.numbness_status && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              {t.numbness.desc}
            </label>
            <textarea
              value={data.numbness_description || ''}
              onChange={(e) => onChange({ numbness_description: e.target.value })}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
              placeholder={t.numbness.desc}
              rows={1}
            />
          </div>
        )}
      </div>

      {/* Phlebitis */}
      <div>
        <label className="block text-sm sm:text-base text-gray-700 font-medium mb-2">
          {questionNumbers.phlebitis}. {t.phlebitis.label} <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {PHLEBITIS_OPTIONS.map(option => (
            <label key={option} className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="phlebitis"
                value={option}
                checked={data.phlebitis === option}
                onChange={(e) => onChange({ phlebitis: e.target.value as typeof data.phlebitis })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-sm sm:text-base text-gray-700">{getOptionLabel(option)}</span>
            </label>
          ))}
        </div>
        {data.phlebitis && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              {t.phlebitis.desc}
            </label>
            <textarea
              value={data.phlebitis_description || ''}
              onChange={(e) => onChange({ phlebitis_description: e.target.value })}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
              rows={1}
            />
          </div>
        )}
      </div>

      {/* Suture */}
      <div>
        <label className="block text-sm sm:text-base text-gray-700 font-medium mb-2">
          {questionNumbers.suture}. {t.suture.label} <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {SUTURE_OPTIONS.map(option => (
            <label key={option} className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="suture"
                value={option}
                checked={data.suture_status === option}
                onChange={(e) => onChange({ suture_status: e.target.value as typeof data.suture_status })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-sm sm:text-base text-gray-700">{getOptionLabel(option)}</span>
            </label>
          ))}
        </div>
        {data.suture_status && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              {t.suture.desc}
            </label>
            <textarea
              value={data.suture_description || ''}
              onChange={(e) => onChange({ suture_description: e.target.value })}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
              rows={1}
            />
          </div>
        )}
      </div>

      {/* Other Symptoms */}
      <div>
        <label className="block text-sm sm:text-base text-gray-700 font-medium mb-2">
          {questionNumbers.otherSymptoms}. {t.other.label}
        </label>
        <div className="space-y-3 border border-gray-200 rounded-lg p-4">
          {OTHER_SYMPTOMS_OPTIONS.filter(key => key !== 'dizziness').map(key => (
            <label key={key} className="flex items-start cursor-pointer">
              <input
                type="checkbox"
                checked={data.other_symptoms?.includes(key) || false}
                onChange={(e) => handleOtherSymptomsChange(key, e.target.checked)}
                className="w-4 h-4 text-blue-600 mt-1"
              />
              <span className="ml-2 text-sm sm:text-base text-gray-700">{getSymptomLabel(key, lang)}</span>
            </label>
          ))}

          {/* Custom Symptoms */}
          <div className="mt-4 pt-4 border-t border-gray-200">
            <label className="block text-gray-700 font-medium mb-3">{t.other.customLabel}</label>
            <div className="space-y-3">
              {customSymptoms.map((symptom, index) => (
                <div key={index} className="flex flex-col sm:flex-row items-start gap-2">
                  <input
                    type="text"
                    value={symptom.symptom || ''}
                    onChange={(e) => handleCustomSymptomChange(index, 'symptom', e.target.value)}
                    className="w-full sm:w-1/3 px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                    placeholder={t.other.namePlaceholder}
                  />
                  <input
                    type="text"
                    value={symptom.detail || ''}
                    onChange={(e) => handleCustomSymptomChange(index, 'detail', e.target.value)}
                    className="w-full flex-1 px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                    placeholder={t.other.descPlaceholder}
                  />
                  <button
                    type="button"
                    onClick={() => handleRemoveSymptomField(index)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors self-end sm:self-auto"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              ))}
              <button
                type="button"
                onClick={handleAddSymptomField}
                className="flex items-center gap-2 px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-medium"
              >
                <Plus className="w-5 h-5" />
                {customSymptoms.length === 0
                  ? t.other.add
                  : t.other.add
                }
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Antibiotic */}
      <div>
        <label className="block text-sm sm:text-base text-gray-700 font-medium mb-2">
          {questionNumbers.antibiotic}. {t.antibiotic.label} <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {ANTIBIOTIC_OPTIONS.map(option => (
            <label key={option} className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="antibiotic"
                value={option}
                checked={data.antibiotic_compliance === option}
                onChange={(e) => onChange({ antibiotic_compliance: e.target.value as typeof data.antibiotic_compliance })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-sm sm:text-base text-gray-700">{getOptionLabel(option)}</span>
            </label>
          ))}
        </div>

        {data.antibiotic_compliance === 'ลืมทานบางครั้ง' && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              {t.antibiotic.forgotCount} <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              min="0"
              required
              value={data.antibiotic_description || ''}
              onChange={(e) => onChange({ antibiotic_description: e.target.value })}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
            />
          </div>
        )}
      </div>

      {/* Compress */}
      <div>
        <label className="block text-sm sm:text-base text-gray-700 font-medium mb-2">
          {questionNumbers.compress}. {t.compress.label} <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {COMPRESS_OPTIONS.map(option => (
            <label key={option} className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="compress"
                value={option}
                checked={data.compress_type === option}
                onChange={(e) => onChange({ compress_type: e.target.value as typeof data.compress_type })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-sm sm:text-base text-gray-700">{getOptionLabel(option)}</span>
            </label>
          ))}
        </div>
      </div>

      {/* IMF (Conditional) */}
      {(data.imf_wire || data.imf_elastic) && (
        <div className="animate-in fade-in slide-in-from-top-2">
          <label className="block text-sm sm:text-base text-gray-700 font-medium mb-2">
            {questionNumbers.imfWire}. {t.imfWire.label} <span className="text-red-500">*</span>
          </label>
          <div className="space-y-2">
            {IMF_WIRE_OPTIONS.map(option => (
              <label key={option} className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  name="imf_wire"
                  value={option}
                  checked={data.imf_wire_status === option}
                  onChange={(e) => onChange({ imf_wire_status: e.target.value as typeof data.imf_wire_status })}
                  className="w-4 h-4 text-blue-600"
                />
                <span className="ml-2 text-sm sm:text-base text-gray-700">{getOptionLabel(option)}</span>
              </label>
            ))}
          </div>
          {data.imf_wire_status && (
            <div className="mt-3 ml-6">
              <label className="block text-gray-600 text-sm mb-1">
                {t.imfWire.desc}
              </label>
              <textarea
                value={data.imf_wire_description || ''}
                onChange={(e) => onChange({ imf_wire_description: e.target.value })}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
                rows={1}
              />
            </div>
          )}
        </div>
      )}

      {/* Walking (Conditional) - ICBG */}
      {data.special_icbg && (
        <div className="animate-in fade-in slide-in-from-top-2">
          <label className="block text-sm sm:text-base text-gray-700 font-medium mb-2">
            {questionNumbers.walking}. {t.walking.label} <span className="text-red-500">*</span>
          </label>
          <div className="space-y-2">
            {WALKING_OPTIONS.map(option => (
              <label key={option} className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  name="walking"
                  value={option}
                  checked={data.walking_status === option}
                  onChange={(e) => onChange({ walking_status: e.target.value as typeof data.walking_status })}
                  className="w-4 h-4 text-blue-600"
                />
                <span className="ml-2 text-sm sm:text-base text-gray-700">{getOptionLabel(option)}</span>
              </label>
            ))}
          </div>
          {data.walking_status && (
            <div className="mt-3 ml-6">
              <label className="block text-gray-600 text-sm mb-1">
                {t.walking.desc}
              </label>
              <textarea
                value={data.walking_description || ''}
                onChange={(e) => onChange({ walking_description: e.target.value })}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
                rows={1}
              />
            </div>
          )}
        </div>
      )}

    </div>
  );
}
