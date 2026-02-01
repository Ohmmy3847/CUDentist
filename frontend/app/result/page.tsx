'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Download, Share2, CheckCircle, AlertTriangle, XCircle, ChevronDown, ChevronUp, FileText, MessageCircle } from 'lucide-react';
import type { ThreeLayerResult, PatientFormData } from '@/lib';
import RiskResult from '@/components/RiskResult';

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

        // Save log with AI results (only if not already saved)
        console.log('🔵 [SAVE CHECK] alreadySavedFlag:', alreadySavedFlag);
        if (alreadySavedFlag !== 'true') {
          try {
            console.log('📤 [API CALL] Calling assessPatient API to save results...');
            // Results are automatically saved through the assessPatient call
            console.log('✅ [SUCCESS] Successfully saved results with assessment');
          } catch (logError) {
            console.error('❌ [ERROR] Failed to save results:', logError);
            // Continue anyway - don't block showing results
          }
        } else {
          console.log('⏭️ [SKIP] Skipped save because already saved');
        }

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
      const lowRisk = riskLevels.filter(r => r.includes('ต่ำ')).length;

      if (overall_risk.includes('สูง') || highRisk > 0) {
        return { level: 'ความเสี่ยงสูง', count: highRisk, color: 'red' };
      } else if (overall_risk.includes('กลาง') || overall_risk.includes('ปานกลาง') || mediumRisk > 0) {
        return { level: 'ความเสี่ยงกลาง', count: mediumRisk, color: 'yellow' };
      }
      return { level: 'ความเสี่ยงต่ำ', count: lowRisk, color: 'green' };
    }

    // Fallback: calculate from individual flows
    const riskLevels = Object.values(result.flows).map((r: any) => r.risk_level);
    const highRisk = riskLevels.filter(r => r.includes('สูง')).length;
    const mediumRisk = riskLevels.filter(r => r.includes('กลาง') || r.includes('ปานกลาง')).length;
    const lowRisk = riskLevels.filter(r => r.includes('ต่ำ')).length;

    if (highRisk > 0) {
      return { level: 'ความเสี่ยงสูง', count: highRisk, color: 'red' };
    } else if (mediumRisk > 0) {
      return { level: 'ความเสี่ยงกลาง', count: mediumRisk, color: 'yellow' };
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

  const getFieldLabel = (key: string): string => {
    const labels: Record<string, string> = {
      // ข้อมูลพื้นฐาน
      age: '1. อายุ',
      gender: '2. เพศ',
      hn: '3. HN (กรอกเลขคนไข้)',
      procedures: '4. หัตถการที่ทำ (เลือกได้มากกว่า 1 หัตถการ)',
      lefort_sub_options: '4.1 รายละเอียด Lefort I',
      bssro_sub_options: '4.2 รายละเอียด BSSRO',
      
      // หัตถการย่อย
      has_imf: '5. หัตถการย่อย - IMF',
      imf_type: '5.1 ประเภทการมัดฟัน',
      imf_loops: '5.2 จำนวน loop',
      special_icbg: '5. หัตถการย่อย - ICBG',
      special_icbg_description: '5.1 รายละเอียด ICBG',
      special_ng_tube: '5. หัตถการย่อย - NG tube',
      special_ng_tube_description: '5.1 รายละเอียด NG tube',
      
      surgery_date: '6. ได้รับการผ่าตัดเมื่อวันที่',
      note: 'หมายเหตุพิเศษ (สำหรับหมอและพยาบาล)',
      
      // อาการ
      pain_score: '7. ระดับความปวด ณ ปัจจุบัน (Pain score)',
      pain_medication_effective: '8. ทานยาแก้ปวดแล้วดีขึ้นหรือไม่?',
      swelling_status: '9. อาการบวม',
      swelling_description: 'คำอธิบายอาการบวม',
      breathing_or_swallowing_difficulty: '10. มีอาการหายใจลำบาก หรือ กลืนลำบากหรือไม่?',
      breathing_description: 'คำอธิบายการหายใจ/กลืน',
      bleeding_status: '11. อาการเลือดซึม หรือ เลือดออก จากแผลในช่องปาก หรือ บริเวณจมูก',
      bleeding_description: 'คำอธิบายอาการเลือดออก',
      fever_status: '12. อาการไข้',
      fever_description: 'คำอธิบายอาการไข้',
      numbness_status: '13. อาการชา (บันทึกบริเวณที่ชาที่ช่องอื่นๆ)',
      numbness_description: 'บริเวณที่ชา/คำอธิบาย',
      phlebitis: '14. บริเวณที่เอาเข็มน้ำเกลือออกที่หลังมือหรือข้อมือ',
      phlebitis_description: 'คำอธิบายบริเวณเข็มน้ำเกลือ',
      suture_status: '15. ไหมเย็บแผล',
      suture_description: 'คำอธิบายไหมเย็บแผล',
      other_symptoms: '16. อาการอื่นๆ (เลือกได้หลายคำตอบ)',
      other_symptoms_custom: '16. อาการอื่นๆ ที่ระบุเพิ่มเติม',
      antibiotic_compliance: '17. รับประทานยาฆ่าเชื้อครบตามแผนการรักษาหรือไม่?',
      antibiotic_description: 'จำนวนครั้งที่ลืมทานยาฆ่าเชื้อ',
      compress_type: '18. ประคบเย็น หรือ อุ่นอยู่หรือไม่?',
      
      // IMF related (ถ้ามีการมัดฟัน)
      imf_wire_status: '19. หากมีการมัดฟันบนและล่างเข้าด้วยกัน ลวด/ยางมัดฟันแน่นดีหรือไม่?',
      imf_wire_description: 'คำอธิบายลวด/ยางมัดฟัน',
      
      // ICBG related (ถ้ามีการปลูกกระดูก)
      walking_status: '20. การเดิน ในผู้ป่วยที่ได้รับการรักษาการแหว่งของสันเหงือกโดยการนำกระดูกสะโพกมาปลูก',
      walking_description: 'คำอธิบายการเดิน',
      
      // การใช้ชีวิตประจำวัน
      brushing_teeth: '21. การแปรงฟัน',
      brushing_description: 'คำอธิบายการแปรงฟัน',
      mouth_rinsing: '22. การบ้วนปาก',
      rinsing_description: 'คำอธิบายการบ้วนปาก',
      feeding_method: '23. วิธีการรับประทานอาหาร',
      feeding_description: 'คำอธิบายวิธีการรับประทานอาหาร',
      food_types: '24. ประเภทอาหาร (เลือกได้หลายคำตอบ)',
      food_amount: '25. ปริมาณอาหาร',
      food_amount_description: 'คำอธิบายปริมาณอาหาร',
      additional_questions: '26. คำถามเพิ่มเติม',
      
      // NG tube related (ถ้ามี NG tube)
      ng_tube_position: '27. ตำแหน่งสายยางให้อาหาร',
      ng_tube_description: 'คำอธิบายตำแหน่งสายยาง',
    };
    return labels[key] || key;
  };

  // Loading state - show patient data while processing
  if (isProcessing || !result) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50 py-8">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="mb-8">
            <Link href="/" className="flex items-center text-gray-600 hover:text-gray-800 mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              กลับหน้าหลัก
            </Link>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              กำลังประเมินความเสี่ยง
            </h1>
            {patientData?.hn && (
              <p className="text-gray-600">
                HN: {patientData.hn} | วันที่ประเมิน: {new Date().toLocaleDateString('th-TH')}
              </p>
            )}
          </div>

          {/* Processing Status */}
          <div className="mb-8 bg-white rounded-xl shadow-lg p-8">
            <div className="flex items-center mb-6">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cu-pink-600 mr-4"></div>
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

          {/* Show patient data while waiting */}
          {patientData && (
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="p-6 bg-pink-50 border-b border-pink-100">
                <div className="flex items-center">
                  <FileText className="w-5 h-5 text-cu-pink-600 mr-3" />
                  <h3 className="text-lg font-bold text-gray-800">
                    ข้อมูลที่กรอก ({Object.keys(patientData).filter(k => patientData[k as keyof PatientFormData]).length} ข้อ)
                  </h3>
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  ข้อมูลเหล่านี้จะถูกนำไปใช้ในการประเมินความเสี่ยง
                </p>
              </div>

              <div className="p-6">
                <div className="grid md:grid-cols-2 gap-x-8 gap-y-4">
                  {Object.entries(patientData)
                    .filter(([, value]) => value !== undefined && value !== null && value !== '')
                    .sort(([keyA], [keyB]) => {
                      const order = [
                        'age', 'gender', 'hn', 
                        'procedures', 'lefort_sub_options', 'bssro_sub_options',
                        'has_imf', 'imf_type', 'imf_loops',
                        'special_icbg', 'special_icbg_description',
                        'special_ng_tube', 'special_ng_tube_description',
                        'surgery_date', 'note',
                        'pain_score', 'pain_medication_effective',
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
                        'brushing_teeth', 'brushing_description',
                        'mouth_rinsing', 'rinsing_description',
                        'feeding_method', 'feeding_description',
                        'food_types', 'food_amount', 'food_amount_description',
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
                      <div key={key} className="flex flex-col">
                        <span className="text-sm font-medium text-gray-600 mb-1">
                          {getFieldLabel(key)}
                        </span>
                        <span className="text-gray-800">
                          {formatFieldValue(key, value)}
                        </span>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}

          {/* Error display */}
          {error && (
            <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
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
        </div>
      </div>
    );
  }

  const overallRisk = getOverallRisk();

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
                <p className="text-gray-700">
                  ตรวจพบความเสี่ยงใน {overallRisk.count} ด้าน จากทั้งหมด {result.flows ? Object.keys(result.flows).length : 0} ด้านที่ประเมินได้
                </p>
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
                  ข้อมูลที่กรอก ({Object.keys(patientData).filter(k => patientData[k as keyof PatientFormData]).length} ข้อ)
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
                    .filter(([, value]) => value !== undefined && value !== null && value !== '')
                    .sort(([keyA], [keyB]) => {
                      // กำหนดลำดับการแสดงผล
                      const order = [
                        'age', 'gender', 'hn', 
                        'procedures', 'lefort_sub_options', 'bssro_sub_options',
                        'has_imf', 'imf_type', 'imf_loops',
                        'special_icbg', 'special_icbg_description',
                        'special_ng_tube', 'special_ng_tube_description',
                        'surgery_date', 'note',
                        'pain_score', 'pain_medication_effective',
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
                        'brushing_teeth', 'brushing_description',
                        'mouth_rinsing', 'rinsing_description',
                        'feeding_method', 'feeding_description',
                        'food_types', 'food_amount', 'food_amount_description',
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
                      <div key={key} className="flex flex-col">
                        <span className="text-sm font-medium text-gray-600 mb-1">
                          {getFieldLabel(key)}
                        </span>
                        <span className="text-gray-800">
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
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            รายละเอียดการประเมินแต่ละด้าน
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            {Object.entries(result.flows).map(([flowName, flowResult]: [string, any]) => (
              <RiskResult
                key={flowName}
                flowName={flowName}
                result={flowResult}
              />
            ))}
          </div>
        </div>

        {/* Actions */}
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