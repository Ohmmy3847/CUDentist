'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, ArrowRight, CheckCircle, Loader2, Trash2 } from 'lucide-react';
import type { PatientFormData } from '@/lib';
import { logApi } from '@/lib';

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

  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const savedData = localStorage.getItem(FORM_STORAGE_KEY);
    const savedStep = localStorage.getItem(STEP_STORAGE_KEY);
    
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData);
        setFormData(parsed);
        setHasSavedData(true);
      } catch (e) {
        console.error('Failed to load saved form data:', e);
      }
    }
    
    if (savedStep) {
      try {
        const step = parseInt(savedStep, 10);
        setCurrentStep(step);
      } catch (e) {
        console.error('Failed to load saved step:', e);
      }
    }
    
    setIsLoaded(true);
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (isLoaded && Object.keys(formData).length > 0) {
      localStorage.setItem(FORM_STORAGE_KEY, JSON.stringify(formData));
    }
  }, [formData, isLoaded]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (isLoaded) {
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

    try {
      // บันทึก raw input ลง Google Sheet ก่อน
      try {
        await logApi.saveRawInput(formData);
        console.log('Successfully saved raw input to Google Sheets');
      } catch (logError) {
        console.error('Failed to save raw input:', logError);
        // Continue anyway - don't block navigation
      }
      
      // บันทึกข้อมูลลง sessionStorage เพื่อส่งไปหน้า result
      sessionStorage.setItem('patientData', JSON.stringify(formData));
      sessionStorage.setItem('isProcessing', 'true');
      
      localStorage.removeItem(FORM_STORAGE_KEY);
      localStorage.removeItem(STEP_STORAGE_KEY);
      
      router.push('/result');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'เกิดข้อผิดพลาดในการบันทึกข้อมูล');
      setIsSubmitting(false);
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
    <div className="w-full flex flex-col items-center justify-center py-6 px-2">
      <div className="cu-container w-full max-w-2xl">
        <div className="mb-6 flex flex-col md:flex-row items-center justify-between gap-2">
          <button
            onClick={() => router.push('/')}
            className="cu-btn bg-cu-gray text-cu-pink border border-cu-pink flex items-center"
          >
            <ArrowLeft className="w-4 h-4 mr-2" /> กลับหน้าหลัก
          </button>
          <h1 className="text-xl md:text-2xl font-bold text-cu-pink text-center">กรอกข้อมูลคนไข้</h1>
          {hasSavedData && (
            <button
              onClick={handleClearDraft}
              className="cu-btn bg-red-100 text-red-700 border border-red-300 flex items-center"
            >
              <Trash2 className="w-4 h-4 mr-2" /> ล้างข้อมูล
            </button>
          )}
        </div>

        <div className="mb-6 flex items-center justify-center gap-2 md:gap-4">
          {STEPS.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div className={`flex flex-col items-center ${currentStep === step.id ? 'text-cu-pink font-bold' : 'text-gray-500'}`}>
                <div className={`w-8 h-8 md:w-10 md:h-10 flex items-center justify-center rounded-full border-2 ${currentStep === step.id ? 'border-cu-pink bg-cu-pink text-white' : currentStep > step.id ? 'border-green-500 bg-green-500 text-white' : 'border-gray-300 bg-white'}`}>
                  {currentStep > step.id ? <CheckCircle className="w-4 h-4 md:w-5 md:h-5" /> : step.id}
                </div>
                <span className="mt-1 md:mt-2 text-xs md:text-sm text-center max-w-[120px]">{step.title}</span>
              </div>
              {index < STEPS.length - 1 && (
                <div className={`h-0.5 w-4 md:w-8 mx-1 md:mx-2 ${currentStep > step.id ? 'bg-green-500' : 'bg-gray-300'}`} />
              )}
            </div>
          ))}
        </div>

        {hasSavedData && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-xs md:text-sm text-blue-800 text-center">
              ✓ พบข้อมูลที่บันทึกไว้ ระบบจะบันทึกอัตโนมัติทุกครั้งที่คุณกรอก
            </p>
          </div>
        )}

        <div className="cu-section bg-white rounded-lg p-4 md:p-6 shadow-cu">
          {renderStepContent()}
        </div>

        {error && (
          <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-center text-sm">
            {error}
          </div>
        )}

        <div className="flex flex-col md:flex-row gap-3 md:gap-4 justify-between mt-6 md:mt-8">
          <button
            onClick={handlePrevious}
            className="cu-btn bg-cu-gray text-cu-pink border border-cu-pink flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={currentStep === 1}
          >
            <ArrowLeft className="w-4 h-4 mr-2" /> ย้อนกลับ
          </button>
          {currentStep < STEPS.length ? (
            <button
              onClick={handleNext}
              className="cu-btn flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={!isCurrentStepValid}
            >
              ถัดไป <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              className="cu-btn flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={!isCurrentStepValid || isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  กำลังบันทึก...
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  ส่งข้อมูลเพื่อประเมิน
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
