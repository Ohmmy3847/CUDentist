import React from 'react';
import type { PatientFormData } from '@/lib';
import {
  FOOD_AMOUNT_OPTIONS,
  NG_TUBE_OPTIONS,
  BRUSHING_TEETH_OPTIONS,
  MOUTH_RINSING_OPTIONS,
  FOOD_TYPE_OPTIONS,
} from '@/lib';
import { th, en } from '@/lib/locales';

interface DailyLifeFormProps {
  data: PatientFormData;
  onChange: (data: Partial<PatientFormData>) => void;
  onValidationChange?: (isValid: boolean) => void;
  startingQuestionNumber?: number;
  lang?: 'th' | 'en';
}

export function validateDailyLife(): boolean {
  return true;
}



export default function DailyLifeForm({
  data,
  onChange,
  onValidationChange,
  startingQuestionNumber = 20,
  lang = 'th'
}: DailyLifeFormProps) {
  const t = lang === 'th' ? th.form.dailyLife : en.form.dailyLife;

  const getOptionLabel = (option: string): string => {
    if (lang === 'th') return option;

    const map: Record<string, string> = {
      // Brushing
      'แปรงฟันได้': t.brushing.good,
      'แปรงฟันไม่ถนัด': t.brushing.difficult,

      // Rinsing
      'บ้วนปากได้': t.rinsing.good,
      'บ้วนปากไม่ได้': t.rinsing.difficult,
      'ไม่ได้บ้วนปาก': t.rinsing.none,

      // Food Types
      'อาหารเหลวใสไม่มีกาก เช่น น้ำซุปใส น้ำผลไม้กรอง นม': t.foodTypes.liquid,
      'อาหารปั่นเหลวมีกาก เช่น โจ๊กปั่นเหลว ไก่ปั่น': t.foodTypes.pureed,
      'อาหารอ่อน เช่น โจ๊ก ข้าวต้ม ไข่ลวก ผักนึ่ง': t.foodTypes.soft,
      'อาหารปกติแต่เว้นอาหารรสจัด เผ็ด ร้อน แข็ง เหนียว': t.foodTypes.regular,

      // Food Amount
      'รับประทานอาหารปริมาณปกติ': t.foodAmount.normal,
      'รับประทานอาหารได้น้อยลง': t.foodAmount.less,

      // NG Tube
      'สายยางอยู่ในตำแหน่งเดิม,  เทปยึดจมูกกับสายแน่นดี ไม่เลื่อนหลุด': t.ngTube.secure,
      'สายยางเลื่อนตำแหน่ง, เทปยึดจมูกกับสายไม่แน่น, เลื่อนหลุด': t.ngTube.loose,
    };

    return map[option] || option;
  };

  // Clear conditional description fields when parent field changes
  React.useEffect(() => {
    const updates: Partial<PatientFormData> = {};

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
      onValidationChange(validateDailyLife());
    }
  }, [data, onValidationChange]);

  // Dynamic question numbering
  const questionNumbers = React.useMemo(() => {
    let num = startingQuestionNumber;
    const numbers: Record<string, number> = {};

    numbers.brushing = ++num;
    numbers.rinsing = ++num;
    numbers.foodTypes = ++num;
    numbers.foodAmount = ++num;

    // Check if additional questions appear for everyone
    numbers.questions = ++num;

    if (data.special_ng_tube) numbers.ngTube = ++num;

    return numbers;
  }, [startingQuestionNumber, data.special_ng_tube]);

  return (
    <div className="space-y-6">
      <h2 className="text-xl sm:text-2xl font-bold text-gray-800 mb-6">
        {t.title}
      </h2>

      {/* Brushing Teeth */}
      <div>
        <label className="block text-sm sm:text-base text-gray-700 font-medium mb-2">
          {questionNumbers.brushing}. {t.brushing.label} <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {BRUSHING_TEETH_OPTIONS.map(option => (
            <label key={option} className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="brushing"
                value={option}
                checked={data.brushing_teeth === option}
                onChange={(e) => onChange({ brushing_teeth: e.target.value })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-sm sm:text-base text-gray-700">{getOptionLabel(option)}</span>
            </label>
          ))}
        </div>
        {data.brushing_teeth && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              {t.brushing.desc}
            </label>
            <textarea
              value={data.brushing_description || ''}
              onChange={(e) => onChange({ brushing_description: e.target.value })}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
              rows={1}
            />
          </div>
        )}
      </div>

      {/* Mouth Rinsing */}
      <div>
        <label className="block text-sm sm:text-base text-gray-700 font-medium mb-2">
          {questionNumbers.rinsing}. {t.rinsing.label} <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {MOUTH_RINSING_OPTIONS.map(option => (
            <label key={option} className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="rinsing"
                value={option}
                checked={data.mouth_rinsing === option}
                onChange={(e) => onChange({ mouth_rinsing: e.target.value })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-sm sm:text-base text-gray-700">{getOptionLabel(option)}</span>
            </label>
          ))}
        </div>
        {data.mouth_rinsing && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              {t.brushing.desc}
            </label>
            <textarea
              value={data.rinsing_description || ''}
              onChange={(e) => onChange({ rinsing_description: e.target.value })}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
              rows={1}
            />
          </div>
        )}
      </div>

      {/* Food Types */}
      <div>
        <label className="block text-sm sm:text-base text-gray-700 font-medium mb-2">
          {questionNumbers.foodTypes}. {t.foodTypes.label} <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2 border border-gray-200 rounded-lg p-4">
          {FOOD_TYPE_OPTIONS.map((option) => (
            <label key={option} className="flex items-start cursor-pointer">
              <input
                type="checkbox"
                checked={!!(data.food_types?.some(t => t === option))}
                onChange={(e) => {
                  const current = data.food_types || [];
                  const val = option as any;
                  if (e.target.checked) {
                    onChange({ food_types: [...current, val] });
                  } else {
                    onChange({ food_types: current.filter(t => t !== val) });
                  }
                }}
                className="w-4 h-4 text-blue-600 mt-1"
              />
              <span className="ml-2 text-sm sm:text-base text-gray-700">{getOptionLabel(option)}</span>
            </label>
          ))}
          <div className="flex items-start">
            <label className="flex items-start cursor-pointer">
              <input
                type="checkbox"
                checked={data.food_types?.some(t => !FOOD_TYPE_OPTIONS.includes(t as any)) || false}
                onChange={(e) => {
                  const standardTypes = data.food_types?.filter(t => FOOD_TYPE_OPTIONS.includes(t as any)) || [];
                  if (e.target.checked) {
                    onChange({ food_types: [...standardTypes, ''] });
                  } else {
                    onChange({ food_types: standardTypes });
                  }
                }}
                className="w-4 h-4 text-blue-600 mt-1"
              />
              <span className="ml-2 text-sm sm:text-base text-gray-700">{t.foodTypes.other}:</span>
            </label>
            <input
              type="text"
              value={data.food_types?.find(t => !FOOD_TYPE_OPTIONS.includes(t as any)) || ''}
              onChange={(e) => {
                const standardTypes = data.food_types?.filter(t => FOOD_TYPE_OPTIONS.includes(t as any)) || [];
                onChange({
                  food_types: e.target.value ? [...standardTypes, e.target.value] : standardTypes
                });
              }}
              onFocus={() => {
                if (!data.food_types?.some(t => !FOOD_TYPE_OPTIONS.includes(t as any))) {
                  const standardTypes = data.food_types?.filter(t => FOOD_TYPE_OPTIONS.includes(t as any)) || [];
                  onChange({ food_types: [...standardTypes, ''] });
                }
              }}
              className="ml-2 px-3 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent flex-1"
            />
          </div>
        </div>
      </div>

      {/* Food Amount */}
      <div>
        <label className="block text-sm sm:text-base text-gray-700 font-medium mb-2">
          {questionNumbers.foodAmount}. {t.foodAmount.label} <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {FOOD_AMOUNT_OPTIONS.map(option => (
            <label key={option} className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="food_amount"
                value={option}
                checked={data.food_amount === option}
                onChange={(e) => onChange({ food_amount: e.target.value as typeof data.food_amount })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-sm sm:text-base text-gray-700">{getOptionLabel(option)}</span>
            </label>
          ))}
        </div>
        {data.food_amount && (
          <div className="mt-3 ml-6">
            <label className="block text-gray-600 text-sm mb-1">
              {t.foodAmount.desc}
            </label>
            <textarea
              value={data.food_amount_description || ''}
              onChange={(e) => onChange({ food_amount_description: e.target.value })}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
              rows={1}
            />
          </div>
        )}
      </div>

      {/* Additional Questions */}
      <div>
        <label className="block text-sm sm:text-base text-gray-700 font-medium mb-2">
          {questionNumbers.questions}. {t.questions.label}
        </label>
        <textarea
          value={data.additional_questions || ''}
          onChange={(e) => onChange({ additional_questions: e.target.value })}
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder={t.questions.placeholder}
        />
      </div>

      {/* NG Tube (Conditional) */}
      {data.special_ng_tube && (
        <div className="animate-in fade-in slide-in-from-top-2">
          <label className="block text-sm sm:text-base text-gray-700 font-medium mb-2">
            {questionNumbers.ngTube}. {t.ngTube.label} <span className="text-red-500">*</span>
          </label>
          <div className="space-y-2">
            {NG_TUBE_OPTIONS.map(option => (
              <label key={option} className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  name="ng_tube"
                  value={option}
                  checked={data.ng_tube_position === option}
                  onChange={(e) => onChange({ ng_tube_position: e.target.value as typeof data.ng_tube_position })}
                  className="w-4 h-4 text-blue-600"
                />
                <span className="ml-2 text-sm sm:text-base text-gray-700">{getOptionLabel(option)}</span>
              </label>
            ))}
          </div>
          {data.ng_tube_position && (
            <div className="mt-3 ml-6">
              <label className="block text-gray-600 text-sm mb-1">
                {t.foodAmount.desc}
              </label>
              <textarea
                value={data.ng_tube_description || ''}
                onChange={(e) => onChange({ ng_tube_description: e.target.value })}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
                rows={1}
              />
            </div>
          )}
        </div>
      )}

      {/* Ready to Submit */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-8">
        <h3 className="font-bold text-blue-900 mb-2 flex items-center">
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          {t.readySubmit.title}
        </h3>
        <p className="text-blue-800 text-sm">
          {t.readySubmit.desc}
        </p>
      </div>
    </div>
  );
}
