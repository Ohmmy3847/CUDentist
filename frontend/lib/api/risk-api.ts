/**
 * Risk Assessment API Client
 * Handles all API calls related to risk classification
 */

import axios, { AxiosError } from 'axios';
import type {
  PatientFormData,
  ApiError,
  ThreeLayerResult,
} from '../types';
import type {
  ProgressCallback,
} from '../types/api.types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Risk Assessment API
 */
export const riskApi = {
  /**
   * Comprehensive patient risk assessment with progress tracking
   * Returns 3-layer response: flows, descriptions, summary, patient_qa
   */
  assessPatient: async (
    data: PatientFormData,
    onProgress?: ProgressCallback,
    language: string = 'th'
  ): Promise<ThreeLayerResult> => {
    try {
      // Show phases instead of fake flow-by-flow progress
      const phases = language === 'en'
        ? [
          { name: '1. Assessing 17 risk factors...', progress: 30 },
          { name: '2. AI Analysis in progress...', progress: 60 },
          { name: '3. Generating summary...', progress: 90 },
        ]
        : [
          { name: '1. ประเมินความเสี่ยง 17 ด้าน...', progress: 30 },
          { name: '2. วิเคราะห์รายละเอียดด้วย AI...', progress: 60 },
          { name: '3. สรุปผลและคำแนะนำ...', progress: 90 },
        ];

      let currentPhase = 0;
      const showPhase = () => {
        if (onProgress && currentPhase < phases.length) {
          const phase = phases[currentPhase];
          onProgress(phase.progress, 100, phase.name);
          currentPhase++;
        }
      };

      // Start classification immediately
      showPhase(); // Show phase 1

      // Separate basic info from assessment data
      const {
        // Personal Information
        first_name,
        last_name,
        phone,
        birth_date,
        // Basic Medical Info
        gender,
        hn,
        procedures,
        lefort_sub_options,
        bssro_sub_options,
        surgery_date,
        discharge_date,
        note,
        // Special Procedures
        imf_wire,
        imf_wire_loops,
        imf_elastic,
        imf_elastic_loops,
        special_icbg,
        special_icbg_description,
        special_ng_tube,
        special_ng_tube_description,
        // Rest is assessment data (symptoms, care, etc.)
        ...assessmentData
      } = data;

      const apiPromise = apiClient.post<ThreeLayerResult>('/patient-assessment', {
        basic_info: {
          // Personal Information
          first_name,
          last_name,
          phone,
          birth_date,
          // Basic Medical Info
          gender,
          hn,
          procedures,
          lefort_sub_options,
          bssro_sub_options,
          surgery_date,
          discharge_date,
          note,
          // Special Procedures
          imf_wire,
          imf_wire_loops,
          imf_elastic,
          imf_elastic_loops,
          special_icbg,
          special_icbg_description,
          special_ng_tube,
          special_ng_tube_description,
        },
        assessment_data: assessmentData,
        language: language,
      });

      // Update progress every 3 seconds while waiting
      const progressInterval = setInterval(() => {
        showPhase();
      }, 3000);

      const response = await apiPromise;
      clearInterval(progressInterval);

      // Show completion
      if (onProgress) {
        onProgress(100, 100, '✅ ประเมินเสร็จสมบูรณ์');
      }

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<ApiError>;
        throw new Error(
          axiosError.response?.data?.detail || 'Failed to classify patient data'
        );
      }
      throw error;
    }
  },

  /**
   * Get available flows
   */
  getFlows: async (): Promise<string[]> => {
    try {
      const response = await apiClient.get<{ flows: string[] }>('/flows');
      return response.data.flows;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<ApiError>;
        throw new Error(
          axiosError.response?.data?.detail || 'Failed to fetch flows'
        );
      }
      throw error;
    }
  },

  /**
   * Health check
   */
  healthCheck: async (): Promise<boolean> => {
    try {
      await apiClient.get('/');
      return true;
    } catch {
      return false;
    }
  },
};
