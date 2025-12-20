/**
 * Log Save API Client
 * Handles all API calls related to logging form submissions to backend
 */

import axios, { AxiosError } from 'axios';
import type { PatientFormData, AllFlowsResult, ApiError } from '../types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Log API client for form submission logging
 */
export const logApi = {
  /**
   * Save form data with AI risk assessment results
   * 
   * @param formData - Patient form data
   * @param results - Risk assessment results from all flows
   * @param sessionId - Optional session identifier
   */
  saveLog: async (
    formData: PatientFormData,
    results: AllFlowsResult,
    sessionId?: string
  ): Promise<{ status: string; timestamp: string; session_id?: string }> => {
    try {
      const response = await apiClient.post('/log/submission', {
        form_data: formData,
        results: results,
        session_id: sessionId,
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<ApiError>;
        throw new Error(
          axiosError.response?.data?.detail || 'Failed to save log'
        );
      }
      throw error;
    }
  },

  /**
   * Save raw form input without results
   * 
   * @param formData - Raw patient form data
   */
  saveRawInput: async (
    formData: PatientFormData
  ): Promise<{ status: string; timestamp: string }> => {
    try {
      const response = await apiClient.post('/log/raw-input', formData);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<ApiError>;
        throw new Error(
          axiosError.response?.data?.detail || 'Failed to save raw input'
        );
      }
      throw error;
    }
  },};

export default logApi;