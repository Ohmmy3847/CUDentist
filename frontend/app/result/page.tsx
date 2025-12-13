'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Download, Share2, CheckCircle, AlertTriangle, XCircle, ChevronDown, ChevronUp, FileText } from 'lucide-react';
import type { AllFlowsResult, PatientFormData } from '@/lib/types';
import RiskResult from '@/components/RiskResult';

export default function ResultPage() {
  const router = useRouter();
  const [result, setResult] = useState<AllFlowsResult | null>(null);
  const [patientData, setPatientData] = useState<PatientFormData | null>(null);
  const [showDataPreview, setShowDataPreview] = useState(false);

  useEffect(() => {
    // Load result from sessionStorage
    const storedResult = sessionStorage.getItem('riskAssessmentResult');
    const storedPatient = sessionStorage.getItem('patientData');

    if (storedResult) {
      setResult(JSON.parse(storedResult));
    }
    if (storedPatient) {
      setPatientData(JSON.parse(storedPatient));
    }

    // If no result, redirect to home
    if (!storedResult) {
      router.push('/');
    }
  }, [router]);

  const getOverallRisk = () => {
    if (!result) return { level: 'ไม่ทราบ', count: 0, color: 'gray' };

    const riskLevels = Object.values(result).map(r => r.risk_level);
    const highRisk = riskLevels.filter(r => r.includes('สูง')).length;
    const mediumRisk = riskLevels.filter(r => r.includes('กลาง')).length;
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

  const formatFieldValue = (key: string, value: any): string => {
    if (value === undefined || value === null || value === '') return 'ไม่ได้ระบุ';
    if (Array.isArray(value)) {
      return value.length > 0 ? value.join(', ') : 'ไม่ได้ระบุ';
    }
    return String(value);
  };

  const getFieldLabel = (key: string): string => {
    const labels: Record<string, string> = {
      age: 'อายุ',
      gender: 'เพศ',
      hn: 'HN',
      procedures: 'หัตถการที่ทำ',
      surgery_date: 'วันที่ผ่าตัด',
      pain_score: 'ระดับความปวด',
      pain_medication_effective: 'ยาแก้ปวดมีผล',
      swelling_status: 'อาการบวม',
      swelling_description: 'คำอธิบายอาการบวม',
      breathing_or_swallowing_difficulty: 'หายใจ/กลืนลำบาก',
      breathing_description: 'คำอธิบายการหายใจ/กลืน',
      bleeding_status: 'อาการเลือดออก',
      bleeding_description: 'คำอธิบายอาการเลือดออก',
      fever_status: 'อาการไข้',
      fever_description: 'คำอธิบายอาการไข้',
      numbness_status: 'อาการชา',
      numbness_description: 'คำอธิบายอาการชา',
      phlebitis: 'บริเวณเข็มน้ำเกลือ',
      phlebitis_description: 'คำอธิบายบริเวณเข็มน้ำเกลือ',
      suture_status: 'ไหมเย็บแผล',
      suture_description: 'คำอธิบายไหมเย็บแผล',
      other_symptoms: 'อาการอื่นๆ',
      antibiotic_compliance: 'การทานยาฆ่าเชื้อ',
      antibiotic_description: 'จำนวนครั้งที่ลืมทาน',
      compress_type: 'ประคบ',
      has_imf: 'การมัดฟัน (IMF)',
      imf_wire_status: 'ลวด/ยางมัดฟัน',
      imf_wire_description: 'คำอธิบายลวด/ยางมัดฟัน',
      walking_status: 'การเดิน',
      walking_description: 'คำอธิบายการเดิน',
      brushing_teeth: 'การแปรงฟัน',
      brushing_description: 'คำอธิบายการแปรงฟัน',
      mouth_rinsing: 'การบ้วนปาก',
      rinsing_description: 'คำอธิบายการบ้วนปาก',
      feeding_method: 'วิธีการรับประทานอาหาร',
      feeding_description: 'คำอธิบายวิธีการรับประทานอาหาร',
      food_types: 'ประเภทอาหาร',
      food_amount: 'ปริมาณอาหาร',
      food_amount_description: 'คำอธิบายปริมาณอาหาร',
      additional_questions: 'คำถามเพิ่มเติม',
      ng_tube_position: 'ตำแหน่งสายยาง',
      ng_tube_description: 'คำอธิบายตำแหน่งสายยาง',
    };
    return labels[key] || key;
  };

  if (!result) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const overallRisk = getOverallRisk();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 py-8">
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
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              ดาวน์โหลดรายงาน
            </button>
          </div>
        </div>

        {/* Overall Summary */}
        <div className={`mb-8 rounded-xl shadow-lg p-8 ${
          overallRisk.color === 'red' ? 'bg-red-100 border-2 border-red-300' :
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
                  ตรวจพบความเสี่ยงใน {overallRisk.count} ด้าน จากทั้งหมด {Object.keys(result).length} ด้าน
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Patient Data Preview */}
        {patientData && (
          <div className="mb-8 bg-white rounded-lg shadow-md overflow-hidden">
            <button
              onClick={() => setShowDataPreview(!showDataPreview)}
              className="w-full flex items-center justify-between p-6 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center">
                <FileText className="w-5 h-5 text-blue-600 mr-3" />
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
                    .filter(([_, value]) => value !== undefined && value !== null && value !== '')
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
            {Object.entries(result).map(([flowName, flowResult]) => (
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
                className="flex-1 flex items-center justify-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
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
