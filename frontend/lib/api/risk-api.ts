/**
 * Risk Assessment API Client
 * Handles all API calls related to risk classification
 */

import axios, { AxiosError } from 'axios';
import type {
  PatientFormData,
  AllFlowsResult,
  ApiError,
} from '../types';
import type {
  ProgressCallback,
  UploadProgressCallback,
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
   * Classify patient risk across all flows with progress tracking
   */
  classifyPatient: async (
    data: PatientFormData,
    onProgress?: ProgressCallback
  ): Promise<AllFlowsResult> => {
    try {
      // Get list of flows first
      const flowsResponse = await apiClient.get<{ flows: string[] }>('/flows');
      const flows = flowsResponse.data.flows;
      const totalFlows = flows.length;

      // Show progress before starting actual API call
      if (onProgress) {
        // Simulate progress during preparation phase
        for (let i = 0; i < Math.min(3, totalFlows); i++) {
          onProgress(i + 1, totalFlows, 'กำลังเตรียมข้อมูล...');
          await new Promise(resolve => setTimeout(resolve, 200));
        }
      }

      // Start classification - send data wrapped in { data: ... }
      const startTime = Date.now();
      const response = await apiClient.post<AllFlowsResult>('/classify-all-flows', {
        data: data,
      });
      const elapsed = Date.now() - startTime;

      // Simulate progress during/after processing to show user what's happening
      if (onProgress) {
        const minDisplayTime = 2000; // แสดง loading อย่างน้อย 2 วินาที
        const remainingTime = Math.max(0, minDisplayTime - elapsed);
        const steps = Math.max(1, Math.floor(remainingTime / 150));
        const startProgress = Math.min(3, totalFlows);
        
        for (let i = startProgress; i < totalFlows; i++) {
          onProgress(i + 1, totalFlows, flows[i] || 'กำลังวิเคราะห์...');
          await new Promise(resolve => setTimeout(resolve, Math.floor(remainingTime / (totalFlows - startProgress))));
        }
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
   * Upload CSV file and get processed results
   */
  uploadCSV: async (
    file: File,
    maxConcurrent: number = 10,
    onProgress?: UploadProgressCallback
  ): Promise<Blob> => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      // Estimate total rows for progress (read first to count)
      let estimatedRows = 0;
      try {
        const text = await file.text();
        estimatedRows = text.split('\n').length - 1; // -1 for header
      } catch {
        // Fallback to file size estimate
        estimatedRows = Math.floor(file.size / 500); // rough estimate
      }

      const response = await apiClient.post(
        `/classify-csv?max_concurrent=${maxConcurrent}`,
        formData,
        {
          responseType: 'blob',
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            if (onProgress && progressEvent.total) {
              const uploadPercent = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              // First 10% is upload
              onProgress(Math.min(uploadPercent, 100), 0, estimatedRows);
            }
          },
          onDownloadProgress: (progressEvent) => {
            if (onProgress && progressEvent.total) {
              const downloadPercent = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              // Simulate processing progress (90% upload + processing, 10% download)
              const processedRows = Math.floor((downloadPercent / 100) * estimatedRows);
              onProgress(100, processedRows, estimatedRows);
            }
          },
        }
      );

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<ApiError>;
        throw new Error(
          axiosError.response?.data?.detail || 'Failed to process CSV file'
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
