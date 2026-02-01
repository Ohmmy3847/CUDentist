'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Download, Share2, CheckCircle, AlertTriangle, XCircle, ChevronDown, ChevronUp, FileText, MessageCircle, Loader2 } from 'lucide-react';
import type { ThreeLayerResult, PatientFormData } from '@/lib';
import RiskResult from '@/components/RiskResult';

// Helper functions (outside component for better performance)
const formatFieldValue = (key: string, value: unknown): React.ReactNode => {
  if (value === undefined || value === null || value === '') return 'ไม่ได้ระบุ';

  // จัดการ boolean
  if (typeof value === 'boolean') {
    return value ? 'ใช่' : 'ไม่';
  }

  // จัดการ array - แสดงเป็นบรรทัดใหม่
  if (Array.isArray(value)) {
    if (value.length === 0) return 'ไม่ได้ระบุ';
    return (
      <div className="space-y-1">
        {value.map((item, index) => (
          <div key={index}>• {item}</div>
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

  return String(value);
};

const getDynamicLabels = (data: PatientFormData | null): Record<string, string> => {
  const baseLabels: Record<string, string> = {
    // ข้อมูลพื้นฐาน
    first_name: '1. ชื่อจริง',
    last_name: '2. นามสกุล',
    email: '3. อีเมล',
    phone: '4. เบอร์โทรศัพท์',
    birth_year: '5. ปีเกิด (พ.ศ.)',
    age: '6. อายุ',
    gender: '7. เพศ',
    hn: '8. HN (หมายเลขผู้ป่วย)',
    procedures: '9. หัตถการที่ทำ',

    // รายละเอียดหัตถการ (Sub-options)
    lefort_sub_options: '9.1 รายละเอียด Lefort I',
    bssro_sub_options: '9.2 รายละเอียด BSSRO',
    surgical_tooth_numbers: '9.3 หมายเลขซี่ฟันสำหรับผ่าตัด',
    extraction_tooth_numbers: '9.4 หมายเลขซี่ฟันสำหรับถอนฟัน',
    biopsy_sub_options: '9.5 รายละเอียด Biopsy',

    // หัตถการอื่นๆ (ข้อ 10)
    imf_wire: '10.1 IMF มัดลวด',
    imf_elastic: '10.2 IMF มัดยาง',
    imf_loops: 'จำนวน Loop',
    special_icbg: '10.3 ICBG (ปลูกกระดูก)',
    special_icbg_description: 'รายละเอียด ICBG',
    special_ng_tube: '10.4 NG tube (สายยางให้อาหาร)',
    special_ng_tube_description: 'รายละเอียด NG tube',

    // วันที่และหมายเหตุ
    surgery_date: '11. ได้รับการผ่าตัดเมื่อวันที่',
    discharge_date: '12. วันที่ Discharge (กลับบ้าน)',
    note: '13. หมายเหตุพิเศษ',
  };

  if (!data) return baseLabels;

  // Dynamic numbering logic based on SymptomsForm & DailyLifeForm logic
  let qNum = 13;
  const addLabel = (key: string, label: string, isSub: boolean = false) => {
    if (!isSub) qNum++;
    baseLabels[key] = isSub ? `${qNum}.1 ${label}` : `${qNum}. ${label}`;
  };

  // --- Symptoms Form ---
  addLabel('pain_score', 'ระดับความปวด (0-10)');
  baseLabels['pain_description'] = `${qNum}.1 คำอธิบายความปวด`;
  baseLabels['pain_score_description'] = `${qNum}.1 คำอธิบายความปวด`;

  if ((data.pain_score || 0) > 0) {
    addLabel('pain_medication_effect', 'ทานยาแก้ปวดแล้วดีขึ้นหรือไม่');
    baseLabels['pain_medication_effective'] = baseLabels['pain_medication_effect'];
  }

  addLabel('swelling_status', 'อาการบวม');
  baseLabels['swelling_description'] = `${qNum}.1 คำอธิบายอาการบวม`;

  addLabel('breathing_or_swallowing_difficulty', 'หายใจ/กลืนลำบาก');
  baseLabels['breathing_description'] = `${qNum}.1 คำอธิบายการหายใจ`;

  addLabel('bleeding_status', 'เลือดออก');
  baseLabels['bleeding_description'] = `${qNum}.1 คำอธิบายเลือดออก`;

  addLabel('fever_status', 'อาการไข้');
  baseLabels['fever_description'] = `${qNum}.1 คำอธิบายไข้`;

  addLabel('numbness_status', 'อาการชา');
  baseLabels['numbness_description'] = `${qNum}.1 บริเวณที่ชา`;

  addLabel('phlebitis', 'บริเวณเข็มน้ำเกลือ');
  baseLabels['phlebitis_description'] = `${qNum}.1 คำอธิบายเข็มน้ำเกลือ`;

  addLabel('suture_status', 'ไหมเย็บแผล');
  baseLabels['suture_description'] = `${qNum}.1 คำอธิบายไหมเย็บแผล`;

  addLabel('other_symptoms', 'อาการอื่นๆ');
  baseLabels['other_symptoms_custom'] = `${qNum}.1 อาการอื่นๆ เพิ่มเติม`;

  addLabel('antibiotic_compliance', 'การทานยาฆ่าเชื้อ');
  baseLabels['antibiotic_description'] = `${qNum}.1 จำนวนครั้งที่ลืมทานยา`;

  addLabel('compress_type', 'การประคบ (เย็น/อุ่น)');

  // IMF Wire/Elastic check
  // Note: This logic aims to match SymptomsForm
  if (data.has_imf === 'มีการมัดฟัน' || data.imf_wire || data.imf_elastic) {
    addLabel('imf_wire_status', 'สถานะลวด/ยางมัดฟัน');
    baseLabels['imf_wire_description'] = `${qNum}.1 คำอธิบายลวดมัดฟัน`;
  }

  // ICBG check
  if (data.special_icbg === 'มี') {
    addLabel('walking_status', 'การเดิน (ICBG)');
    baseLabels['walking_description'] = `${qNum}.1 คำอธิบายการเดิน`;
  }

  // --- Daily Life Form ---
  addLabel('brushing_teeth', 'การแปรงฟัน');
  baseLabels['brushing_description'] = `${qNum}.1 คำอธิบายการแปรงฟัน`;

  addLabel('mouth_rinsing', 'การบ้วนปาก');
  baseLabels['rinsing_description'] = `${qNum}.1 คำอธิบายการบ้วนปาก`;

  addLabel('food_types', 'ประเภทอาหาร');
  baseLabels['food_types_custom'] = `${qNum}.1 อาหารอื่นๆ`;

  addLabel('food_amount', 'ปริมาณอาหาร');
  baseLabels['food_amount_description'] = `${qNum}.1 คำอธิบายปริมาณอาหาร`;

  addLabel('additional_questions', 'คำถามเพิ่มเติม');

  // NG Tube check
  if (data.special_ng_tube === 'มี') {
    addLabel('ng_tube_position', 'ตำแหน่งสายยางให้อาหาร');
    baseLabels['ng_tube_description'] = `${qNum}.1 คำอธิบายสายยาง`;
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
        const classificationResult = await api.assessPatient(
          patientFormData,
          (current: number, total: number, flowName: string) => {
            setProcessingProgress({ current, total, flowName });
          }
        );

        // Store result and update state
        sessionStorage.setItem('riskAssessmentResult', JSON.stringify(classificationResult));
        sessionStorage.removeItem('isCurrentlyProcessing'); // Clear processing flag when done
        setResult(classificationResult as unknown as ThreeLayerResult);
        setIsProcessing(false);
      } catch (err) {
        sessionStorage.removeItem('isCurrentlyProcessing'); // Clear processing flag on error
        setError(err instanceof Error ? err.message : 'เกิดข้อผิดพลาดในการประเมินความเสี่ยง');
        console.error('Classification error:', err);
        setIsProcessing(false);
      }
    };

    performClassification();
  }, [router]);

  const getOverallRisk = () => {
    if (!result || !result.flows) return { level: 'ไม่ทราบ', count: 0, color: 'gray' };

    // Use summary if available (from LLM)
    if (result.summary) {
      const { overall_risk } = result.summary;

      // Count from flows directly
      const riskLevels = Object.values(result.flows).map((r: any) => r.risk_level);
      const highRisk = riskLevels.filter(r => r.includes('สูง')).length;
      const mediumRisk = riskLevels.filter(r => r.includes('กลาง') || r.includes('ปานกลาง')).length;
      const complicatedRisk = riskLevels.filter(r => r.includes('ซับซ้อน') || r.includes('ไม่สามารถสรุป')).length;
      const lowRisk = riskLevels.filter(r => r.includes('ต่ำ')).length;

      // ลำดับความสำคัญ: HIGH > MEDIUM > COMPLICATED > LOW
      if (overall_risk.includes('สูง') || highRisk > 0) {
        return { level: 'ความเสี่ยงสูง', count: highRisk, color: 'red' };
      } else if (overall_risk.includes('กลาง') || overall_risk.includes('ปานกลาง') || mediumRisk > 0) {
        return { level: 'ความเสี่ยงกลาง', count: mediumRisk, color: 'yellow' };
      } else if (overall_risk.includes('ซับซ้อน') || overall_risk.includes('ไม่สามารถสรุป') || complicatedRisk > 0) {
        return { level: 'ไม่สามารถสรุปผลความเสี่ยงได้เนื่องจากอาการมีความซับซ้อน', count: complicatedRisk, color: 'orange' };
      }
      return { level: 'ความเสี่ยงต่ำ', count: lowRisk, color: 'green' };
    }

    // Fallback: calculate from individual flows
    const riskLevels = Object.values(result.flows).map((r: any) => r.risk_level);
    const highRisk = riskLevels.filter(r => r.includes('สูง')).length;
    const mediumRisk = riskLevels.filter(r => r.includes('กลาง') || r.includes('ปานกลาง')).length;
    const complicatedRisk = riskLevels.filter(r => r.includes('ซับซ้อน') || r.includes('ไม่สามารถสรุป')).length;
    const lowRisk = riskLevels.filter(r => r.includes('ต่ำ')).length;

    // ลำดับความสำคัญ: HIGH > MEDIUM > COMPLICATED > LOW
    if (highRisk > 0) {
      return { level: 'ความเสี่ยงสูง', count: highRisk, color: 'red' };
    } else if (mediumRisk > 0) {
      return { level: 'ความเสี่ยงกลาง', count: mediumRisk, color: 'yellow' };
    } else if (complicatedRisk > 0) {
      return { level: 'ไม่สามารถสรุปผลความเสี่ยงได้เนื่องจากอาการมีความซับซ้อน', count: complicatedRisk, color: 'orange' };
    }
    return { level: 'ความเสี่ยงต่ำ', count: lowRisk, color: 'green' };
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
  const dynamicLabels = getDynamicLabels(patientData);

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <Link href="/" className="flex items-center text-gray-600 hover:text-gray-800 mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            กลับหน้าหลัก
          </Link>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 mb-2">
                ผลการประเมินความเสี่ยง
              </h1>
              {patientData?.hn && (
                <p className="text-gray-600">
                  HN: {patientData.hn} | วันที่ประเมิน: {new Date().toLocaleDateString('th-TH')}
                </p>
              )}
            </div>
            <button
              onClick={handleDownloadReport}
              className="flex items-center px-4 py-2 bg-cu-pink-600 text-white rounded-lg hover:bg-cu-pink-700 transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              ดาวน์โหลดรายงาน
            </button>
          </div>
        </div>

        {/* Loading State */}
        {isProcessing && (
          <div className="mb-8 bg-white rounded-xl shadow-lg p-8">
            <div className="flex items-center mb-6">
              <Loader2 className="animate-spin h-8 w-8 text-cu-pink-600 mr-4" />
              <div className="flex-1">
                <h2 className="text-xl font-bold text-gray-800">กำลังประมวลผลข้อมูล...</h2>
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
              ระบบกำลังวิเคราะห์ข้อมูลด้วย AI อาจใช้เวลา 10-30 วินาที
            </p>
          </div>
        )}

        {/* Error display */}
        {error && (
          <div className="mb-8 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 font-medium">เกิดข้อผิดพลาด</p>
            <p className="text-red-700 text-sm mt-1">{error}</p>
            <button
              onClick={() => router.push('/form')}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              กลับไปแก้ไขฟอร์ม
            </button>
          </div>
        )}

        {/* Result Content */}
        {!isProcessing && result && (
          <>
            {/* Overall Summary */}
            <div className={`mb-8 rounded-xl shadow-lg p-8 ${overallRisk.color === 'red' ? 'bg-red-100 border-2 border-red-300' :
              overallRisk.color === 'yellow' ? 'bg-yellow-100 border-2 border-yellow-300' :
                'bg-green-100 border-2 border-green-300'
              }`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  {overallRisk.color === 'red' ? (
                    <XCircle className="w-16 h-16 text-red-600 mr-4" />
                  ) : overallRisk.color === 'yellow' ? (
                    <AlertTriangle className="w-16 h-16 text-yellow-600 mr-4" />
                  ) : (
                    <CheckCircle className="w-16 h-16 text-green-600 mr-4" />
                  )}
                  <div>
                    <h2 className="text-2xl font-bold text-gray-800 mb-1">
                      สรุปผลการประเมิน: {overallRisk.level}
                    </h2>

                    {result.flows && Object.keys(result.flows).length < 17 && (
                      <p className="text-sm text-orange-600 mt-1">
                        ⚠️ หมายเหตุ: ระบบประเมินได้เพียง {Object.keys(result.flows).length} ด้าน จาก 17 ด้านทั้งหมด
                      </p>
                    )}
                    <p className="text-sm text-green-600 mt-2 flex items-center">
                      <CheckCircle className="w-4 h-4 mr-1" />
                      บันทึกข้อมูลสำเร็จ - ผลการประเมินถูกบันทึกลงระบบแล้ว
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
                        สรุปผลการประเมิน
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
                    <h4 className="font-bold text-red-800 mb-2">⚠️ ปัญหาสำคัญที่ต้องดูแลเร่งด่วน:</h4>
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
                        คำตอบสำหรับคำถามของคุณ
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
                  ข้อมูลที่กรอก ({Object.keys(patientData).filter(k => patientData![k as keyof PatientFormData]).length} ข้อ)
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
                          {formatFieldValue(key, value)}
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
              รายละเอียดการประเมินแต่ละด้าน
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              {result.flows && Object.entries(result.flows).map(([flowName, flowResult]: [string, any]) => (
                <RiskResult
                  key={flowName}
                  flowName={flowName}
                  result={flowResult}
                />
              ))}
            </div>
          </div>
        )}

        {/* Actions - Only show if not processing and has patientData */}
        {!isProcessing && patientData && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold text-gray-800 mb-4">
              ขั้นตอนต่อไป
            </h3>
            <div className="space-y-3">
              {overallRisk.color === 'red' && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-red-800 font-medium mb-2">⚠️ แนะนำให้ติดต่อแพทย์ทันที</p>
                  <p className="text-red-700 text-sm">
                    พบความเสี่ยงสูงในบางด้าน กรุณาติดต่อแพทย์หรือพยาบาลเพื่อรับคำปรึกษาและการรักษาที่เหมาะสม
                  </p>
                </div>
              )}
              {overallRisk.color === 'yellow' && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <p className="text-yellow-800 font-medium mb-2">⚠️ ควรติดตามอาการอย่างใกล้ชิด</p>
                  <p className="text-yellow-700 text-sm">
                    พบความเสี่ยงปานกลาง แนะนำให้ติดตามอาการและปฏิบัติตามคำแนะนำที่ได้รับ หากอาการไม่ดีขึ้นควรพบแพทย์
                  </p>
                </div>
              )}
              {overallRisk.color === 'green' && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-green-800 font-medium mb-2">✓ อาการอยู่ในเกณฑ์ปกติ</p>
                  <p className="text-green-700 text-sm">
                    ความเสี่ยงอยู่ในระดับต่ำ แนะนำให้ดูแลตนเองตามคำแนะนำและติดตามอาการต่อไป
                  </p>
                </div>
              )}

              <div className="flex gap-4 pt-4">
                <Link
                  href="/form"
                  className="flex-1 flex items-center justify-center px-6 py-3 bg-cu-pink-600 text-white rounded-lg hover:bg-cu-pink-700 transition-colors"
                >
                  ประเมินใหม่อีกครั้ง
                </Link>
                <button
                  onClick={() => {
                    if (navigator.share && patientData) {
                      navigator.share({
                        title: 'ผลการประเมินความเสี่ยง',
                        text: `ผลการประเมินความเสี่ยง: ${overallRisk.level}`,
                      });
                    }
                  }}
                  className="flex items-center px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  <Share2 className="w-4 h-4 mr-2" />
                  แชร์ผล
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Disclaimer */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>หมายเหตุ:</strong> ผลการประเมินนี้เป็นเพียงข้อมูลเบื้องต้นเท่านั้น
            ไม่สามารถใช้แทนการวินิจฉัยหรือคำแนะนำจากแพทย์ผู้เชี่ยวชาญได้
            หากมีข้อสงสัยหรืออาการผิดปกติ กรุณาปรึกษาแพทย์
          </p>
        </div>
      </div>
    </div>
  );
}