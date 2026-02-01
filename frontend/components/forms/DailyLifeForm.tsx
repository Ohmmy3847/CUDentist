import React from 'react';
import type { PatientFormData } from '@/lib';
import {
  FOOD_AMOUNT_OPTIONS,
  NG_TUBE_OPTIONS,
} from '@/lib';

interface DailyLifeFormProps {
  data: PatientFormData;
  onChange: (data: Partial<PatientFormData>) => void;
  onValidationChange?: (isValid: boolean) => void;
  startingQuestionNumber?: number;
}

export function validateDailyLife(data: PatientFormData): boolean {
  console.log('validateDailyLife', data);
  return true;
  // return !!(
  //   data.brushing_teeth &&
  //   data.mouth_rinsing &&
  //   data.feeding_method &&
  //   data.food_types && data.food_types.length > 0 &&
  //   data.food_amount &&
  //   data.ng_tube_position
  // );
}

export default function DailyLifeForm({ data, onChange, onValidationChange, startingQuestionNumber = 20 }: DailyLifeFormProps) {
  // Clear conditional description fields when parent field changes
  React.useEffect(() => {
    const updates: Partial<PatientFormData> = {};

    // ล้าง description fields เมื่อ main field เป็น undefined
    if (!data.brushing_teeth && data.brushing_description) {
      updates.brushing_description = undefined;
    }
    if (!data.mouth_rinsing && data.rinsing_description) {
      updates.rinsing_description = undefined;
    }

    if (!data.food_amount && data.food_amount_description) {
      updates.food_amount_description = undefined;
    }
    if (!data.ng_tube_position && data.ng_tube_description) {
      updates.ng_tube_description = undefined;
    }

    if (Object.keys(updates).length > 0) {
      onChange(updates);
    }
  }, [
    data.brushing_teeth,
    data.mouth_rinsing,
    data.food_amount,
    data.ng_tube_position,
    data.brushing_description,
    data.rinsing_description,
    data.food_amount_description,
    data.ng_tube_description,
    onChange
  ]);

  React.useEffect(() => {
    if (onValidationChange) {
      onValidationChange(validateDailyLife(data));
    }
  }, [data, onValidationChange]);

  const handleFoodTypesChange = (type: string, checked: boolean) => {
    const current = data.food_types || [];
    const updated = checked
      ? [...current, type]
      : current.filter(t => t !== type);
    onChange({ food_types: updated });
  };

  const FOOD_TYPE_OPTIONS = [
    'อาหารเหลวใสไม่มีกาก เช่น น้ำซุปใส น้ำผลไม้กรอง นม',
    'อาหารปั่นเหลวมีกาก เช่น โจ๊กปั่นเหลว ไก่ปั่น',
    'อาหารอ่อน เช่น โจ๊ก ข้าวต้ม ไข่ลวก ผักนึ่ง',
    'อาหารปกติแต่เว้นอาหารรสจัด เผ็ด ร้อน แข็ง เหนียว',
  ];

  // คำนวณเลขข้อคำถามแบบ dynamic ตามคำถามที่แสดงจริง
  const questionNumbers = React.useMemo(() => {
    let num = startingQuestionNumber;
    const numbers: Record<string, number> = {};

    numbers.brushing = ++num; // Brushing teeth (always)
    numbers.rinsing = ++num; // Mouth rinsing (always)
    numbers.foodTypes = ++num; // Food types (always)
    numbers.foodAmount = ++num; // Food amount (always)
    numbers.questions = ++num; // Additional questions (always)
    if (data.special_ng_tube === 'มี') numbers.ngTube = ++num; // NG tube (conditional)

    return numbers;
  }, [startingQuestionNumber, data.special_ng_tube]);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">
        ส่วนที่ 3: การใช้ชีวิตประจำวัน
      </h2>

      {/* การแปรงฟัน */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {questionNumbers.brushing}. การแปรงฟัน <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          <label className="flex items-center">
            <input
              type="radio"
              name="brushing"
              value="แปรงฟันได้"
              checked={data.brushing_teeth === 'แปรงฟันได้'}
              onChange={(e) => onChange({ brushing_teeth: e.target.value })}
              className="w-4 h-4 text-blue-600"
            />
            <span className="ml-2 text-gray-700">แปรงฟันได้</span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="brushing"
              value="แปรงฟันไม่ถนัด"
              checked={data.brushing_teeth === 'แปรงฟันไม่ถนัด'}
              onChange={(e) => onChange({ brushing_teeth: e.target.value })}
              className="w-4 h-4 text-blue-600"
            />
            <span className="ml-2 text-gray-700">แปรงฟันไม่ถนัด</span>
          </label>
        </div>
        {data.brushing_teeth && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              คำอธิบายเพิ่มเติม (ไม่บังคับ)
            </label>
            <textarea
              value={data.brushing_description || ''}
              onChange={(e) => onChange({ brushing_description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="เช่น แปรงบ้างส่วน, ปวดเมื่อแปรง"
              rows={1}
            />
          </div>
        )}
      </div>

      {/* 22. การบ้วนปาก */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {questionNumbers.rinsing}. การบ้วนปากด้วยน้ำยาบ้วนปาก <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          <label className="flex items-center">
            <input
              type="radio"
              name="rinsing"
              value="บ้วนปากได้"
              checked={data.mouth_rinsing === 'บ้วนปากได้'}
              onChange={(e) => onChange({ mouth_rinsing: e.target.value })}
              className="w-4 h-4 text-blue-600"
            />
            <span className="ml-2 text-gray-700">บ้วนปากได้</span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="rinsing"
              value="บ้วนปากไม่ได้"
              checked={data.mouth_rinsing === 'บ้วนปากไม่ได้'}
              onChange={(e) => onChange({ mouth_rinsing: e.target.value })}
              className="w-4 h-4 text-blue-600"
            />
            <span className="ml-2 text-gray-700">บ้วนปากไม่ได้</span>
          </label>
        </div>
        {data.mouth_rinsing && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              คำอธิบายเพิ่มเติม (ไม่บังคับ)
            </label>
            <textarea
              value={data.rinsing_description || ''}
              onChange={(e) => onChange({ rinsing_description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder=""
              rows={1}
            />
          </div>
        )}
      </div>



      {/* 24. ประเภทอาหาร */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {questionNumbers.foodTypes}. ประเภทอาหารที่ทาน (สามารถเลือกได้หลายคำตอบ) <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2 border border-gray-200 rounded-lg p-4">
          {FOOD_TYPE_OPTIONS.map((option) => (
            <label key={option} className="flex items-start">
              <input
                type="checkbox"
                checked={data.food_types?.includes(option) || false}
                onChange={(e) => handleFoodTypesChange(option, e.target.checked)}
                className="w-4 h-4 text-blue-600 mt-1"
              />
              <span className="ml-2 text-gray-700">{option}</span>
            </label>
          ))}
          <div className="flex items-start">
            <label className="flex items-start cursor-pointer">
              <input
                type="checkbox"
                checked={data.food_types?.some(t => !FOOD_TYPE_OPTIONS.includes(t)) || false}
                onChange={(e) => {
                  const standardTypes = data.food_types?.filter(t => FOOD_TYPE_OPTIONS.includes(t)) || [];
                  if (e.target.checked) {
                    onChange({ food_types: [...standardTypes, ''] });
                  } else {
                    onChange({ food_types: standardTypes });
                  }
                }}
                className="w-4 h-4 text-blue-600 mt-1"
              />
              <span className="ml-2 text-gray-700">อื่นๆ:</span>
            </label>
            <input
              type="text"
              value={data.food_types?.find(t => !FOOD_TYPE_OPTIONS.includes(t)) || ''}
              onChange={(e) => {
                const standardTypes = data.food_types?.filter(t => FOOD_TYPE_OPTIONS.includes(t)) || [];
                onChange({
                  food_types: e.target.value ? [...standardTypes, e.target.value] : standardTypes
                });
              }}
              onFocus={() => {
                if (!data.food_types?.some(t => !FOOD_TYPE_OPTIONS.includes(t))) {
                  const standardTypes = data.food_types?.filter(t => FOOD_TYPE_OPTIONS.includes(t)) || [];
                  onChange({ food_types: [...standardTypes, ''] });
                }
              }}
              className="ml-2 px-3 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent flex-1"
              placeholder=""
            />
          </div>
        </div>
      </div>

      {/* 25. ปริมาณอาหาร */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {questionNumbers.foodAmount}. ปริมาณอาหารที่ทาน <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {FOOD_AMOUNT_OPTIONS.map(option => (
            <label key={option} className="flex items-center">
              <input
                type="radio"
                name="food_amount"
                value={option}
                checked={data.food_amount === option}
                onChange={(e) => onChange({ food_amount: e.target.value as typeof data.food_amount })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-gray-700">{option}</span>
            </label>
          ))}
        </div>
        {data.food_amount && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              คำอธิบายเพิ่มเติม (ไม่บังคับ)
            </label>
            <textarea
              value={data.food_amount_description || ''}
              onChange={(e) => onChange({ food_amount_description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder=""
              rows={1}
            />
          </div>
        )}
      </div>

      {/* 26. คำถามเพิ่มเติม */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {questionNumbers.questions}. ผู้ป่วยมีคำถามที่จะสอบถามพยาบาลเพิ่มเติมหรือไม่?
        </label>
        <textarea
          value={data.additional_questions || ''}
          onChange={(e) => onChange({ additional_questions: e.target.value })}
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="กรอกคำถามหรือข้อสงสัยที่ต้องการสอบถาม"
        />
      </div>

      {/* 27. สายยางให้อาหาร (NG tube) - แสดงเฉพาะเมื่อเลือก NG tube */}
      {data.special_ng_tube === 'มี' && (
        <div>
          <label className="block text-gray-700 font-medium mb-2">
            {questionNumbers.ngTube}. ตำแหน่งสายยางให้อาหาร <span className="text-red-500">*</span>
          </label>
          <div className="space-y-2">
            {NG_TUBE_OPTIONS.map(option => (
              <label key={option} className="flex items-center">
                <input
                  type="radio"
                  name="ng_tube"
                  value={option}
                  checked={data.ng_tube_position === option}
                  onChange={(e) => onChange({ ng_tube_position: e.target.value as typeof data.ng_tube_position })}
                  className="w-4 h-4 text-blue-600"
                />
                <span className="ml-2 text-gray-700">{option}</span>
              </label>
            ))}
          </div>
          {data.ng_tube_position && (
            <div className="mt-3 ml-6">
              <label className="block text-gray-600 text-sm mb-1">
                คำอธิบายเพิ่มเติม (ไม่บังคับ)
              </label>
              <textarea
                value={data.ng_tube_description || ''}
                onChange={(e) => onChange({ ng_tube_description: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder=""
                rows={1}
              />
            </div>
          )}
        </div>
      )}

      {/* สรุปข้อมูลที่กรอก */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-8">
        <h3 className="font-bold text-blue-900 mb-2 flex items-center">
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          พร้อมส่งข้อมูลแล้ว
        </h3>
        <p className="text-blue-800 text-sm">
          กรุณาตรวจสอบข้อมูลก่อนกดปุ่ม &quot;ส่งและประเมินความเสี่ยง&quot; ระบบจะทำการวิเคราะห์และให้คำแนะนำตามระดับความเสี่ยงที่ประเมินได้
        </p>
      </div>
    </div>
  );
}
