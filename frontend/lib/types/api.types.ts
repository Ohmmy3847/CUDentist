/**
 * API Response Types - Updated to match Pydantic models
 */

/**
 * Single risk assessment result for one flow
 */
export interface RiskAssessmentResult {
  risk_level: string;
  recommendation: string;
  reason: string;
}

/**
 * Description field analysis result (LLM-based) - Updated
 */
export interface DescriptionAnalysis {
  has_risk: boolean;
  risk_level: string;  // "ปกติ", "เฝ้าระวัง", "เสี่ยง"
  analysis: string;
  key_points: string[];
}

/**
 * Overall summary and recommendations (LLM-based)
 */
export interface RiskSummary {
  overall_risk: string;
  summary: string;
  critical_issues: string[];
}

/**
 * Patient Question Answer (LLM-based) - NEW
 */
export interface PatientQuestionAnswer {
  answer: string;
  urgency_level: string;  // "ปกติ", "ติดตาม", "เร่งด่วน"
  should_contact_doctor: boolean;
  related_risks: string[];
}

/**
 * Complete 3-Layer Response - Updated
 */
export interface ThreeLayerResult {
  flows: { [flowName: string]: RiskAssessmentResult };  // Rule-based results
  descriptions: { [fieldName: string]: DescriptionAnalysis };  // LLM analysis (not shown separately now)
  summary: RiskSummary;  // Overall LLM summary (includes description context)
  patient_qa: PatientQuestionAnswer;  // Answer to patient questions (structured)
  errors?: { [flowName: string]: string };  // Any errors
}

/**
 * API error response
 */
export interface ApiError {
  detail: string;
}

/**
 * Progress callback for classification
 */
export type ProgressCallback = (
  current: number,
  total: number,
  flowName: string
) => void;
