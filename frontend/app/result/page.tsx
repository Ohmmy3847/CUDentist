'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Download, Share2, CheckCircle, AlertTriangle, XCircle, ChevronDown, ChevronUp, FileText, MessageCircle, Loader2 } from 'lucide-react';
import type { ThreeLayerResult, PatientFormData } from '@/lib';
import RiskResult from '@/components/RiskResult';
import { th, en } from '@/lib/locales';
import { getSymptomLabel } from '@/lib/symptomMappings';

// Helper functions (outside component for better performance)
const translateFieldValue = (key: string, value: string, language: string): string => {
  // For other_symptoms field, check if value is a symptom key
  if (key === 'other_symptoms') {
    const translatedSymptom = getSymptomLabel(value, language as 'th' | 'en');
    if (translatedSymptom !== value) {
      return translatedSymptom; // Found symptom mapping
    }
  }
  
  // Translation map for other field values (TH -> EN) - matching exactly with form options
  const translations: Record<string, string> = {
    // Common answers
    'ปกติ': 'Normal',
    'ไม่ปกติ': 'Abnormal',
    'ใช่': 'Yes',
    'ไม่ใช่': 'No',
    'มี': en.form.symptoms.breathing.yes,
    'ไม่มี': en.form.symptoms.breathing.no,
    
    // Gender - exact matches from BasicInfoForm
    'ชาย': en.form.basicInfo.genderOptions.male,
    'หญิง': en.form.basicInfo.genderOptions.female,
    
    // Procedures - exact matches from BasicInfoForm
    'ผ่าตัดขากรรไกรบน  (Lefort I)': en.form.basicInfo.procedureOptions.lefort,
    'ผ่าตัดขากรรไกรล่าง (BSSRO-bilateral sagittal split osteotomy)': en.form.basicInfo.procedureOptions.bssro,
    'ผ่าตัดถอนฟัน (Surgical removal of tooth)': en.form.basicInfo.procedureOptions.surgicalRemoval,
    'ถอนฟัน (Extraction)': en.form.basicInfo.procedureOptions.extraction,
    'การตัดชิ้นเนื้อตรวจ (Biopsy)': en.form.basicInfo.procedureOptions.biopsy,
    'การตัดถุงน้ำออก (Cyst Enucleation)': en.form.basicInfo.procedureOptions.cyst,
    'การกรีดและระบายหนอง (Incision and drainage)': en.form.basicInfo.procedureOptions.incision,
    'การรักษาการแหว่งของสันเหงือกโดยการนำกระดูกสะโพกมาปลูก (Repair alveolar cleft with Iliac crest bone graft)': en.form.basicInfo.procedureOptions.cleftRepair,
    'ผ่าตัดปุ่มกระดูก (Torectomy)': en.form.basicInfo.procedureOptions.torectomy,
    'การผ่าตัดเพื่อนำแผ่นโลหะและสกรูออก (Off plate and screws)': en.form.basicInfo.procedureOptions.plateRemoval,
    
    // Pain medication - exact matches from SymptomsForm
    'ดีขึ้น': en.form.symptoms.painMed.better,
    'ไม่ดีขึ้น': en.form.symptoms.painMed.notBetter,
    'ไม่ได้ทานยาแก้ปวด': en.form.symptoms.painMed.notTaken,
    
    // Swelling - exact matches from SymptomsForm
    'ปัจจุบันหายบวมแล้ว': en.form.symptoms.swelling.gone,
    'บวมลดลง': en.form.symptoms.swelling.reduced,
    'บวมเท่าเดิม': en.form.symptoms.swelling.noChange,
    'บวมมากขึ้น': en.form.symptoms.swelling.increased,
    'บวมมากขึ้นมากๆจนกระทบการใช้ชีวิตประจำวัน': en.form.symptoms.swelling.severe,
    
    // Bleeding - exact matches from SymptomsForm
    'ไม่มีเลือดซึมหรือไหลแล้ว': en.form.symptoms.bleeding.no,
    'เลือดซึม แต่หยุดได้เอง': en.form.symptoms.bleeding.slight,
    'เลือดสีแดงสดไหลไม่หยุดปริมาณมาก': en.form.symptoms.bleeding.heavy,
    
    // Fever - exact matches from SymptomsForm
    'ไม่มีไข้': en.form.symptoms.fever.no,
    'มีไข้ (มากกว่า 38 องศาเซลเซียส)': en.form.symptoms.fever.yes,
    'มีไข้': en.form.symptoms.fever.yes,
    
    // Numbness - exact matches from SymptomsForm
    'หายชาแล้วหลังทำหัตถการ': en.form.symptoms.numbness.resolved,
    'ยังชาอยู่แต่ชาน้อยลงเรื่อยๆ': en.form.symptoms.numbness.improving,
    'ยังรู้สึกชาเท่ากับตอนหลังทำหัตถการทันที': en.form.symptoms.numbness.unchanged,
    
    // Phlebitis - exact matches from SymptomsForm
    'ไม่มีอาการปวด/บวม/แดง รอบรอยเข็ม': en.form.symptoms.phlebitis.no,
    'มีอาการปวด/บวม/แดง รอบรอยเข็ม': en.form.symptoms.phlebitis.yes,
    
    // Suture - exact matches from SymptomsForm
    'ไหมแน่นดี / ไม่ได้สังเกต': en.form.symptoms.suture.secure,
    'ไหมหลุดหายไปบางส่วน แต่ไม่มีเลือดไหล': en.form.symptoms.suture.loose,
    'ไหมหลุดหายไปบางส่วน และมีอาการเลือดสีแดงสดไหล': en.form.symptoms.suture.bleeding,
    
    // Antibiotics - exact matches from SymptomsForm
    'ครบตามแพทย์สั่ง': en.form.symptoms.antibiotic.all,
    'ลืมทานบางครั้ง': en.form.symptoms.antibiotic.missed,
    'ไม่ได้ทานเลย': en.form.symptoms.antibiotic.none,
    'ไม่ได้ทาน': en.form.symptoms.antibiotic.none,
    
    // Compress - exact matches from SymptomsForm
    'ประคบเย็นอยู่': en.form.symptoms.compress.cold,
    'ประคบอุ่นอยู่': en.form.symptoms.compress.warm,
    'ไม่ได้ประคบอะไรเลย': en.form.symptoms.compress.none,
    
    // IMF Wire - exact matches from SymptomsForm
    'ลวด/ยางมัดฟันแน่นดี': en.form.symptoms.imfWire.tight,
    'ลวด/ยางมัดฟันหลวม อ้าปากได้เล็กน้อย': en.form.symptoms.imfWire.loose,
    'ยางมัดฟันขาดไปบางเส้น แต่ยังอ้าปากไม่ได้': en.form.symptoms.imfWire.broken,
    
    // Walking - exact matches from SymptomsForm
    'เดินได้ปกติ': en.form.symptoms.walking.normal,
    'เดินไม่ถนัด': en.form.symptoms.walking.difficult,
    
    // Tooth brushing - exact matches from DailyLifeForm
    'แปรงฟันได้': en.form.dailyLife.brushing.good,
    'แปรงฟันไม่ถนัด': en.form.dailyLife.brushing.difficult,
    
    // Mouth rinsing - exact matches from DailyLifeForm
    'บ้วนปากได้': en.form.dailyLife.rinsing.good,
    'บ้วนปากไม่ได้': en.form.dailyLife.rinsing.difficult,
    'ไม่ได้บ้วนปาก': en.form.dailyLife.rinsing.none,
    
    // Food types - exact matches from DailyLifeForm
    'อาหารเหลวใสไม่มีกาก เช่น น้ำซุปใส น้ำผลไม้กรอง นม': en.form.dailyLife.foodTypes.liquid,
    'อาหารปั่นเหลวมีกาก เช่น โจ๊กปั่นเหลว ไก่ปั่น': en.form.dailyLife.foodTypes.pureed,
    'อาหารอ่อน เช่น โจ๊ก ข้าวต้ม ไข่ลวก ผักนึ่ง': en.form.dailyLife.foodTypes.soft,
    'อาหารปกติแต่เว้นอาหารรสจัด เผ็ด ร้อน แข็ง เหนียว': en.form.dailyLife.foodTypes.regular,
    
    // Food amount - exact matches from DailyLifeForm
    'รับประทานอาหารปริมาณปกติ': en.form.dailyLife.foodAmount.normal,
    'รับประทานอาหารได้น้อยลง': en.form.dailyLife.foodAmount.less,
    
    // NG Tube position - exact matches from DailyLifeForm
    'สายยางอยู่ในตำแหน่งเดิม,  เทปยึดจมูกกับสายแน่นดี ไม่เลื่อนหลุด': en.form.dailyLife.ngTube.secure,
    'สายยางเลื่อนตำแหน่ง, เทปยึดจมูกกับสายไม่แน่น, เลื่อนหลุด': en.form.dailyLife.ngTube.loose,
  };

  if (language === 'en' && translations[value]) {
    return translations[value];
  }
  
  return value;
};

const formatFieldValue = (key: string, value: unknown, t: typeof th, language: string = 'th'): React.ReactNode => {
  if (value === undefined || value === null || value === '') return t.common.notSpecified;

  // จัดการ boolean
  if (typeof value === 'boolean') {
    return value ? t.common.yes : t.common.no;
  }

  // จัดการ array - แสดงเป็นบรรทัดใหม่ และแปลภาษา
  if (Array.isArray(value)) {
    if (value.length === 0) return t.common.notSpecified;
    return (
      <div className="space-y-1">
        {value.map((item, index) => (
          <div key={index}>• {translateFieldValue(key, String(item), language)}</div>
        ))}
      </div>
    );
  }

  // จัดการ special fields
  if (key === 'pain_score') {
    return `${value} / 10`;
  }

  if (key === 'imf_loops') {
    return `${value} loop`;
  }

  // แปลภาษาสำหรับ string values
  return translateFieldValue(key, String(value), language);
};

const getDynamicLabels = (data: PatientFormData | null, t: typeof th): Record<string, string> => {
  const baseLabels: Record<string, string> = {
    // ข้อมูลพื้นฐาน
    first_name: `1. ${t.form.basicInfo.firstName}`,
    last_name: `2. ${t.form.basicInfo.lastName}`,
    email: `3. ${t.form.basicInfo.email}`,
    phone: `4. ${t.form.basicInfo.phone}`,
    birth_year: `5. ${t.form.basicInfo.birthYear}`,
    age: `6. ${t.form.basicInfo.age}`,
    gender: `7. ${t.form.basicInfo.gender}`,
    hn: `8. ${t.form.basicInfo.hn}`,
    procedures: `9. ${t.form.basicInfo.procedures}`,

    // รายละเอียดหัตถการ (Sub-options)
    lefort_sub_options: `9.1 ${t.form.basicInfo.subOptions} (Lefort I)`,
    bssro_sub_options: `9.2 ${t.form.basicInfo.subOptions} (BSSRO)`,
    surgical_tooth_numbers: `9.3 ${t.form.basicInfo.surgicalTooth}`,
    extraction_tooth_numbers: `9.4 ${t.form.basicInfo.surgicalTooth}`,
    biopsy_sub_options: `9.5 ${t.form.basicInfo.subOptions} (Biopsy)`,

    // หัตถการอื่นๆ (ข้อ 10)
    imf_wire: `10.1 ${t.form.basicInfo.imfWire}`,
    imf_elastic: `10.2 ${t.form.basicInfo.imfElastic}`,
    imf_loops: t.form.basicInfo.loops,
    special_icbg: `10.3 ${t.form.basicInfo.icbg}`,
    special_icbg_description: t.form.basicInfo.icbgDesc,
    special_ng_tube: `10.4 ${t.form.basicInfo.ngTube}`,
    special_ng_tube_description: t.form.basicInfo.ngTubeDesc,

    // วันที่และหมายเหตุ
    surgery_date: `11. ${t.form.basicInfo.surgeryDate}`,
    discharge_date: `12. ${t.form.basicInfo.dischargeDate}`,
    note: `13. ${t.form.basicInfo.note}`,
  };

  if (!data) return baseLabels;

  // Dynamic numbering logic based on SymptomsForm & DailyLifeForm logic
  let qNum = 13;
  const addLabel = (key: string, label: string, isSub: boolean = false) => {
    if (!isSub) qNum++;
    baseLabels[key] = isSub ? `${qNum}.1 ${label}` : `${qNum}. ${label}`;
  };

  // --- Symptoms Form ---
  addLabel('pain_score', t.form.symptoms.pain.label);
  baseLabels['pain_description'] = `${qNum}.1 ${t.form.symptoms.pain.desc}`;
  baseLabels['pain_score_description'] = `${qNum}.1 ${t.form.symptoms.pain.desc}`;

  if ((data.pain_score || 0) > 0) {
    addLabel('pain_medication_effect', t.form.symptoms.painMed.label);
    baseLabels['pain_medication_effective'] = baseLabels['pain_medication_effect'];
  }

  addLabel('swelling_status', t.form.symptoms.swelling.label);
  baseLabels['swelling_description'] = `${qNum}.1 ${t.form.symptoms.swelling.desc}`;

  addLabel('breathing_or_swallowing_difficulty', t.form.symptoms.breathing.label);
  baseLabels['breathing_description'] = `${qNum}.1 ${t.form.symptoms.breathing.label}`; // Reusing label as desc placeholder if needed

  addLabel('bleeding_status', t.form.symptoms.bleeding.label);
  baseLabels['bleeding_description'] = `${qNum}.1 ${t.form.symptoms.bleeding.label}`;

  addLabel('fever_status', t.form.symptoms.fever.label);
  baseLabels['fever_description'] = `${qNum}.1 ${t.form.symptoms.fever.desc}`;

  addLabel('numbness_status', t.form.symptoms.numbness.label);
  baseLabels['numbness_description'] = `${qNum}.1 ${t.form.symptoms.numbness.desc}`;

  addLabel('phlebitis', t.form.symptoms.phlebitis.label);
  baseLabels['phlebitis_description'] = `${qNum}.1 ${t.form.symptoms.phlebitis.label}`;

  addLabel('suture_status', t.form.symptoms.suture.label);
  baseLabels['suture_description'] = `${qNum}.1 ${t.form.symptoms.suture.label}`;

  addLabel('other_symptoms', t.form.symptoms.other.label);
  baseLabels['other_symptoms_custom'] = `${qNum}.1 ${t.form.symptoms.other.customLabel}`;

  addLabel('antibiotic_compliance', t.form.symptoms.antibiotic.label);
  baseLabels['antibiotic_description'] = `${qNum}.1 ${t.form.symptoms.antibiotic.forgotCount}`;

  addLabel('compress_type', t.form.symptoms.compress.label);

  // IMF Wire/Elastic check
  if (data.has_imf === 'มีการมัดฟัน' || data.imf_wire || data.imf_elastic) {
    addLabel('imf_wire_status', t.form.symptoms.imfWire.label);
    baseLabels['imf_wire_description'] = `${qNum}.1 ${t.form.symptoms.imfWire.label}`;
  }

  // ICBG check
  if (data.special_icbg === 'มี') {
    addLabel('walking_status', t.form.symptoms.walking.label);
    baseLabels['walking_description'] = `${qNum}.1 ${t.form.symptoms.walking.label}`;
  }

  // --- Daily Life Form ---
  addLabel('brushing_teeth', t.form.dailyLife.brushing.label);
  baseLabels['brushing_description'] = `${qNum}.1 ${t.form.dailyLife.brushing.desc}`;

  addLabel('mouth_rinsing', t.form.dailyLife.rinsing.label);
  baseLabels['rinsing_description'] = `${qNum}.1 ${t.form.dailyLife.rinsing.label}`;

  addLabel('food_types', t.form.dailyLife.foodTypes.label);
  baseLabels['food_types_custom'] = `${qNum}.1 ${t.form.dailyLife.foodTypes.other}`;

  addLabel('food_amount', t.form.dailyLife.foodAmount.label);
  baseLabels['food_amount_description'] = `${qNum}.1 ${t.form.dailyLife.foodAmount.desc}`;

  addLabel('additional_questions', t.form.dailyLife.questions.label);

  // NG Tube check
  if (data.special_ng_tube === 'มี') {
    addLabel('ng_tube_position', t.form.dailyLife.ngTube.label);
    baseLabels['ng_tube_description'] = `${qNum}.1 ${t.form.dailyLife.ngTube.label}`;
  }

  return baseLabels;
};

const shouldSkipField = (key: string, value: any): boolean => {
  if (value === undefined || value === null || value === '') return true;
  if (key === 'has_imf') return true;
  if (key === 'imf_type') return true; // Legacy field
  if (key === 'pain_medication_effective') return true;
  if (key === 'pain_score_description') return true;
  if (key === 'imf_wire' && value === false) return true;
  if (key === 'imf_elastic' && value === false) return true;
  if (key === 'special_icbg' && value === 'ไม่ทำ') return true;
  if (key === 'special_ng_tube' && value === 'ไม่ทำ') return true;
  return false;
};

export default function ResultPage() {
  const router = useRouter();
  const [result, setResult] = useState<ThreeLayerResult | null>(null);
  const [patientData, setPatientData] = useState<PatientFormData | null>(null);
  const [showDataPreview, setShowDataPreview] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingProgress, setProcessingProgress] = useState({ current: 0, total: 0, flowName: '' });
  const [error, setError] = useState<string | null>(null);

  // Determine language
  const language = (patientData as any)?._language || 'th';
  const t = language === 'en' ? en : th;

  useEffect(() => {
    console.log('🔵 [RESULT PAGE] useEffect triggered');

    // Use only sessionStorage for persistence across unmount/remount
    const alreadyProcessing = sessionStorage.getItem('isCurrentlyProcessing');
    console.log('🔵 [CHECK] isCurrentlyProcessing:', alreadyProcessing);

    if (alreadyProcessing === 'true') {
      console.log('🚫 [BLOCKED] Already processing - EXITING');
      return;
    }

    // Set flag immediately before any async operations
    sessionStorage.setItem('isCurrentlyProcessing', 'true');
    console.log('✅ [STARTED] Processing flag set to TRUE');

    const performClassification = async () => {
      // Load patient data from sessionStorage
      const storedPatient = sessionStorage.getItem('patientData');
      const isProcessingFlag = sessionStorage.getItem('isProcessing');
      const storedResult = sessionStorage.getItem('riskAssessmentResult');
      const alreadySavedFlag = sessionStorage.getItem('resultSaved');

      console.log('🔵 [FLAGS] resultSaved:', alreadySavedFlag, '| hasResult:', !!storedResult);

      if (!storedPatient) {
        console.log('⚠️ [NO DATA] Redirecting to home');
        router.push('/');
        return;
      }

      const patientFormData = JSON.parse(storedPatient);
      // Ensure language is set from stored data
      setPatientData(patientFormData);

      // If already has result, just display it
      if (storedResult && isProcessingFlag !== 'true') {
        console.log('✅ [CACHED] Using existing result - NO SAVE');
        setResult(JSON.parse(storedResult));
        return;
      }

      // Prevent duplicate saves - check flag BEFORE any async operations
      if (alreadySavedFlag === 'true') {
        console.log('🚫 [DUPLICATE] Already saved flag is TRUE - skipping save');
        // If result exists, just display it
        if (storedResult) {
          setResult(JSON.parse(storedResult));
          return;
        }
        // If no result yet, continue to classification without saving again
        return;
      }

      // Mark as saved immediately to prevent race conditions
      sessionStorage.setItem('resultSaved', 'true');
      console.log('✅ [FIRST RUN] resultSaved flag set - WILL SAVE to backend');

      // Need to perform classification
      setIsProcessing(true);
      sessionStorage.removeItem('isProcessing');

      try {

        // Import api dynamically to avoid circular dependencies
        const { api } = await import('@/lib');

        // Comprehensive patient assessment (3-layer response)

        // Extract language from patient data (added in form page)
        const lang = (patientFormData as any)._language || 'th';

        const classificationResult = await api.assessPatient(
          patientFormData,
          (current: number, total: number, flowName: string) => {
            setProcessingProgress({ current, total, flowName });
          },
          lang
        );

        // Store result and update state
        sessionStorage.setItem('riskAssessmentResult', JSON.stringify(classificationResult));
        sessionStorage.removeItem('isCurrentlyProcessing'); // Clear processing flag when done
        setResult(classificationResult as unknown as ThreeLayerResult);
        setIsProcessing(false);
      } catch (err) {
        sessionStorage.removeItem('isCurrentlyProcessing'); // Clear processing flag on error
        setError(err instanceof Error ? err.message : t.result.error.title);
        console.error('Classification error:', err);
        setIsProcessing(false);
      }
    };

    performClassification();
  }, [router]); // t is not a dependency as it's derived from state/constant

  const getOverallRisk = () => {
    if (!result || !result.flows) return { level: t.common.unknown, count: 0, color: 'gray' };

    // Use summary if available (from LLM)
    if (result.summary) {
      const { overall_risk } = result.summary;

      // Count from flows directly
      const riskLevels = Object.values(result.flows).map((r: any) => r.risk_level);
      const highRisk = riskLevels.filter(r => r.includes('สูง') || r.toLowerCase().includes('high')).length;
      const mediumRisk = riskLevels.filter(r => r.includes('กลาง') || r.includes('ปานกลาง') || r.toLowerCase().includes('moderate')).length;
      const complicatedRisk = riskLevels.filter(r => r.includes('ซับซ้อน') || r.includes('ไม่สามารถสรุป') || r.toLowerCase().includes('complex')).length;
      const lowRisk = riskLevels.filter(r => r.includes('ต่ำ') || r.toLowerCase().includes('low')).length;

      // ลำดับความสำคัญ: HIGH > MEDIUM > COMPLICATED > LOW
      if (overall_risk.includes('สูง') || overall_risk.toLowerCase().includes('high') || highRisk > 0) {
        return { level: t.result.riskLevels.high, count: highRisk, color: 'red' };
      } else if (overall_risk.includes('กลาง') || overall_risk.includes('ปานกลาง') || overall_risk.toLowerCase().includes('moderate') || mediumRisk > 0) {
        return { level: t.result.riskLevels.medium, count: mediumRisk, color: 'yellow' };
      } else if (overall_risk.includes('ซับซ้อน') || overall_risk.includes('ไม่สามารถสรุป') || overall_risk.toLowerCase().includes('complex') || complicatedRisk > 0) {
        return { level: t.result.riskLevels.complex, count: complicatedRisk, color: 'purple' };
      }
      return { level: t.result.riskLevels.low, count: lowRisk, color: 'green' };
    }

    // Fallback: calculate from individual flows
    const riskLevels = Object.values(result.flows).map((r: any) => r.risk_level);
    const highRisk = riskLevels.filter(r => r.includes('สูง') || r.toLowerCase().includes('high')).length;
    const mediumRisk = riskLevels.filter(r => r.includes('กลาง') || r.includes('ปานกลาง') || r.toLowerCase().includes('moderate')).length;
    const complicatedRisk = riskLevels.filter(r => r.includes('ซับซ้อน') || r.includes('ไม่สามารถสรุป') || r.toLowerCase().includes('complex')).length;
    const lowRisk = riskLevels.filter(r => r.includes('ต่ำ') || r.toLowerCase().includes('low')).length;

    // ลำดับความสำคัญ: HIGH > MEDIUM > COMPLICATED > LOW
    if (highRisk > 0) {
      return { level: t.result.riskLevels.high, count: highRisk, color: 'red' };
    } else if (mediumRisk > 0) {
      return { level: t.result.riskLevels.medium, count: mediumRisk, color: 'yellow' };
    } else if (complicatedRisk > 0) {
      return { level: t.result.riskLevels.complex, count: complicatedRisk, color: 'purple' };
    }
    return { level: t.result.riskLevels.low, count: lowRisk, color: 'green' };
  };

  const handleDownloadReport = () => {
    if (!result || !patientData) return;

    const reportData = {
      patient: patientData,
      assessment: result,
      date: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json',
    });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `risk_assessment_${patientData.hn || 'patient'}_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const overallRisk = getOverallRisk();
  const dynamicLabels = getDynamicLabels(patientData, t);

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <Link href="/" className="flex items-center text-gray-600 hover:text-gray-800 mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            {t.result.header.back}
          </Link>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 mb-2">
                {t.result.title}
              </h1>
              {patientData?.hn && (
                <p className="text-gray-600">
                  HN: {patientData.hn} | {t.result.header.assessmentDate}: {new Date().toLocaleDateString(language === 'en' ? 'en-US' : 'th-TH')}
                </p>
              )}
            </div>
            <button
              onClick={handleDownloadReport}
              className="flex items-center px-4 py-2 bg-cu-pink-600 text-white rounded-lg hover:bg-cu-pink-700 transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              {t.result.header.download}
            </button>
          </div>
        </div>

        {/* Loading State */}
        {isProcessing && (
          <div className="mb-8 bg-white rounded-xl shadow-lg p-8">
            <div className="flex items-center mb-6">
              <Loader2 className="animate-spin h-8 w-8 text-cu-pink-600 mr-4" />
              <div className="flex-1">
                <h2 className="text-xl font-bold text-gray-800">{t.result.loading.title}</h2>
                {processingProgress.flowName && (
                  <p className="text-gray-600 mt-1">
                    {processingProgress.flowName}
                  </p>
                )}
              </div>
            </div>

            {/* Progress bar */}
            {processingProgress.total > 0 && (
              <div className="w-full bg-gray-200 rounded-full h-2.5 mb-2">
                <div
                  className="bg-cu-pink-600 h-2.5 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${processingProgress.current}%` }}
                ></div>
              </div>
            )}
            {processingProgress.current > 0 && (
              <p className="text-sm text-gray-600 mb-4 text-center">
                {processingProgress.current}%
              </p>
            )}

            <p className="text-sm text-gray-500 mt-2">
              {t.result.loading.subtitle}
            </p>
          </div>
        )}

        {/* Error display */}
        {error && (
          <div className="mb-8 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 font-medium">{t.result.error.title}</p>
            <p className="text-red-700 text-sm mt-1">{error}</p>
            <button
              onClick={() => router.push('/form')}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              {t.result.error.retry}
            </button>
          </div>
        )}

        {/* Result Content */}
        {!isProcessing && result && (
          <>
            {/* Overall Summary */}
            <div className={`mb-8 rounded-xl shadow-lg p-8 ${
              overallRisk.color === 'red' ? 'bg-red-100 border-2 border-red-300' :
              overallRisk.color === 'yellow' ? 'bg-yellow-100 border-2 border-yellow-300' :
              overallRisk.color === 'purple' ? 'bg-purple-100 border-2 border-purple-300' :
              'bg-green-100 border-2 border-green-300'
              }`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  {overallRisk.color === 'red' ? (
                    <XCircle className="w-16 h-16 text-red-600 mr-4" />
                  ) : overallRisk.color === 'yellow' ? (
                    <AlertTriangle className="w-16 h-16 text-yellow-600 mr-4" />
                  ) : overallRisk.color === 'purple' ? (
                    <AlertTriangle className="w-16 h-16 text-purple-600 mr-4" />
                  ) : (
                    <CheckCircle className="w-16 h-16 text-green-600 mr-4" />
                  )}
                  <div>
                    <h2 className="text-2xl font-bold text-gray-800 mb-1">
                      {t.result.summary.title}: {overallRisk.level}
                    </h2>

                    {result.flows && Object.keys(result.flows).length < 17 && (
                      <p className="text-sm text-orange-600 mt-1">
                        ⚠️ {t.result.summary.note.replace('{count}', String(Object.keys(result.flows).length))}
                      </p>
                    )}
                    <p className="text-sm text-green-600 mt-2 flex items-center">
                      <CheckCircle className="w-4 h-4 mr-1" />
                      {t.result.summary.saved}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* AI-Generated Summary */}
            {result.summary && result.summary.summary && (
              <div className="mb-8">
                <div className="bg-gradient-to-r from-pink-50 to-purple-50 rounded-xl shadow-lg p-8 border-2 border-pink-200">
                  <div className="flex items-start mb-4">
                    <MessageCircle className="w-6 h-6 text-pink-600 mr-3 mt-1" />
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-gray-800 mb-2">
                        {t.result.summary.aiSummaryBox}
                      </h3>
                      <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                        {result.summary.summary}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Critical Issues */}
                {result.summary.critical_issues && result.summary.critical_issues.length > 0 && (
                  <div className="mt-6 p-4 bg-red-50 border-l-4 border-red-500 rounded">
                    <h4 className="font-bold text-red-800 mb-2">⚠️ {t.result.summary.critical}</h4>
                    <ul className="list-disc list-inside text-red-700 space-y-1">
                      {result.summary.critical_issues.map((issue: string, idx: number) => (
                        <li key={idx}>{issue}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Patient Questions & Answers - UPDATED with structured output */}
            {result.patient_qa && result.patient_qa.answer && result.patient_qa.answer.trim() !== '' && result.patient_qa.answer !== 'ไม่มีคำถามเพิ่มเติม' && (
              <div className={`mb-8 bg-white rounded-xl shadow-lg p-8 border-2 ${result.patient_qa.should_contact_doctor ? 'border-red-300' : 'border-green-200'
                }`}>
                <div className="flex items-start">
                  <MessageCircle className={`w-6 h-6 mr-3 mt-1 ${result.patient_qa.should_contact_doctor ? 'text-red-600' : 'text-green-600'
                    }`} />
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-xl font-bold text-gray-800">
                        {t.result.qa.title}
                      </h3>
                    </div>

                    {/* Answer */}
                    <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed mb-4">
                      {result.patient_qa.answer}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        {/* Patient Data Preview */}
        {patientData && (
          <div className="mb-8 bg-white rounded-lg shadow-md overflow-hidden">
            <button
              onClick={() => setShowDataPreview(!showDataPreview)}
              className="w-full flex items-center justify-between p-6 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center">
                <FileText className="w-5 h-5 text-cu-pink-600 mr-3" />
                <h3 className="text-lg font-bold text-gray-800">
                  {t.result.dataPreview.title} ({t.result.dataPreview.count.replace('{count}', String(Object.keys(patientData).filter(k => patientData![k as keyof PatientFormData]).length))})
                </h3>
              </div>
              {showDataPreview ? (
                <ChevronUp className="w-5 h-5 text-gray-600" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-600" />
              )}
            </button>

            {showDataPreview && (
              <div className="border-t border-gray-200 p-6">
                <div className="grid md:grid-cols-2 gap-x-8 gap-y-4">
                  {Object.entries(patientData)
                    .filter(([key, value]) => !shouldSkipField(key, value))
                    .sort(([keyA], [keyB]) => {
                      const order = [
                        // Basic Info
                        'first_name', 'last_name', 'email', 'phone', 'birth_year',
                        'age', 'gender', 'hn',
                        'procedures', 'lefort_sub_options', 'bssro_sub_options',
                        'surgical_tooth_numbers', 'extraction_tooth_numbers', 'biopsy_sub_options',

                        // Procedure Details (ข้อ 10)
                        'imf_wire', 'imf_elastic', 'imf_loops',
                        'special_icbg', 'special_icbg_description',
                        'special_ng_tube', 'special_ng_tube_description',

                        // Dates & Note
                        'surgery_date', 'discharge_date', 'note',

                        // Symptoms
                        'pain_score', 'pain_description',
                        'pain_medication_effect',
                        'swelling_status', 'swelling_description',
                        'breathing_or_swallowing_difficulty', 'breathing_description',
                        'bleeding_status', 'bleeding_description',
                        'fever_status', 'fever_description',
                        'numbness_status', 'numbness_description',
                        'phlebitis', 'phlebitis_description',
                        'suture_status', 'suture_description',
                        'other_symptoms', 'other_symptoms_custom',
                        'antibiotic_compliance', 'antibiotic_description',
                        'compress_type',
                        'imf_wire_status', 'imf_wire_description',
                        'walking_status', 'walking_description',

                        // Daily Life
                        'brushing_teeth', 'brushing_description',
                        'mouth_rinsing', 'rinsing_description',
                        'food_types', 'food_types_custom', 'food_amount', 'food_amount_description',
                        'additional_questions',
                        'ng_tube_position', 'ng_tube_description'
                      ];

                      const indexA = order.indexOf(keyA);
                      const indexB = order.indexOf(keyB);

                      if (indexA === -1 && indexB === -1) return 0;
                      if (indexA === -1) return 1;
                      if (indexB === -1) return -1;
                      return indexA - indexB;
                    })
                    .map(([key, value]) => (
                      <div key={key} className="flex flex-col border-b border-gray-100 pb-2 last:border-0 hover:bg-white transition-colors p-2 rounded">
                        <span className="text-sm font-semibold text-gray-500 mb-1">
                          {dynamicLabels[key] || key}
                        </span>
                        <span className="text-gray-800 font-medium break-words">
                          {formatFieldValue(key, value, t, language)}
                        </span>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Risk Assessment Results */}
        {!isProcessing && result && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">
              {t.result.title}
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              {result.flows && Object.entries(result.flows).map(([flowName, flowResult]: [string, any]) => (
                <RiskResult
                  key={flowName}
                  flowName={flowName}
                  result={flowResult}
                  language={(patientData as any)?._language || 'th'}
                />
              ))}
            </div>
          </div>
        )}

        {/* Actions - Only show if not processing and has patientData */}
        {!isProcessing && patientData && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold text-gray-800 mb-4">
              {t.result.actions.nextSteps}
            </h3>
            <div className="space-y-3">
              {overallRisk.color === 'red' && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-red-800 font-medium mb-2">⚠️ {t.result.actions.contactDoctor}</p>
                  <p className="text-red-700 text-sm">
                    {t.result.actions.contactDoctorDesc}
                  </p>
                </div>
              )}
              {overallRisk.color === 'yellow' && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <p className="text-yellow-800 font-medium mb-2">⚠️ {t.result.actions.monitor}</p>
                  <p className="text-yellow-700 text-sm">
                    {t.result.actions.monitorDesc}
                  </p>
                </div>
              )}
              {overallRisk.color === 'green' && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-green-800 font-medium mb-2">✓ {t.result.actions.normal}</p>
                  <p className="text-green-700 text-sm">
                    {t.result.actions.normalDesc}
                  </p>
                </div>
              )}

              <div className="flex gap-4 pt-4">
                <Link
                  href="/form"
                  className="flex-1 flex items-center justify-center px-6 py-3 bg-cu-pink-600 text-white rounded-lg hover:bg-cu-pink-700 transition-colors"
                >
                  {t.result.actions.assessAgain}
                </Link>
                <button
                  onClick={() => {
                    if (navigator.share && patientData) {
                      navigator.share({
                        title: t.result.title,
                        text: `${t.result.title}: ${overallRisk.level}`,
                      });
                    }
                  }}
                  className="flex items-center px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  <Share2 className="w-4 h-4 mr-2" />
                  {t.result.actions.share}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Disclaimer */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>{t.result.disclaimer.split(':')[0]}:</strong>{t.result.disclaimer.split(':')[1]}
          </p>
        </div>
      </div>
    </div>
  );
}