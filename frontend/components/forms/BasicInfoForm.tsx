import React from 'react';
import type { PatientFormData } from '@/lib/types';
import { GENDER_OPTIONS, PROCEDURE_OPTIONS } from '@/lib/types';

interface BasicInfoFormProps {
  data: PatientFormData;
  onChange: (data: Partial<PatientFormData>) => void;
  onValidationChange?: (isValid: boolean) => void;
}

export function validateBasicInfo(data: PatientFormData): boolean {
  return !!(
    data.age &&
    data.gender &&
    data.hn &&
    data.procedures && data.procedures.length > 0 &&
    data.surgery_date
  );
}

export default function BasicInfoForm({ data, onChange, onValidationChange }: BasicInfoFormProps) {
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
        <div className="space-y-2 border border-gray-200 rounded-lg p-4">
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
          <div className="flex items-start">
            <label className="flex items-start cursor-pointer">
              <input
                type="checkbox"
                checked={data.procedures?.some(p => !PROCEDURE_OPTIONS.includes(p as typeof PROCEDURE_OPTIONS[number])) || false}
                onChange={(e) => {
                  const standardProcedures = data.procedures?.filter(p => PROCEDURE_OPTIONS.includes(p as typeof PROCEDURE_OPTIONS[number])) || [];
                  if (e.target.checked) {
                    onChange({ procedures: [...standardProcedures, ''] });
                  } else {
                    onChange({ procedures: standardProcedures });
                  }
                }}
                className="w-4 h-4 text-blue-600 mt-1"
              />
              <span className="ml-2 text-gray-700">อื่นๆ:</span>
            </label>
            <input
              type="text"
              value={data.procedures?.find(p => !PROCEDURE_OPTIONS.includes(p as typeof PROCEDURE_OPTIONS[number])) || ''}
              onChange={(e) => {
                const standardProcedures = data.procedures?.filter(p => PROCEDURE_OPTIONS.includes(p as typeof PROCEDURE_OPTIONS[number])) || [];
                onChange({
                  procedures: e.target.value ? [...standardProcedures, e.target.value] : standardProcedures
                });
              }}
              onFocus={() => {
                if (!data.procedures?.some(p => !PROCEDURE_OPTIONS.includes(p as typeof PROCEDURE_OPTIONS[number]))) {
                  const standardProcedures = data.procedures?.filter(p => PROCEDURE_OPTIONS.includes(p as typeof PROCEDURE_OPTIONS[number])) || [];
                  onChange({ procedures: [...standardProcedures, ''] });
                }
              }}
              className="ml-2 px-3 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent flex-1"
              placeholder="ระบุหัตถการอื่นๆ"
            />
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
    </div>
  );
}
