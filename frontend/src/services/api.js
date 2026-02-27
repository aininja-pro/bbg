/**
 * API service for BBG backend communication
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

export const api = {
  /**
   * Upload and process Excel file
   * @param {File} file - The Excel file to process
   * @returns {Promise<Blob>} - CSV file blob
   */
  async processAndDownload(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/process-and-download`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Processing failed' }));
      throw new Error(error.detail || 'Failed to process file');
    }

    return await response.blob();
  },

  /**
   * Upload file and get processing results with preview
   * @param {File} file - The Excel file to process
   * @returns {Promise<Object>} - Processing results
   */
  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(error.detail || 'Failed to upload file');
    }

    return await response.json();
  },

  /**
   * Batch process multiple files
   * @param {File[]} files - Array of Excel files to process
   * @param {string} outputMode - 'merged' for single CSV or 'zip' for ZIP archive
   * @returns {Promise<Blob>} - ZIP or CSV file blob
   */
  async batchProcess(files, outputMode = 'zip') {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await fetch(`${API_BASE_URL}/api/batch-process?output_mode=${outputMode}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Batch processing failed' }));
      throw new Error(error.detail || 'Failed to process files');
    }

    return await response.blob();
  },

  /**
   * Health check
   * @returns {Promise<Object>}
   */
  async healthCheck() {
    const response = await fetch(`${API_BASE_URL}/health`);
    return await response.json();
  },

  // NEW CACHED ENDPOINTS FOR FAST DOWNLOADS

  /**
   * Upload file with caching for instant downloads
   * @param {File} file - The Excel file to process
   * @returns {Promise<Object>} - Job status with job_id
   */
  async uploadWithCache(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/upload-with-cache`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(error.detail || 'Failed to upload file');
    }

    return await response.json();
  },

  /**
   * Batch process files with caching
   * @param {File[]} files - Array of Excel files to process
   * @param {string} outputMode - 'merged' for single CSV or 'zip' for ZIP archive
   * @returns {Promise<Object>} - Job status with job_id
   */
  async batchProcessWithCache(files, outputMode = 'merged') {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await fetch(`${API_BASE_URL}/api/batch-process-with-cache?output_mode=${outputMode}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Batch processing failed' }));
      throw new Error(error.detail || 'Failed to process files');
    }

    return await response.json();
  },

  /**
   * Download processed file by job_id (instant!)
   * @param {string} jobId - The job ID from processing
   * @returns {Promise<Blob>} - CSV or ZIP file blob
   */
  async downloadByJobId(jobId) {
    const response = await fetch(`${API_BASE_URL}/api/download/${jobId}`, {
      method: 'GET',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Download failed' }));
      throw new Error(error.detail || 'Failed to download file');
    }

    return await response.blob();
  },

  /**
   * Check job processing status
   * @param {string} jobId - The job ID to check
   * @returns {Promise<Object>} - Job status
   */
  async getJobStatus(jobId) {
    const response = await fetch(`${API_BASE_URL}/api/job-status/${jobId}`, {
      method: 'GET',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get status' }));
      throw new Error(error.detail || 'Failed to get job status');
    }

    return await response.json();
  },

  // USAGE REPORT GENERATION

  /**
   * Generate per-builder usage reports from a master list and template
   * @param {File} masterList - Master Builder List (.xlsx)
   * @param {File} template - Template file (.xlsm)
   * @returns {Promise<{blob: Blob, filesGenerated: number, rowsSkipped: number, warnings: string[]}>}
   */
  /**
   * Start report generation (returns immediately with a job_id)
   */
  async startReportGeneration(masterList, template) {
    const formData = new FormData();
    formData.append('master_list', masterList);
    formData.append('template', template);

    const response = await fetch(`${API_BASE_URL}/api/generate-reports`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Report generation failed' }));
      throw new Error(error.detail || 'Failed to generate reports');
    }

    return await response.json(); // { job_id }
  },

  /**
   * Poll report generation status
   */
  async getReportStatus(jobId) {
    const response = await fetch(`${API_BASE_URL}/api/generate-reports/${jobId}/status`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get status' }));
      throw new Error(error.detail || 'Failed to get report status');
    }

    return await response.json();
  },

  /**
   * Download completed report ZIP
   */
  async downloadReport(jobId) {
    const response = await fetch(`${API_BASE_URL}/api/generate-reports/${jobId}/download`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Download failed' }));
      throw new Error(error.detail || 'Failed to download reports');
    }

    return await response.blob();
  },

  // DISTRIBUTION ENDPOINTS (PHASE 2)

  /**
   * Process distribution reports (Supplier or Territory Manager)
   * @param {File[]} files - Array of CSV files to process
   * @param {string} mode - 'mode1' (Supplier) or 'mode2' (Territory Manager)
   * @returns {Promise<Object>} - Job status with job_id
   */
  async processDistribution(files, mode) {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await fetch(`${API_BASE_URL}/api/distribution/process?mode=${mode}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Distribution processing failed' }));
      throw new Error(error.detail || 'Failed to process distribution');
    }

    return await response.json();
  },

  /**
   * Get distribution processing status
   * @param {string} jobId - The job ID to check
   * @returns {Promise<Object>} - Job status with progress
   */
  async getDistributionStatus(jobId) {
    const response = await fetch(`${API_BASE_URL}/api/distribution/status/${jobId}`, {
      method: 'GET',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get status' }));
      throw new Error(error.detail || 'Failed to get distribution status');
    }

    return await response.json();
  },
};
