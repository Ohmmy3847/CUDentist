'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ArrowLeft, ArrowRight, CheckCircle, Loader2, Trash2 } from 'lucide-react';
import type { PatientFormData } from '@/lib';
import { th, en } from '@/lib/locales';

// Import form part components
import BasicInfoForm from '@/components/forms/BasicInfoForm';
import SymptomsForm from '@/components/forms/SymptomsForm';
import DailyLifeForm from '@/components/forms/DailyLifeForm';

const FORM_STORAGE_KEY = 'patientFormDraft';
const STEP_STORAGE_KEY = 'patientFormStep';

function FormContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const lang = (searchParams.get('lang') as 'th' | 'en') || 'th';
  const t = lang === 'th' ? th.form : en.form;

  const STEPS = [
    { id: 1, title: t.steps.basicInfo, description: t.steps.description[1] },
    { id: 2, title: t.steps.symptoms, description: t.steps.description[2] },
    { id: 3, title: t.steps.dailyLife, description: t.steps.description[3] },
  ];

  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<PatientFormData>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isCurrentStepValid, setIsCurrentStepValid] = useState(false);
  const [hasSavedData, setHasSavedData] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Clear result page flags when starting new form
    sessionStorage.removeItem('resultSaved');

    // Also try to restore language from storage if not in URL, or save URL lang to storage
    // For now, simpler to just rely on URL.

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
      // Clear previous result flags to allow new submission
      console.log('=== Form Submit: Clearing flags ===');
      sessionStorage.removeItem('resultSaved');
      sessionStorage.removeItem('riskAssessmentResult');
      sessionStorage.removeItem('isCurrentlyProcessing'); // Also clear processing flag

      // Include language preference in form data
      const finalData: PatientFormData = {
        ...formData,
        // @ts-ignore - adding temporary field for backend
        _language: lang
      };

      // บันทึกข้อมูลลง sessionStorage เพื่อส่งไปหน้า result
      sessionStorage.setItem('patientData', JSON.stringify(finalData));
      sessionStorage.setItem('isProcessing', 'true');

      localStorage.removeItem(FORM_STORAGE_KEY);
      localStorage.removeItem(STEP_STORAGE_KEY);

      router.push(`/result?lang=${lang}`);

      // Start the API call in background (or in parallel) - actually the logic here seems to redirect to /result 
      // which probably triggers the API call or handles it.
      // Wait, in the original file I see:
      /*
      await riskApi.assessPatient(formData, (current, total, status) => {
        setSubmitProgress({ current, total, status });
      });
      */
      // BUT `FormContent` in the viewed file (Step 222) DOES NOT HAVE `assessPatient` call visible in `handleSubmit`.
      // It pushes to `/result`.
      // Ah, I missed something. 
      // The `handleSubmit` in Step 222 pushes to `/result`. 
      // WHERE IS `assessPatient` called?
      // It might be called in `/result/page.tsx`??

      // Let me re-read `form/page.tsx` Step 222 very carefully.
      // It pushes to `/result`. It sets `patientData` in sessionStorage.

      // Therefore, the API call is NOT here. It is likely in the Result page.

      // My previous assumption that `assessPatient` is called in `form/page.tsx` was wrong based on the current file content.
      // I must check `app/result/page.tsx` instead.

    } catch (err) {
      setError(err instanceof Error ? err.message : t.validationError);
      setIsSubmitting(false);
    }
  };

  const handleClearDraft = () => {
    if (confirm(t.confirmClear)) {
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
            lang={lang}
          />
        );
      case 2:
        return (
          <SymptomsForm
            data={formData}
            onChange={handleFormDataChange}
            onValidationChange={setIsCurrentStepValid}
            startingQuestionNumber={13}
            lang={lang}
          />
        );
      case 3:
        // คำนวณจำนวนข้อใน SymptomsForm เพื่อหาเลขเริ่มต้นของ DailyLifeForm
        let symptomsCount = 11; // Base questions (pain, swelling, breathing, bleeding, fever, numbness, phlebitis, suture, other, antibiotic, compress)

        // Conditional questions in SymptomsForm
        if ((formData.pain_score || 0) > 0) symptomsCount++; // Pain medication
        if (formData.has_imf === 'มีการมัดฟัน') symptomsCount++; // IMF wire
        if (formData.special_icbg === 'มี') symptomsCount++; // Walking

        const dailyLifeStartNum = 13 + symptomsCount;

        return (
          <DailyLifeForm
            data={formData}
            onChange={handleFormDataChange}
            onValidationChange={setIsCurrentStepValid}
            startingQuestionNumber={dailyLifeStartNum}
            lang={lang}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="w-full flex flex-col items-center justify-center py-6 px-2">
      <div className="cu-container w-full max-w-2xl">
        <div className="mb-6">
          <div className="grid grid-cols-2 gap-2 mb-3">
            <button
              onClick={() => router.push(`/?lang=${lang}`)}
              className="cu-btn bg-cu-gray text-cu-pink border border-cu-pink flex items-center justify-center text-sm md:text-base"
            >
              <ArrowLeft className="w-4 h-4 mr-1 md:mr-2" /> <span className="hidden sm:inline">{t.back}</span>{t.backHome}
            </button>
            {hasSavedData && (
              <button
                onClick={handleClearDraft}
                className="cu-btn bg-red-100 text-red-700 border border-red-300 flex items-center justify-center text-sm md:text-base"
              >
                <Trash2 className="w-4 h-4 mr-1 md:mr-2" /> {t.clear}
              </button>
            )}
          </div>
          <h1 className="text-xl md:text-2xl font-bold text-cu-pink text-center">{t.title}</h1>
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
              ✓ {t.savedDataFound}
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

        <div className="grid grid-cols-2 gap-3 md:gap-4 mt-6 md:mt-8">
          <button
            onClick={handlePrevious}
            className="cu-btn bg-cu-gray text-cu-pink border border-cu-pink flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={currentStep === 1}
          >
            <ArrowLeft className="w-4 h-4 mr-1 md:mr-2" /> {t.back}
          </button>
          {currentStep < STEPS.length ? (
            <button
              onClick={handleNext}
              className="cu-btn flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={!isCurrentStepValid}
            >
              {t.next} <ArrowRight className="w-4 h-4 ml-1 md:ml-2" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              className="cu-btn flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed text-sm md:text-base"
              disabled={!isCurrentStepValid || isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-1 md:mr-2 animate-spin" />
                  <span className="hidden sm:inline">{t.submitting}</span>
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4 mr-1 md:mr-2" />
                  <span className="hidden sm:inline">{t.submit}</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default function PatientFormPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <FormContent />
    </Suspense>
  );
}
