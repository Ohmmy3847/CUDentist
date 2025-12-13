'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, ArrowRight, CheckCircle, Loader2, Trash2 } from 'lucide-react';
import type { PatientFormData, AllFlowsResult } from '@/lib/types';
import { api } from '@/lib/api';

// Import form part components
import BasicInfoForm from '@/components/forms/BasicInfoForm';
import SymptomsForm from '@/components/forms/SymptomsForm';
import DailyLifeForm from '@/components/forms/DailyLifeForm';

const STEPS = [
  { id: 1, title: 'ข้อมูลพื้นฐาน', description: 'ข้อ 1-5' },
  { id: 2, title: 'อาการ', description: 'ข้อ 6-20' },
  { id: 3, title: 'การใช้ชีวิตประจำวัน', description: 'ข้อ 21-27' },
];

const FORM_STORAGE_KEY = 'patientFormDraft';
const STEP_STORAGE_KEY = 'patientFormStep';

export default function PatientFormPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<PatientFormData>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isCurrentStepValid, setIsCurrentStepValid] = useState(false);
  const [hasSavedData, setHasSavedData] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);
  const [processingProgress, setProcessingProgress] = useState({ current: 0, total: 0, flowName: '' });

  // Debug validation state
  useEffect(() => {
    console.log('Validation state changed:', isCurrentStepValid);
  }, [isCurrentStepValid]);

  // Load saved data from localStorage on mount
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const savedData = localStorage.getItem(FORM_STORAGE_KEY);
    const savedStep = localStorage.getItem(STEP_STORAGE_KEY);
    
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData);
        console.log('Loaded saved data:', parsed);
        setFormData(parsed);
        setHasSavedData(true);
      } catch (e) {
        console.error('Failed to load saved form data:', e);
      }
    }
    
    if (savedStep) {
      try {
        const step = parseInt(savedStep, 10);
        console.log('Loaded saved step:', step);
        setCurrentStep(step);
      } catch (e) {
        console.error('Failed to load saved step:', e);
      }
    }
    
    setIsLoaded(true);
  }, []);

  // Save formData to localStorage whenever it changes (after initial load)
  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (isLoaded && Object.keys(formData).length > 0) {
      console.log('Saving form data:', formData);
      localStorage.setItem(FORM_STORAGE_KEY, JSON.stringify(formData));
    }
  }, [formData, isLoaded]);

  // Save current step to localStorage whenever it changes (after initial load)
  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (isLoaded) {
      console.log('Saving step:', currentStep);
      localStorage.setItem(STEP_STORAGE_KEY, currentStep.toString());
    }
  }, [currentStep, isLoaded]);

  const handleNext = () => {
    if (currentStep < STEPS.length) {
      setCurrentStep(currentStep + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleFormDataChange = (data: Partial<PatientFormData>) => {
    setFormData(prev => ({ ...prev, ...data }));
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);
    setProcessingProgress({ current: 0, total: 0, flowName: '' });

    try {
      const result: AllFlowsResult = await api.classifyPatient(
        formData,
        (current, total, flowName) => {
          setProcessingProgress({ current, total, flowName });
        }
      );
      
      // Store result in sessionStorage and navigate to result page
      sessionStorage.setItem('riskAssessmentResult', JSON.stringify(result));
      sessionStorage.setItem('patientData', JSON.stringify(formData));
      
      // Clear saved draft after successful submission
      localStorage.removeItem(FORM_STORAGE_KEY);
      localStorage.removeItem(STEP_STORAGE_KEY);
      
      router.push('/result');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'เกิดข้อผิดพลาดในการประเมินความเสี่ยง');
      setIsSubmitting(false);
      setProcessingProgress({ current: 0, total: 0, flowName: '' });
    }
  };

  const handleClearDraft = () => {
    if (confirm('คุณต้องการล้างข้อมูลที่บันทึกไว้ใช่หรือไม่?')) {
      localStorage.removeItem(FORM_STORAGE_KEY);
      localStorage.removeItem(STEP_STORAGE_KEY);
      setFormData({});
      setCurrentStep(1);
      setHasSavedData(false);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <BasicInfoForm
            data={formData}
            onChange={handleFormDataChange}
            onValidationChange={setIsCurrentStepValid}
          />
        );
      case 2:
        return (
          <SymptomsForm
            data={formData}
            onChange={handleFormDataChange}
            onValidationChange={setIsCurrentStepValid}
          />
        );
      case 3:
        return (
          <DailyLifeForm
            data={formData}
            onChange={handleFormDataChange}
            onValidationChange={setIsCurrentStepValid}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/')}
            className="flex items-center text-gray-600 hover:text-gray-800 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            กลับหน้าหลัก
          </button>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">
                แบบฟอร์มประเมินความเสี่ยงผู้ป่วยหลังผ่าตัด
              </h1>
              <p className="text-gray-600 mt-2">
                ติดตามอาการผู้ป่วยหลังกลับบ้านเป็นเวลา 3 วัน
              </p>
            </div>
            {hasSavedData && (
              <button
                onClick={handleClearDraft}
                className="flex items-center px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors border border-red-200"
                title="ล้างข้อมูลที่บันทึกไว้"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                ล้างข้อมูล
              </button>
            )}
          </div>
          {hasSavedData && (
            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                ✓ พบข้อมูลที่บันทึกไว้ ระบบจะบันทึกข้อมูลอัตโนมัติทุกครั้งที่คุณกรอก
              </p>
            </div>
          )}
        </div>

        {/* Progress Steps */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            {STEPS.map((step, index) => (
              <div key={step.id} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                      currentStep > step.id
                        ? 'bg-green-500 text-white'
                        : currentStep === step.id
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-500'
                    }`}
                  >
                    {currentStep > step.id ? (
                      <CheckCircle className="w-6 h-6" />
                    ) : (
                      step.id
                    )}
                  </div>
                  <div className="mt-2 text-center">
                    <div
                      className={`font-medium ${
                        currentStep >= step.id ? 'text-gray-800' : 'text-gray-400'
                      }`}
                    >
                      {step.title}
                    </div>
                    <div className="text-xs text-gray-500">{step.description}</div>
                  </div>
                </div>
                {index < STEPS.length - 1 && (
                  <div
                    className={`flex-1 h-1 mx-4 ${
                      currentStep > step.id ? 'bg-green-500' : 'bg-gray-200'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Form Content */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-6">
          {renderStepContent()}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            <p className="font-medium">เกิดข้อผิดพลาด:</p>
            <p>{error}</p>
          </div>
        )}

        {/* Processing Progress */}
        {isSubmitting && processingProgress.total > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">
                กำลังประมวลผล: {processingProgress.flowName}
              </span>
              <span className="text-sm font-medium text-blue-600">
                {processingProgress.current} / {processingProgress.total}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                style={{ 
                  width: `${(processingProgress.current / processingProgress.total) * 100}%` 
                }}
              />
            </div>
            <p className="text-xs text-gray-600 mt-2">
              กำลังวิเคราะห์ความเสี่ยงด้วย AI... กรุณารอสักครู่
            </p>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="flex justify-between items-center bg-white rounded-lg shadow-md p-6">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 1}
            className={`flex items-center px-6 py-3 rounded-lg font-medium transition-colors ${
              currentStep === 1
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            ย้อนกลับ
          </button>

          {currentStep < STEPS.length ? (
            <button
              onClick={handleNext}
              disabled={!isCurrentStepValid}
              className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              ถัดไป
              <ArrowRight className="w-5 h-5 ml-2" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={isSubmitting || !isCurrentStepValid}
              className="flex items-center px-6 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  กำลังประเมิน...
                </>
              ) : (
                <>
                  <CheckCircle className="w-5 h-5 mr-2" />
                  ส่งและประเมินความเสี่ยง
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
