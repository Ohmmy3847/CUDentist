import React from 'react';
import type { PatientFormData } from '@/lib/types';
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
  IMF_OPTIONS,
  IMF_WIRE_OPTIONS,
  WALKING_OPTIONS,
} from '@/lib/types';

interface SymptomsFormProps {
  data: PatientFormData;
  onChange: (data: Partial<PatientFormData>) => void;
  onValidationChange?: (isValid: boolean) => void;
}

export function validateSymptoms(data: PatientFormData): boolean {
  const hasIMF = data.has_imf === 'มีการมัดฟัน';
  const hasPain = (data.pain_score || 0) > 0;
  const forgotAntibiotic = data.antibiotic_compliance === 'ลืมทานบางครั้ง';
  
  const isValid = !!(
    data.pain_score !== undefined &&
    (!hasPain || data.pain_medication_effective) &&
    data.swelling_status &&
    data.breathing_or_swallowing_difficulty &&
    data.bleeding_status &&
    data.fever_status &&
    data.numbness_status &&
    data.phlebitis &&
    data.suture_status &&
    data.antibiotic_compliance &&
    (!forgotAntibiotic || data.antibiotic_description) &&
    data.compress_type &&
    data.has_imf &&
    (!hasIMF || data.imf_wire_status) &&
    data.walking_status
  );
  
  console.log('SymptomsForm Validation:', {
    isValid,
    pain_score: data.pain_score,
    hasPain,
    pain_medication_effective: data.pain_medication_effective,
    swelling_status: data.swelling_status,
    breathing_or_swallowing_difficulty: data.breathing_or_swallowing_difficulty,
    bleeding_status: data.bleeding_status,
    fever_status: data.fever_status,
    numbness_status: data.numbness_status,
    phlebitis: data.phlebitis,
    suture_status: data.suture_status,
    antibiotic_compliance: data.antibiotic_compliance,
    forgotAntibiotic,
    antibiotic_description: data.antibiotic_description,
    compress_type: data.compress_type,
    has_imf: data.has_imf,
    hasIMF,
    imf_wire_status: data.imf_wire_status,
    walking_status: data.walking_status
  });
  
  return isValid;
}

export default function SymptomsForm({ data, onChange, onValidationChange }: SymptomsFormProps) {
  // Clear conditional fields when parent field changes
  React.useEffect(() => {
    const hasPain = (data.pain_score || 0) > 0;
    const hasIMF = data.has_imf === 'มีการมัดฟัน';
    const forgotAntibiotic = data.antibiotic_compliance === 'ลืมทานบางครั้ง';
    
    const updates: Partial<PatientFormData> = {};
    
    // ถ้า pain_score = 0 ให้ล้าง pain_medication_effective
    if (!hasPain && data.pain_medication_effective) {
      updates.pain_medication_effective = undefined;
    }
    
    // ถ้าไม่มีการมัดฟัน ให้ล้าง imf_wire_status และ description
    if (!hasIMF && (data.imf_wire_status || data.imf_wire_description)) {
      updates.imf_wire_status = undefined;
      updates.imf_wire_description = undefined;
    }
    
    // ถ้าไม่ได้ลืมทานยา ให้ล้าง antibiotic_description
    if (!forgotAntibiotic && data.antibiotic_description) {
      updates.antibiotic_description = undefined;
    }
    
    // ล้าง description fields เมื่อ main field เป็น undefined
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
    data.has_imf,
    data.antibiotic_compliance,
    data.swelling_status,
    data.breathing_or_swallowing_difficulty,
    data.bleeding_status,
    data.fever_status,
    data.numbness_status,
    data.phlebitis,
    data.suture_status,
    data.walking_status
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

  let qNum = 5; // เริ่มจาก 6 (5+1)

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">
        ส่วนที่ 2: อาการ
      </h2>

      {/* 6. ระดับความปวด */}
      <div>
        <label className="block text-gray-700 font-medium mb-3">
          {++qNum}. ระดับความปวด ณ ปัจจุบัน (Pain score) <span className="text-red-500">*</span>
        </label>
        <div className="space-y-3">
          <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
            <span>ไม่ปวดเลย</span>
            <span>ปวดมากที่สุดในชีวิต</span>
          </div>
          <div className="grid grid-cols-11 gap-2">
            {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(score => (
              <button
                key={score}
                type="button"
                onClick={() => onChange({ pain_score: score })}
                className={`
                  py-3 px-2 rounded-lg font-semibold transition-all
                  ${data.pain_score === score
                    ? 'bg-blue-600 text-white shadow-lg scale-110'
                    : 'bg-gray-100 text-gray-700 hover:bg-blue-100 hover:text-blue-600'
                  }
                `}
              >
                {score}
              </button>
            ))}
          </div>
          <div className="text-center mt-3">
            {data.pain_score !== undefined ? (
              <>
                <span className="text-3xl font-bold text-blue-600">{data.pain_score}</span>
                <span className="text-gray-600"> / 10</span>
              </>
            ) : (
              <span className="text-gray-400">กรุณาเลือกระดับความปวด</span>
            )}
          </div>
        </div>
      </div>

      {/* 7. ยาแก้ปวดมีผลหรือไม่ - แสดงเฉพาะเมื่อ pain_score > 0 */}
      {(data.pain_score || 0) > 0 && (
        <div>
          <label className="block text-gray-700 font-medium mb-2">
            {++qNum}. ทานยาแก้ปวดแล้วดีขึ้นหรือไม่? <span className="text-red-500">*</span>
          </label>
          <div className="space-y-2">
            {PAIN_MEDICATION_OPTIONS.map(option => (
              <label key={option} className="flex items-center">
                <input
                  type="radio"
                  name="pain_medication"
                  value={option}
                  checked={data.pain_medication_effective === option}
                  onChange={(e) => onChange({ pain_medication_effective: e.target.value as typeof data.pain_medication_effective })}
                  className="w-4 h-4 text-blue-600"
                />
                <span className="ml-2 text-gray-700">{option}</span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* 8. อาการบวม */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. อาการบวม <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {SWELLING_OPTIONS.map(option => (
            <label key={option} className="flex items-center">
              <input
                type="radio"
                name="swelling"
                value={option}
                checked={data.swelling_status === option}
                onChange={(e) => onChange({ swelling_status: e.target.value as typeof data.swelling_status })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-gray-700">{option}</span>
            </label>
          ))}
        </div>
        {data.swelling_status && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              คำอธิบายเพิ่มเติมสำหรับอาการ (ไม่บังคับ)
            </label>
            <textarea
              value={data.swelling_description || ''}
              onChange={(e) => onChange({ swelling_description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="เช่น บวมบริเวณใด, บวมมากน้อยแค่ไหน"
              rows={3}
            />
          </div>
        )}
      </div>

      {/* 9. หายใจ/กลืนลำบาก */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. มีอาการหายใจลำบาก หรือ กลืนลำบากหรือไม่? <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          <label className="flex items-center">
            <input
              type="radio"
              name="breathing"
              value="ไม่มี"
              checked={data.breathing_or_swallowing_difficulty === 'ไม่มี'}
              onChange={(e) => onChange({ breathing_or_swallowing_difficulty: e.target.value })}
              className="w-4 h-4 text-blue-600"
            />
            <span className="ml-2 text-gray-700">ไม่มี</span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="breathing"
              value="มี"
              checked={data.breathing_or_swallowing_difficulty === 'มี'}
              onChange={(e) => onChange({ breathing_or_swallowing_difficulty: e.target.value })}
              className="w-4 h-4 text-blue-600"
            />
            <span className="ml-2 text-gray-700">มี</span>
          </label>
        </div>
        {data.breathing_or_swallowing_difficulty && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              คำอธิบายเพิ่มเติมสำหรับอาการ (ไม่บังคับ)
            </label>
            <textarea
              value={data.breathing_description || ''}
              onChange={(e) => onChange({ breathing_description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="เช่น หายใจลำบากเมื่อนอน, กลืนลำบากเฉพาะของแข็ง"
              rows={3}
            />
          </div>
        )}
      </div>

      {/* 10. เลือดออก */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. อาการเลือดซึม หรือ เลือดออก จากแผลในช่องปาก หรือ บริเวณจมูก <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {BLEEDING_OPTIONS.map(option => (
            <label key={option} className="flex items-center">
              <input
                type="radio"
                name="bleeding"
                value={option}
                checked={data.bleeding_status === option}
                onChange={(e) => onChange({ bleeding_status: e.target.value as typeof data.bleeding_status })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-gray-700">{option}</span>
            </label>
          ))}
        </div>
        {data.bleeding_status && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              คำอธิบายเพิ่มเติมสำหรับอาการ (ไม่บังคับ)
            </label>
            <textarea
              value={data.bleeding_description || ''}
              onChange={(e) => onChange({ bleeding_description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="เช่น เลือดซึมบริเวณใด, เป็นเลือดสดหรือเลือดคั่ง"
              rows={3}
            />
          </div>
        )}
      </div>

      {/* 11. ไข้ */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. อาการไข้  <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          <label className="flex items-center">
            <input
              type="radio"
              name="fever"
              value="ไม่มีไข้"
              checked={data.fever_status === 'ไม่มีไข้'}
              onChange={(e) => onChange({ fever_status: e.target.value })}
              className="w-4 h-4 text-blue-600"
            />
            <span className="ml-2 text-gray-700">ไม่มีไข้</span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="fever"
              value="มีไข้ (มากกว่า 38 องศาเซลเซียส)"
              checked={data.fever_status === 'มีไข้ (มากกว่า 38 องศาเซลเซียส)'}
              onChange={(e) => onChange({ fever_status: e.target.value })}
              className="w-4 h-4 text-blue-600"
            />
            <span className="ml-2 text-gray-700">มีไข้ (มากกว่า 38 องศาเซลเซียส)</span>
          </label>
        </div>
        {data.fever_status && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              คำอธิบายเพิ่มเติมสำหรับอาการ (ไม่บังคับ)
            </label>
            <textarea
              value={data.fever_description || ''}
              onChange={(e) => onChange({ fever_description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="เช่น อุณหภูมิเท่าไร, มีไข้เป็นช่วงๆ"
              rows={3}
            />
          </div>
        )}
      </div>

      {/* 12. อาการชา */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. อาการชา (บันทึกบริเวณที่ชาที่ช่องอื่นๆ) <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {NUMBNESS_OPTIONS.map(option => (
            <label key={option} className="flex items-center">
              <input
                type="radio"
                name="numbness"
                value={option}
                checked={data.numbness_status === option}
                onChange={(e) => onChange({ numbness_status: e.target.value as typeof data.numbness_status })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-gray-700">{option}</span>
            </label>
          ))}
        </div>
        {data.numbness_status && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              คำอธิบายเพิ่มเติมสำหรับอาการ (ไม่บังคับ)
            </label>
            <textarea
              value={data.numbness_description || ''}
              onChange={(e) => onChange({ numbness_description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="ระบุบริเวณที่ชา เช่น ชาบริเวณริมฝีปากล่าง, ชาบริเวณหลังคอ"
              rows={3}
            />
          </div>
        )}
      </div>

      {/* 13. Phlebitis */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. บริเวณที่เอาเข็มน้ำเกลือออกที่หลังมือหรือข้อมือ <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {PHLEBITIS_OPTIONS.map(option => (
            <label key={option} className="flex items-center">
              <input
                type="radio"
                name="phlebitis"
                value={option}
                checked={data.phlebitis === option}
                onChange={(e) => onChange({ phlebitis: e.target.value as typeof data.phlebitis })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-gray-700">{option}</span>
            </label>
          ))}
        </div>
        {data.phlebitis && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              คำอธิบายเพิ่มเติมสำหรับอาการ (ไม่บังคับ)
            </label>
            <textarea
              value={data.phlebitis_description || ''}
              onChange={(e) => onChange({ phlebitis_description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="เช่น บริเวณหลังมือมีอาการเจ็บเล็กน้อย"
              rows={3}
            />
          </div>
        )}
      </div>

      {/* 14. ไหมเย็บแผล */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. ไหมเย็บแผล <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {SUTURE_OPTIONS.map(option => (
            <label key={option} className="flex items-center">
              <input
                type="radio"
                name="suture"
                value={option}
                checked={data.suture_status === option}
                onChange={(e) => onChange({ suture_status: e.target.value as typeof data.suture_status })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-gray-700">{option}</span>
            </label>
          ))}
        </div>
        {data.suture_status && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              คำอธิบายเพิ่มเติมสำหรับอาการ (ไม่บังคับ)
            </label>
            <textarea
              value={data.suture_description || ''}
              onChange={(e) => onChange({ suture_description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="เช่น ไหมเย็บหลุดบริเวณใด, หลุดกี่เส้น"
              rows={3}
            />
          </div>
        )}
      </div>

      {/* 15. อาการอื่นๆ (multiple) */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. อาการอื่นๆ (เลือกได้หลายคำตอบ)
        </label>
        <div className="space-y-2 border border-gray-200 rounded-lg p-4">
          {OTHER_SYMPTOMS_OPTIONS.map(symptom => (
            <label key={symptom} className="flex items-start">
              <input
                type="checkbox"
                checked={data.other_symptoms?.includes(symptom) || false}
                onChange={(e) => handleOtherSymptomsChange(symptom, e.target.checked)}
                className="w-4 h-4 text-blue-600 mt-1"
              />
              <span className="ml-2 text-gray-700">{symptom}</span>
            </label>
          ))}
          <div className="flex items-start">
            <label className="flex items-start cursor-pointer">
              <input
                type="checkbox"
                checked={data.other_symptoms?.some(s => !OTHER_SYMPTOMS_OPTIONS.includes(s as typeof OTHER_SYMPTOMS_OPTIONS[number])) || false}
                onChange={(e) => {
                  const standardSymptoms = data.other_symptoms?.filter(s => OTHER_SYMPTOMS_OPTIONS.includes(s as typeof OTHER_SYMPTOMS_OPTIONS[number])) || [];
                  if (e.target.checked) {
                    onChange({ other_symptoms: [...standardSymptoms, ''] });
                  } else {
                    onChange({ other_symptoms: standardSymptoms });
                  }
                }}
                className="w-4 h-4 text-blue-600 mt-1"
              />
              <span className="ml-2 text-gray-700">อื่นๆ:</span>
            </label>
            <input
              type="text"
              value={data.other_symptoms?.find(s => !OTHER_SYMPTOMS_OPTIONS.includes(s as typeof OTHER_SYMPTOMS_OPTIONS[number])) || ''}
              onChange={(e) => {
                const standardSymptoms = data.other_symptoms?.filter(s => OTHER_SYMPTOMS_OPTIONS.includes(s as typeof OTHER_SYMPTOMS_OPTIONS[number])) || [];
                onChange({
                  other_symptoms: e.target.value ? [...standardSymptoms, e.target.value] : standardSymptoms
                });
              }}
              onFocus={() => {
                if (!data.other_symptoms?.some(s => !OTHER_SYMPTOMS_OPTIONS.includes(s as typeof OTHER_SYMPTOMS_OPTIONS[number]))) {
                  const standardSymptoms = data.other_symptoms?.filter(s => OTHER_SYMPTOMS_OPTIONS.includes(s as typeof OTHER_SYMPTOMS_OPTIONS[number])) || [];
                  onChange({ other_symptoms: [...standardSymptoms, ''] });
                }
              }}
              className="ml-2 px-3 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent flex-1"
              placeholder="ระบุอาการอื่นๆ"
            />
          </div>
        </div>
      </div>

      {/* 16. ยาฆ่าเชื้อ */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. รับประทานยาฆ่าเชื้อครบตามแผนการรักษาหรือไม่? <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {ANTIBIOTIC_OPTIONS.map(option => (
            <label key={option} className="flex items-center">
              <input
                type="radio"
                name="antibiotic"
                value={option}
                checked={data.antibiotic_compliance === option}
                onChange={(e) => onChange({ antibiotic_compliance: e.target.value as typeof data.antibiotic_compliance })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-gray-700">{option}</span>
            </label>
          ))}
        </div>
        
        {/* แสดงช่องกรอกจำนวนครั้งเฉพาะเมื่อเลือก "ลืมทานบางครั้ง" */}
        {data.antibiotic_compliance === 'ลืมทานบางครั้ง' && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              จำนวนครั้งที่ลืมทาน <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              min="0"
              required
              value={data.antibiotic_description || ''}
              onChange={(e) => onChange({ antibiotic_description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="กรอกจำนวนครั้ง เช่น 2"
            />
          </div>
        )}
      </div>

      {/* 17. ประคบ */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. ประคบเย็น หรือ อุ่นอยู่หรือไม่? <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {COMPRESS_OPTIONS.map(option => (
            <label key={option} className="flex items-center">
              <input
                type="radio"
                name="compress"
                value={option}
                checked={data.compress_type === option}
                onChange={(e) => onChange({ compress_type: e.target.value as typeof data.compress_type })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-gray-700">{option}</span>
            </label>
          ))}
        </div>
      </div>

      {/* 18. มัดฟัน */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. มีการมัดฟันบนและล่างเข้าด้วยกัน โดยที่ไม่สามารถอ้าปากได้หรือไม่? (IMF) <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {IMF_OPTIONS.map(option => (
            <label key={option} className="flex items-center">
              <input
                type="radio"
                name="imf"
                value={option}
                checked={data.has_imf === option}
                onChange={(e) => onChange({ has_imf: e.target.value as typeof data.has_imf })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-gray-700">{option}</span>
            </label>
          ))}
        </div>
      </div>

      {/* 19. ลวดมัดฟัน (แสดงถ้ามีการมัดฟัน) */}
      {data.has_imf === 'มีการมัดฟัน' && (
        <div>
          <label className="block text-gray-700 font-medium mb-2">
            {++qNum}. หากมีการมัดฟันบนและล่างเข้าด้วยกัน ลวด/ยางมัดฟันแน่นดีหรือไม่? <span className="text-red-500">*</span>
          </label>
          <div className="space-y-2">
            {IMF_WIRE_OPTIONS.map(option => (
              <label key={option} className="flex items-center">
                <input
                  type="radio"
                  name="imf_wire"
                  value={option}
                  checked={data.imf_wire_status === option}
                  onChange={(e) => onChange({ imf_wire_status: e.target.value as typeof data.imf_wire_status })}
                  className="w-4 h-4 text-blue-600"
                />
                <span className="ml-2 text-gray-700">{option}</span>
              </label>
            ))}
          </div>
        {data.imf_wire_status && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              คำอธิบายเพิ่มเติมสำหรับอาการ (ไม่บังคับ)
            </label>
            <textarea
              value={data.imf_wire_description || ''}
              onChange={(e) => onChange({ imf_wire_description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="เช่น ลวดหลวมบ้างหรือไม่, ยางขาดหรือไม่"
              rows={3}
            />
          </div>
        )}      </div>
      )}
      {/* 20. การเดิน */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. การเดิน ในผู้ป่วยที่ได้รับการรักษาการแหว่งของสันเหงือกโดยการนำกระดูกสะโพกมาปลูก <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {WALKING_OPTIONS.map(option => (
            <label key={option} className="flex items-center">
              <input
                type="radio"
                name="walking"
                value={option}
                checked={data.walking_status === option}
                onChange={(e) => onChange({ walking_status: e.target.value as typeof data.walking_status })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-gray-700">{option}</span>
            </label>
          ))}
        </div>
        {data.walking_status && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              คำอธิบายเพิ่มเติมสำหรับอาการ (ไม่บังคับ)
            </label>
            <textarea
              value={data.walking_description || ''}
              onChange={(e) => onChange({ walking_description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="เช่น เดินลำบาก, มีอาการปวดบริเวณสะโพก"
              rows={3}
            />
          </div>
        )}
      </div>
    </div>
  );
}
