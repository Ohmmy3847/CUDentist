import type { RiskAssessmentResult } from '@/lib';
import { getSymptomLabel } from '@/lib/symptomMappings';
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

interface RiskResultProps {
  flowName: string;
  result: RiskAssessmentResult;
  language?: string;
}

const getRiskColor = (riskLevel: string) => {
  if (riskLevel.includes('ต่ำ') || riskLevel.toLowerCase().includes('low')) {
    return {
      bg: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-800',
      icon: 'text-green-600',
      badge: 'bg-green-100 text-green-800',
    };
  } else if (riskLevel.includes('กลาง') || riskLevel.toLowerCase().includes('medium') || riskLevel.toLowerCase().includes('moderate')) {
    return {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      text: 'text-yellow-800',
      icon: 'text-yellow-600',
      badge: 'bg-yellow-100 text-yellow-800',
    };
  } else if (riskLevel.includes('สูง') || riskLevel.toLowerCase().includes('high')) {
    return {
      bg: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-800',
      icon: 'text-red-600',
      badge: 'bg-red-100 text-red-800',
    };
  } else if (riskLevel.includes('ซับซ้อน') || riskLevel.toLowerCase().includes('complex') || riskLevel.toLowerCase().includes('complicated')) {
    return {
      bg: 'bg-purple-50',
      border: 'border-purple-200',
      text: 'text-purple-800',
      icon: 'text-purple-600',
      badge: 'bg-purple-100 text-purple-800',
    };
  }
  return {
    bg: 'bg-gray-50',
    border: 'border-gray-200',
    text: 'text-gray-800',
    icon: 'text-gray-600',
    badge: 'bg-gray-100 text-gray-800',
  };
};

const getRiskIcon = (riskLevel: string) => {
  if (riskLevel.includes('ต่ำ') || riskLevel.toLowerCase().includes('low')) {
    return CheckCircle;
  } else if (riskLevel.includes('กลาง') || riskLevel.toLowerCase().includes('medium') || riskLevel.toLowerCase().includes('moderate')) {
    return AlertTriangle;
  } else if (riskLevel.includes('สูง') || riskLevel.toLowerCase().includes('high')) {
    return XCircle;
  }
  return AlertTriangle;
};

const getFlowDisplayName = (flowName: string, language: string): string => {
  const flowNamesTH: { [key: string]: string } = {
    pain: 'อาการปวด',
    swelling: 'อาการบวม',
    bleeding: 'เลือดออก',
    fever: 'ไข้',
    numbness: 'อาการชา',
    phlebitis: 'Phlebitis',
    suture: 'ไหมเย็บแผล',
    imf: 'การมัดฟัน',
    walking: 'การเดิน',
    ng_tube: 'สายยางให้อาหาร',
    brushing: 'การแปรงฟัน',
    rinsing: 'การบ้วนปาก',
    food_types: 'ประเภทอาหาร',
    food_amount: 'ปริมาณอาหาร',
    antibiotic: 'ยาฆ่าเชื้อ',
    compress: 'การประคบ'
  };

  const flowNamesEN: { [key: string]: string } = {
    pain: 'Pain',
    swelling: 'Swelling',
    bleeding: 'Bleeding',
    fever: 'Fever',
    numbness: 'Numbness',
    phlebitis: 'Phlebitis',
    suture: 'Suture',
    imf: 'IMF',
    walking: 'Walking (ICBG)',
    ng_tube: 'NG Tube',
    brushing: 'Brushing Teeth',
    rinsing: 'Mouth Rinsing',
    food_types: 'Food Types',
    food_amount: 'Food Amount',
    antibiotic: 'Antibiotics',
    compress: 'Compress'
  };

  // Try exact match first
  if (language === 'en' && flowNamesEN[flowName]) return flowNamesEN[flowName];
  if (flowNamesTH[flowName]) return language === 'en' ? flowName : flowNamesTH[flowName]; // Fallback to key if EN missing

  // Try to find key by Thai name (if flowName coming from backend is Thai key e.g. "อาการปวด")
  // Backend actually returns flow name as keys like "อาการปวด" (TH)
  // We should map Backend Keys (Thai) to English Display if language is EN.

  if (language === 'en') {
    // Create reverse map or direct map from Thai key to English Display
    const thToEn: { [key: string]: string } = {
      'อาการปวด': 'Pain',
      'อาการบวม': 'Swelling',
      'อาการเลือดซึม/ เลือดออก': 'Bleeding',
      'อาการเลือดออก': 'Bleeding',
      'อาการไข้': 'Fever',
      'ชา': 'Numbness',
      'อาการชา': 'Numbness',
      'บริเวณที่เอาเข็มน้ำเกลือออกที่หลังมือหรือข้อมือ (phlebitis)': 'Phlebitis',
      'ไหมเย็บแผล': 'Suture',
      'อาการอื่นๆ (เลือกได้หลายคำตอบ)': 'Other Symptoms',
      'รับประทานยาฆ่าเชื้อครบตามแผนการรักษาหรือไม่?': 'Antibiotics',
      'ประคบเย็น หรือ อุ่นอยู่หรือไม่?': 'Compress',
      'หากมีการมัดฟันบนและล่างเข้าด้วยกัน ลวดมัดฟันแน่นดีหรือไม่?': 'IMF',
      'การเดิน: การรักษาการแหว่งของสันเหงือกโดยการนำกระดูกสะโพกมาปลูก': 'Walking (ICBG)',
      'ตำแหน่งสายยางให้อาหาร: กรณีในผู้ป่วยที่รับประทานอาหารผ่านทางสายยาง (on NG-nasogastric tube)': 'NG Tube',
      'การแปรงฟัน': 'Brushing Teeth',
      'การบ้วนปาก': 'Mouth Rinsing',
      'ประเภทอาหารที่ทาน (สามารถเลือกได้หลายคำตอบ)': 'Food Types',
      'ปริมาณอาหารที่ทาน': 'Food Amount',
    };

    // Handle symptom keys (headache, bruising, etc.)
    // Try to get label from symptom mappings first
    const symptomLabel = getSymptomLabel(flowName, language as 'th' | 'en');
    if (symptomLabel !== flowName) {
      // Found in symptom mappings
      return symptomLabel;
    }

    // Handle custom symptom flows (starts with "อาการที่ผู้ป่วยระบุเพิ่มเติม:")
    if (flowName.startsWith('อาการที่ผู้ป่วยระบุเพิ่มเติม:')) {
      return 'Additional Symptoms Reported';
    }

    if (thToEn[flowName]) return thToEn[flowName];
  }

  return flowName;
};

const getRiskLevelDisplay = (riskLevel: string, language: string): string => {
  if (language !== 'en') return riskLevel;

  // Map Thai risk levels to English
  if (riskLevel.includes('ต่ำ')) return 'Low Risk';
  if (riskLevel.includes('กลาง') || riskLevel.includes('ปานกลาง')) return 'Moderate Risk';
  if (riskLevel.includes('สูง')) return 'High Risk';
  if (riskLevel.includes('ซับซ้อน')) return 'Complex';
  if (riskLevel.includes('ไม่เกี่ยวข้อง')) return 'N/A';
  if (riskLevel.includes('ไม่สามารถประเมินได้')) return 'Unknown';

  return riskLevel;
}

export default function RiskResult({ flowName, result, language = 'th' }: RiskResultProps) {
  const colors = getRiskColor(result.risk_level);
  const Icon = getRiskIcon(result.risk_level);
  const displayName = getFlowDisplayName(flowName, language);
  const displayRiskLevel = getRiskLevelDisplay(result.risk_level, language);

  return (
    <div className={`${colors.bg} ${colors.border} border-2 rounded-lg p-6 transition-all hover:shadow-lg`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center">
          <Icon className={`w-8 h-8 ${colors.icon} mr-3`} />
          <div>
            <h3 className="text-lg font-bold text-gray-800">
              {displayName}
            </h3>
            <span className={`inline-block mt-1 px-3 py-1 rounded-full text-sm font-medium ${colors.badge}`}>
              {displayRiskLevel}
            </span>
          </div>
        </div>
      </div>

      {/* Reason */}
      <div className="mb-4">
        <h4 className="font-semibold text-gray-700 mb-2 flex items-center">
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          {language === 'en' ? 'Reason' : 'เหตุผล'}
        </h4>
        <p className={`${colors.text} text-sm leading-relaxed pl-7`}>
          {result.reason}
        </p>
      </div>

      {/* Recommendation */}
      <div>
        <h4 className="font-semibold text-gray-700 mb-2 flex items-center">
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          {language === 'en' ? 'Recommendation' : 'คำแนะนำ'}
        </h4>
        <p className={`${colors.text} text-sm leading-relaxed pl-7`}>
          {result.recommendation}
        </p>
      </div>
    </div>
  );
}
