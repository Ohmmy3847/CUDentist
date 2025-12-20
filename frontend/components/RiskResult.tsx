import type { RiskAssessmentResult } from '@/lib';
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

interface RiskResultProps {
  flowName: string;
  result: RiskAssessmentResult;
}

const getRiskColor = (riskLevel: string) => {
  if (riskLevel.includes('ต่ำ')) {
    return {
      bg: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-800',
      icon: 'text-green-600',
      badge: 'bg-green-100 text-green-800',
    };
  } else if (riskLevel.includes('กลาง')) {
    return {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      text: 'text-yellow-800',
      icon: 'text-yellow-600',
      badge: 'bg-yellow-100 text-yellow-800',
    };
  } else if (riskLevel.includes('สูง')) {
    return {
      bg: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-800',
      icon: 'text-red-600',
      badge: 'bg-red-100 text-red-800',
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
  if (riskLevel.includes('ต่ำ')) {
    return CheckCircle;
  } else if (riskLevel.includes('กลาง')) {
    return AlertTriangle;
  } else if (riskLevel.includes('สูง')) {
    return XCircle;
  }
  return AlertTriangle;
};

const getFlowDisplayName = (flowName: string): string => {
  const flowNames: { [key: string]: string } = {
    pain: 'อาการปวด',
    swelling: 'อาการบวม',
    bleeding: 'เลือดออก',
    fever: 'ไข้',
    phlebitis: 'Phlebitis',
    suture: 'ไหมเย็บแผล',
    imf: 'การมัดฟัน',
    hip_wound: 'แผลสะโพก',
    walking: 'การเดิน',
    ng_tube: 'สายยางให้อาหาร',
  };
  return flowNames[flowName] || flowName;
};

export default function RiskResult({ flowName, result }: RiskResultProps) {
  const colors = getRiskColor(result.risk_level);
  const Icon = getRiskIcon(result.risk_level);

  return (
    <div className={`${colors.bg} ${colors.border} border-2 rounded-lg p-6 transition-all hover:shadow-lg`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center">
          <Icon className={`w-8 h-8 ${colors.icon} mr-3`} />
          <div>
            <h3 className="text-lg font-bold text-gray-800">
              {getFlowDisplayName(flowName)}
            </h3>
            <span className={`inline-block mt-1 px-3 py-1 rounded-full text-sm font-medium ${colors.badge}`}>
              {result.risk_level}
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
          เหตุผล
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
          คำแนะนำ
        </h4>
        <p className={`${colors.text} text-sm leading-relaxed pl-7`}>
          {result.recommendation}
        </p>
      </div>
    </div>
  );
}
