/**
 * Central export point for lib/
 * All imports should come from here for consistency
 */

import riskApi from './api';
import logApi from './api/log-save-api';
import type {
  PatientFormData,
  RiskAssessmentResult,
  AllFlowsResult,
  ApiError,
} from './types';
import type {
  ProgressCallback,
  UploadProgressCallback,
} from './types/api.types';

// API clients
export { riskApi, logApi };
export { riskApi as api };

// Types
export type {
  PatientFormData,
  RiskAssessmentResult,
  AllFlowsResult,
  ApiError,
  ProgressCallback,
  UploadProgressCallback,
};

// Form options constants
export {
  GENDER_OPTIONS,
  PROCEDURE_OPTIONS,
  PAIN_MEDICATION_OPTIONS,
  SWELLING_OPTIONS,
  BLEEDING_OPTIONS,
  NUMBNESS_OPTIONS,
  PHLEBITIS_OPTIONS,
  SUTURE_OPTIONS,
  OTHER_SYMPTOMS_OPTIONS,
  ANTIBIOTIC_OPTIONS,
  COMPRESS_OPTIONS,
  IMF_OPTIONS,
  IMF_WIRE_OPTIONS,
  WALKING_OPTIONS,
  FEEDING_METHOD_OPTIONS,
  FOOD_AMOUNT_OPTIONS,
  NG_TUBE_OPTIONS,
} from './types';
