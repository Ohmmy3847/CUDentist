import React from 'react';
import { Plus, X } from 'lucide-react';
import type { PatientFormData } from '@/lib';
import { GENDER_OPTIONS, PROCEDURE_OPTIONS } from '@/lib';

interface BasicInfoFormProps {
  data: PatientFormData;
  onChange: (data: Partial<PatientFormData>) => void;
  onValidationChange?: (isValid: boolean) => void;
}

export function validateBasicInfo(data: PatientFormData): boolean {
  return true;
  // return !!(
  //   data.age &&
  //   data.gender &&
  //   data.hn &&
  //   data.procedures && data.procedures.length > 0 &&
  //   data.surgery_date
  // );
}

export default function BasicInfoForm({ data, onChange, onValidationChange }: BasicInfoFormProps) {
  const [customProcedures, setCustomProcedures] = React.useState<string[]>([]);
  
  // Sync customProcedures from data.procedures when component mounts or data changes
  React.useEffect(() => {
    const currentProcedures = data.procedures || [];
    const customProcs = currentProcedures.filter(p => 
      !PROCEDURE_OPTIONS.includes(p as typeof PROCEDURE_OPTIONS[number])
    );
    if (customProcs.length > 0 && customProcedures.length === 0) {
      setCustomProcedures(customProcs);
    }
  }, [data.procedures]);
  
  React.useEffect(() => {
    const isValid = validateBasicInfo(data);
    console.log('BasicInfoForm validation:', { data, isValid });
    if (onValidationChange) {
      onValidationChange(isValid);
    }
  }, [data, onValidationChange]);

  const handleProcedureChange = (procedure: string, checked: boolean) => {
    const current = data.procedures || [];
    const updated = checked
      ? [...current, procedure]
      : current.filter(p => p !== procedure);
    onChange({ procedures: updated });
  };
  
  const handleAddProcedureField = () => {
    // ตรวจสอบว่าช่องสุดท้ายมีค่าหรือยัง
    if (customProcedures.length === 0 || customProcedures[customProcedures.length - 1].trim() !== '') {
      setCustomProcedures([...customProcedures, '']);
    }
  };
  
  const handleRemoveProcedureField = (index: number) => {
    const updated = customProcedures.filter((_, i) => i !== index);
    setCustomProcedures(updated);
    
    // Remove from procedures array
    const currentProcedures = data.procedures || [];
    const standardProcedures = currentProcedures.filter(p => 
      PROCEDURE_OPTIONS.includes(p as typeof PROCEDURE_OPTIONS[number])
    );
    const customProcs = currentProcedures.filter(p => 
      !PROCEDURE_OPTIONS.includes(p as typeof PROCEDURE_OPTIONS[number])
    );
    customProcs.splice(index, 0);
    onChange({ procedures: [...standardProcedures, ...customProcs.filter(p => p)] });
  };
  
  const handleCustomProcedureChange = (index: number, value: string) => {
    const updatedCustom = [...customProcedures];
    updatedCustom[index] = value;
    setCustomProcedures(updatedCustom);
    
    // Update procedures array
    const currentProcedures = data.procedures || [];
    const standardProcedures = currentProcedures.filter(p => 
      PROCEDURE_OPTIONS.includes(p as typeof PROCEDURE_OPTIONS[number])
    );
    const filledCustomProcedures = updatedCustom.filter(p => p.trim());
    onChange({ procedures: [...standardProcedures, ...filledCustomProcedures] });
  };

  let qNum = 0;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">
        ส่วนที่ 1: ข้อมูลพื้นฐาน
      </h2>

      {/* 1. อายุ */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. อายุ <span className="text-red-500">*</span>
        </label>
        <input
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            value={data.age ?? ""}
            onChange={(e) => {
                const value = e.target.value;
                if (/^\d*$/.test(value)) {      // อนุญาตเฉพาะตัวเลข
                onChange({ age: value === "" ? undefined : parseInt(value) });
                }
            }}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="กรอกอายุ"
        />
      </div>

      {/* 2. เพศ */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. เพศ <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {GENDER_OPTIONS.map(option => (
            <label key={option} className="flex items-center">
              <input
                type="radio"
                name="gender"
                value={option}
                checked={data.gender === option}
                onChange={(e) => onChange({ gender: e.target.value })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-gray-700">{option}</span>
            </label>
          ))}
          <div className="flex items-center">
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="gender"
                checked={!!(data.gender && !GENDER_OPTIONS.includes(data.gender as typeof GENDER_OPTIONS[number]))}
                onChange={() => {
                  onChange({ gender: ' ' });
                }}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-gray-700">อื่นๆ:</span>
            </label>
            <input
              type="text"
              value={data.gender && !GENDER_OPTIONS.includes(data.gender as typeof GENDER_OPTIONS[number]) ? data.gender.trim() : ''}
              onChange={(e) => onChange({ gender: e.target.value || ' ' })}
              onFocus={() => {
                if (!data.gender || GENDER_OPTIONS.includes(data.gender as typeof GENDER_OPTIONS[number])) {
                  onChange({ gender: ' ' });
                }
              }}
              className="ml-2 px-3 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="ระบุ"
            />
          </div>
        </div>
      </div>

      {/* 3. HN */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. HN (กรอกเลขคนไข้) <span className="text-red-500">*</span>
        </label>
        <input
          type="number"
          value={data.hn || ''}
          onChange={(e) => onChange({ hn: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="กรอกหมายเลข HN"
        />
      </div>

      {/* 4. หัตถการที่ทำ */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. หัตถการที่ทำ (เลือกได้มากกว่า 1 หัตถการ) <span className="text-red-500">*</span>
        </label>
        <div className="space-y-3 border border-gray-200 rounded-lg p-4">
          {PROCEDURE_OPTIONS.map(procedure => (
            <label key={procedure} className="flex items-start">
              <input
                type="checkbox"
                checked={data.procedures?.includes(procedure) || false}
                onChange={(e) => handleProcedureChange(procedure, e.target.checked)}
                className="w-4 h-4 text-blue-600 mt-1"
              />
              <span className="ml-2 text-gray-700">{procedure}</span>
            </label>
          ))}
          
          {/* หัตถการอื่นๆ - แบบหลายช่อง */}
          <div className="mt-4 pt-4 border-t border-gray-200">
            <label className="block text-gray-700 font-medium mb-3">หัตถการอื่นๆ:</label>
            <div className="space-y-2">
              {customProcedures.map((proc, index) => (
                <div key={index} className="flex items-center gap-2">
                  <input
                    type="text"
                    value={proc}
                    onChange={(e) => handleCustomProcedureChange(index, e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="โปรดระบุหัตถการ"
                  />
                  <button
                    type="button"
                    onClick={() => handleRemoveProcedureField(index)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="ลบช่องนี้"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              ))}
              <button
                type="button"
                onClick={handleAddProcedureField}
                className="flex items-center gap-2 px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-medium"
              >
                <Plus className="w-5 h-5" />
                {customProcedures.length === 0
                  ? 'กดเพื่อเพิ่มหัตถการอื่น ๆ'
                  : 'กดเพื่อเพิ่มหัตถการถัดไป'
                }
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 5. ได้รับการผ่าตัดเมื่อวันที่ */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. ได้รับการผ่าตัดเมื่อวันที่ <span className="text-red-500">*</span>
        </label>
        <input
          type="date"
          value={data.surgery_date || ''}
          onChange={(e) => onChange({ surgery_date: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
      
      {/* Note - หมายเหตุสำหรับหมอ */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <label className="block text-gray-700 font-medium mb-2">
          <span className="text-yellow-700">📋</span> หมายเหตุพิเศษ (สำหรับหมอ)
        </label>
       
        <textarea
          value={data.note || ''}
          onChange={(e) => onChange({ note: e.target.value })}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
          placeholder="เช่น ผู้ป่วยมีอาการแพ้ยา Amoxicillin เกิดผื่นขึ้น, เลือดออกมากหลังผ่าตัด ต้องให้ยาห้ามเลือดเพิ่ม"
          rows={4}
        />
      </div>
    </div>
  );
}
