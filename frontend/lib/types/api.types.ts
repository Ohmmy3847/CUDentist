/**
 * API Response Types
 * Types for backend API responses
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
 * All flows risk assessment results
 * Key: flow name (e.g., "อาการปวด", "อาการบวม")
 * Value: RiskAssessmentResult
 */
export interface AllFlowsResult {
  [flowName: string]: RiskAssessmentResult;
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

/**
 * Upload progress callback
 */
export type UploadProgressCallback = (
  uploadPercent: number,
  processedRows?: number,
  totalRows?: number
) => void;
