import React from 'react';
import { Plus, X } from 'lucide-react';
import type { PatientFormData } from '@/lib';
import { GENDER_OPTIONS, PROCEDURE_OPTIONS } from '@/lib';
import { th, en } from '@/lib/locales';

interface BasicInfoFormProps {
  data: PatientFormData;
  onChange: (data: Partial<PatientFormData>) => void;
  onValidationChange?: (isValid: boolean) => void;
  lang?: 'th' | 'en';
}

export function validateBasicInfo(_data: PatientFormData): boolean {
  return true;
}



export default function BasicInfoForm({ data, onChange, onValidationChange, lang = 'th' }: BasicInfoFormProps) {
  const t = lang === 'th' ? th.form.basicInfo : en.form.basicInfo;

  const getOptionLabel = (option: string, _lang?: string): string => {
    if (lang === 'th') return option;

    const map: Record<string, string> = {
      // Gender
      'ชาย': t.genderOptions.male,
      'หญิง': t.genderOptions.female,

      // Procedures
      'ผ่าตัดขากรรไกรบน  (Lefort I)': t.procedureOptions.lefort,
      'ผ่าตัดขากรรไกรล่าง (BSSRO-bilateral sagittal split osteotomy)': t.procedureOptions.bssro,
      'ผ่าตัดถอนฟัน (Surgical removal of tooth)': t.procedureOptions.surgicalRemoval,
      'ถอนฟัน (Extraction)': t.procedureOptions.extraction,
      'การตัดชิ้นเนื้อตรวจ (Biopsy)': t.procedureOptions.biopsy,
      'การตัดถุงน้ำออก (Cyst Enucleation)': t.procedureOptions.cyst,
      'การกรีดและระบายหนอง (Incision and drainage)': t.procedureOptions.incision,
      'การรักษาการแหว่งของสันเหงือกโดยการนำกระดูกสะโพกมาปลูก (Repair alveolar cleft with Iliac crest bone graft)': t.procedureOptions.cleftRepair,
      'ผ่าตัดปุ่มกระดูก (Torectomy)': t.procedureOptions.torectomy,
      'การผ่าตัดเพื่อนำแผ่นโลหะและสกรูออก (Off plate and screws)': t.procedureOptions.plateRemoval,
    };

    return map[option] || option;
  };

  const [customProcedures, setCustomProcedures] = React.useState<string[]>([]);

  // Check if specific procedures are selected
  const hasLefortI = data.procedures?.some(p => p.includes('Lefort I')) || false;
  const hasBSSRO = data.procedures?.some(p => p.includes('BSSRO')) || false;
  const hasBiopsy = data.procedures?.some(p => p.includes('Biopsy')) || false;

  // Sync customProcedures from data.procedures when component mounts or data changes
  React.useEffect(() => {
    const currentProcedures = data.procedures || [];
    const customProcs = currentProcedures.filter(p =>
      !PROCEDURE_OPTIONS.includes(p as typeof PROCEDURE_OPTIONS[number])
    );
    if (customProcs.length > 0 && customProcedures.length === 0) {
      setCustomProcedures(customProcs);
    }
  }, [data.procedures, customProcedures.length]);

  React.useEffect(() => {
    const isValid = validateBasicInfo(data);
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

    // Clear sub-options if unchecking
    if (!checked) {
      if (procedure.includes('Lefort I')) {
        onChange({ lefort_sub_options: [] });
      }
      if (procedure.includes('BSSRO')) {
        onChange({ bssro_sub_options: [] });
      }
    }
  };

  const handleSubOptionChange = (type: 'lefort' | 'bssro', option: string, checked: boolean) => {
    const fieldName = type === 'lefort' ? 'lefort_sub_options' : 'bssro_sub_options';
    const current = data[fieldName] || [];
    const updated = checked
      ? [...current, option]
      : current.filter(o => o !== option);
    onChange({ [fieldName]: updated });
  };

  const handleAddProcedureField = () => {
    if (customProcedures.length === 0 || customProcedures[customProcedures.length - 1].trim() !== '') {
      setCustomProcedures([...customProcedures, '']);
    }
  };

  const handleRemoveProcedureField = (index: number) => {
    const updated = customProcedures.filter((_, i) => i !== index);
    setCustomProcedures(updated);

    const currentProcedures = data.procedures || [];
    const standardProcedures = currentProcedures.filter(p =>
      PROCEDURE_OPTIONS.includes(p as typeof PROCEDURE_OPTIONS[number])
    );
    const customProcs = currentProcedures.filter(p =>
      !PROCEDURE_OPTIONS.includes(p as typeof PROCEDURE_OPTIONS[number])
    );
    customProcs.splice(index, 1);
    onChange({ procedures: [...standardProcedures, ...customProcs.filter(p => p)] });
  };

  const handleCustomProcedureChange = (index: number, value: string) => {
    const updatedCustom = [...customProcedures];
    updatedCustom[index] = value;
    setCustomProcedures(updatedCustom);

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
        {t.title}
      </h2>

      {/* Basic Info */}
      <div className="space-y-4">
        {/* 1. First Name */}
        <div>
          <label className="block text-gray-700 font-medium mb-2">
            {++qNum}. {t.firstName} <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={data.first_name || ''}
            onChange={(e) => onChange({ first_name: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder={t.firstName}
          />
        </div>

        {/* 2. Last Name */}
        <div>
          <label className="block text-gray-700 font-medium mb-2">
            {++qNum}. {t.lastName} <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={data.last_name || ''}
            onChange={(e) => onChange({ last_name: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder={t.lastName}
          />
        </div>

        {/* 3. Email */}
        <div>
          <label className="block text-gray-700 font-medium mb-2">
            {++qNum}. {t.email} <span className="text-red-500">*</span>
          </label>
          <input
            type="email"
            value={data.email || ''}
            onChange={(e) => onChange({ email: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="example@email.com"
          />
        </div>

        {/* 4. Phone */}
        <div>
          <label className="block text-gray-700 font-medium mb-2">
            {++qNum}. {t.phone} <span className="text-red-500">*</span>
          </label>
          <input
            type="tel"
            value={data.phone || ''}
            onChange={(e) => onChange({ phone: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder={t.phone}
          />
        </div>

        {/* 5. Birth Year */}
        <div>
          <label className="block text-gray-700 font-medium mb-2">
            {++qNum}. {t.birthYear} <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            value={data.birth_year ?? ""}
            onChange={(e) => {
              const value = e.target.value;
              if (/^\d*$/.test(value)) {
                onChange({ birth_year: value === "" ? undefined : parseInt(value) });
              }
            }}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder={t.birthYear}
          />
        </div>
      </div>

      {/* Age */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. {t.age} <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          inputMode="numeric"
          pattern="[0-9]*"
          value={data.age ?? ""}
          onChange={(e) => {
            const value = e.target.value;
            if (/^\d*$/.test(value)) {
              onChange({ age: value === "" ? undefined : parseInt(value) });
            }
          }}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder={t.age}
        />
      </div>

      {/* Gender */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. {t.gender} <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {GENDER_OPTIONS.map(option => (
            <label key={option} className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="gender"
                value={option}
                checked={data.gender === option}
                onChange={(e) => onChange({ gender: e.target.value })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-gray-700">{getOptionLabel(option, lang)}</span>
            </label>
          ))}
          <div className="flex items-center">
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="gender"
                checked={!!(data.gender && !GENDER_OPTIONS.includes(data.gender as typeof GENDER_OPTIONS[number]))}
                onChange={() => onChange({ gender: ' ' })}
                className="w-4 h-4 text-blue-600"
              />
              <span className="ml-2 text-gray-700">{t.genderOther}:</span>
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
            />
          </div>
        </div>
      </div>

      {/* HN */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. {t.hn} <span className="text-red-500">*</span>
        </label>
        <input
          type="number"
          value={data.hn || ''}
          onChange={(e) => onChange({ hn: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder=""
        />
      </div>

      {/* Procedures */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. {t.procedures} <span className="text-red-500">*</span>
        </label>
        <div className="space-y-3 border border-gray-200 rounded-lg p-4">
          {PROCEDURE_OPTIONS.map(procedure => (
            <div key={procedure}>
              <label className="flex items-start cursor-pointer">
                <input
                  type="checkbox"
                  checked={data.procedures?.includes(procedure) || false}
                  onChange={(e) => handleProcedureChange(procedure, e.target.checked)}
                  className="w-4 h-4 text-blue-600 mt-1"
                />
                <span className="ml-2 text-gray-700">{getOptionLabel(procedure, lang)}</span>
              </label>

              {/* Sub-options for Lefort I */}
              {procedure.includes('Lefort I') && hasLefortI && (
                <div className="ml-6 mt-2 p-3 rounded-lg">
                  <p className="text-sm text-gray-600 mb-2">{t.subOptions}:</p>
                  <div className="flex flex-wrap gap-2">
                    {["Advancement", "Setback", "Osteotomy", "2 pieces", "Impaction"].map(option => (
                      <label key={option} className="inline-flex items-center px-3 py-1 bg-white border border-blue-200 rounded-full hover:bg-blue-100 cursor-pointer transition-colors">
                        <input
                          type="checkbox"
                          checked={data.lefort_sub_options?.includes(option) || false}
                          onChange={(e) => handleSubOptionChange('lefort', option, e.target.checked)}
                          className="w-3 h-3 text-blue-600 mr-2"
                        />
                        <span className="text-sm">{option}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {/* Sub-options for BSSRO */}
              {procedure.includes('BSSRO') && hasBSSRO && (
                <div className="ml-6 mt-2 p-3 rounded-lg">
                  <p className="text-sm text-gray-600 mb-2">{t.subOptions}:</p>
                  <div className="flex flex-wrap gap-2">
                    {["Setback", "Advancement"].map(option => (
                      <label key={option} className="inline-flex items-center px-3 py-1 bg-white border border-green-200 rounded-full hover:bg-green-100 cursor-pointer transition-colors">
                        <input
                          type="checkbox"
                          checked={data.bssro_sub_options?.includes(option) || false}
                          onChange={(e) => handleSubOptionChange('bssro', option, e.target.checked)}
                          className="w-3 h-3 text-green-600 mr-2"
                        />
                        <span className="text-sm">{option}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {/* Surgical Tooth */}
              {((procedure.includes('ผ่าตัดถอนฟัน') && data.procedures?.includes(procedure)) || (procedure.includes('ถอนฟัน') && data.procedures?.includes(procedure))) && (
                <div className="ml-6 mt-2 p-3 rounded-lg">
                  <label className="block text-gray-600 text-sm mb-2">{t.surgicalTooth}:</label>
                  <input
                    type="text"
                    value={procedure.includes('ผ่าตัดถอนฟัน') ? (data.surgical_tooth_numbers || '') : (data.extraction_tooth_numbers || '')}
                    onChange={e => {
                      if (procedure.includes('ผ่าตัดถอนฟัน')) {
                        onChange({ surgical_tooth_numbers: e.target.value });
                      } else {
                        onChange({ extraction_tooth_numbers: e.target.value });
                      }
                    }}
                    className="w-full px-3 py-2 border border-yellow-400 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                    placeholder={t.surgicalTooth}
                  />
                </div>
              )}

              {/* Sub-options for Biopsy */}
              {procedure.includes('Biopsy') && hasBiopsy && (
                <div className="ml-6 mt-2 p-3 rounded-lg">
                  <p className="text-sm text-gray-600 mb-2">{t.subOptions}:</p>
                  <div className="flex flex-wrap gap-2">
                    {["Excisional", "Incisional"].map(option => (
                      <label key={option} className="inline-flex items-center px-3 py-1 bg-white border border-pink-200 rounded-full hover:bg-pink-100 cursor-pointer transition-colors">
                        <input
                          type="checkbox"
                          checked={data.biopsy_sub_options?.includes(option) || false}
                          onChange={(e) => {
                            const current = data.biopsy_sub_options || [];
                            const updated = e.target.checked
                              ? [...current, option]
                              : current.filter(o => o !== option);
                            onChange({ biopsy_sub_options: updated });
                          }}
                          className="w-3 h-3 text-pink-600 mr-2"
                        />
                        <span className="text-sm">{option}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}

          {/* Other Procedures */}
          <div className="mt-4 pt-4 border-t border-gray-200">
            <label className="block text-gray-700 font-medium mb-3">{t.otherProcedures}:</label>
            <div className="space-y-2">
              {customProcedures.map((proc, index) => (
                <div key={index} className="flex items-center gap-2">
                  <input
                    type="text"
                    value={proc}
                    onChange={(e) => handleCustomProcedureChange(index, e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder={t.otherProceduresPlaceholder}
                  />
                  <button
                    type="button"
                    onClick={() => handleRemoveProcedureField(index)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
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
                {t.addProcedure}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Special Procedures */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. {t.specialProcedures}
        </label>
        <div className="space-y-3 border border-gray-200 rounded-lg p-4">
          {/* IMF Wire */}
          <div className="rounded-lg p-4 border border-gray-200">
            <div className="flex items-center gap-4 mb-2">
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={!!data.imf_wire}
                  onChange={(e) => {
                    onChange({ imf_wire: e.target.checked });
                    if (!e.target.checked && !data.imf_elastic) {
                      onChange({ has_imf: 'ไม่มีการมัดฟัน', imf_loops: undefined, imf_wire_loops: undefined });
                    } else if (e.target.checked) {
                      onChange({ has_imf: 'มีการมัดฟัน' });
                    }
                  }}
                  className="w-4 h-4 text-purple-600"
                />
                <span className="ml-2 font-medium text-gray-700">{t.imfWire}</span>
              </label>
            </div>
            {data.imf_wire && (
              <div className="ml-6">
                <label className="block text-sm text-gray-600 mb-1">{t.loops}:</label>
                <input
                  type="number"
                  min="1"
                  max="20"
                  value={data.imf_wire_loops || ''}
                  onChange={(e) => onChange({ imf_wire_loops: e.target.value ? parseInt(e.target.value) : undefined, imf_loops: e.target.value ? parseInt(e.target.value) : undefined })}
                  className="w-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 text-sm"
                  placeholder="Count"
                />
              </div>
            )}
          </div>

          {/* IMF Elastic */}
          <div className="rounded-lg p-4 border border-gray-200">
            <div className="flex items-center gap-4 mb-2">
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={!!data.imf_elastic}
                  onChange={(e) => {
                    onChange({ imf_elastic: e.target.checked });
                    if (!e.target.checked && !data.imf_wire) {
                      onChange({ has_imf: 'ไม่มีการมัดฟัน', imf_loops: undefined, imf_elastic_loops: undefined });
                    } else if (e.target.checked) {
                      onChange({ has_imf: 'มีการมัดฟัน' });
                    }
                  }}
                  className="w-4 h-4 text-purple-600"
                />
                <span className="ml-2 font-medium text-gray-700">{t.imfElastic}</span>
              </label>
            </div>
            {data.imf_elastic && (
              <div className="ml-6">
                <label className="block text-sm text-gray-600 mb-1">{t.loops}:</label>
                <input
                  type="number"
                  min="1"
                  max="20"
                  value={data.imf_elastic_loops || ''}
                  onChange={(e) => onChange({ imf_elastic_loops: e.target.value ? parseInt(e.target.value) : undefined, imf_loops: e.target.value ? parseInt(e.target.value) : undefined })}
                  className="w-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 text-sm"
                  placeholder="Count"
                />
              </div>
            )}
          </div>

          {/* ICBG */}
          <div className="rounded-lg p-4 border border-gray-200">
            <div className="flex items-center gap-4 mb-2">
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={!!data.special_icbg && data.special_icbg !== 'ไม่ทำ'}
                  onChange={(e) => {
                    if (e.target.checked) {
                      onChange({ special_icbg: 'มี' });
                    } else {
                      onChange({ special_icbg: 'ไม่ทำ', special_icbg_description: '' });
                    }
                  }}
                  className="w-4 h-4 text-blue-600"
                />
                <span className="ml-2 font-medium text-gray-700">{t.icbg}</span>
              </label>
            </div>
            {data.special_icbg === 'มี' && (
              <div className="ml-6">
                <label className="block text-sm text-gray-600 mb-1">{t.icbgDesc}:</label>
                <input
                  type="text"
                  value={data.special_icbg_description || ''}
                  onChange={(e) => onChange({ special_icbg_description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                  placeholder={t.icbgDesc}
                  maxLength={100}
                />
              </div>
            )}
          </div>

          {/* NG tube */}
          <div className="rounded-lg p-4 border border-gray-200">
            <div className="flex items-center gap-4 mb-2">
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={!!data.special_ng_tube && data.special_ng_tube !== 'ไม่ทำ'}
                  onChange={(e) => {
                    if (e.target.checked) {
                      onChange({ special_ng_tube: 'มี' });
                    } else {
                      onChange({ special_ng_tube: 'ไม่ทำ', special_ng_tube_description: '' });
                    }
                  }}
                  className="w-4 h-4 text-green-600"
                />
                <span className="ml-2 font-medium text-gray-700">{t.ngTube}</span>
              </label>
            </div>
            {data.special_ng_tube === 'มี' && (
              <div className="ml-6">
                <label className="block text-sm text-gray-600 mb-1">{t.ngTubeDesc}:</label>
                <input
                  type="text"
                  value={data.special_ng_tube_description || ''}
                  onChange={(e) => onChange({ special_ng_tube_description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 text-sm"
                  placeholder={t.ngTubeDesc}
                  maxLength={100}
                />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Surgery Date */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. {t.surgeryDate} <span className="text-red-500">*</span>
        </label>
        <input
          type="date"
          value={data.surgery_date || ''}
          onChange={(e) => onChange({ surgery_date: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Discharge Date */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. {t.dischargeDate} <span className="text-red-500">*</span>
        </label>
        <input
          type="date"
          value={data.discharge_date || ''}
          onChange={(e) => onChange({ discharge_date: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Note */}
      <div>
        <label className="block text-gray-700 font-medium mb-2">
          {++qNum}. {t.note}
        </label>
        <textarea
          value={data.note || ''}
          onChange={(e) => onChange({ note: e.target.value })}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
          placeholder=""
          rows={4}
        />
      </div>
    </div>
  );
}
