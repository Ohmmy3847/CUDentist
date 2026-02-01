/**
 * Central export point for lib/
 * All imports should come from here for consistency
 */

// API clients - import from api directory
export { riskApi, logApi } from './api';
export { riskApi as api } from './api';

// Types - use type keyword for types only
export type {
  PatientFormData,
  RiskAssessmentResult,
  DescriptionAnalysis,
  RiskSummary,
  ThreeLayerResult,
  ApiError,
  ProgressCallback,
} from './types';

// Form options constants - regular export for runtime values
export {
  GENDER_OPTIONS,
  PROCEDURE_OPTIONS,
  LEFORT_SUB_OPTIONS,
  BSSRO_SUB_OPTIONS,
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
  FOOD_TYPE_OPTIONS,
  FOOD_AMOUNT_OPTIONS,
  NG_TUBE_OPTIONS,
  MOUTH_RINSING_OPTIONS,
  BRUSHING_TEETH_OPTIONS,
} from './types/form.types';
