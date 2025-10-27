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
   * @param {Function} onProgress - Optional callback for progress updates
   * @returns {Promise<Blob>} - ZIP or CSV file blob
   */
  async batchProcess(files, outputMode = 'zip', onProgress = null) {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    // Generate job ID on frontend and pass to backend
    const jobId = crypto.randomUUID();

    // Start polling immediately if progress callback provided
    if (onProgress) {
      this.pollProgress(jobId, onProgress);
    }

    const response = await fetch(`${API_BASE_URL}/api/batch-process?output_mode=${outputMode}&job_id=${jobId}`, {
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
   * Poll for batch processing progress
   * @param {string} jobId - Job ID to track
   * @param {Function} onProgress - Callback function for progress updates
   */
  async pollProgress(jobId, onProgress) {
    console.log('[Progress] Starting polling for job:', jobId);
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/batch-progress/${jobId}`);
        console.log('[Progress] Poll response status:', response.status);
        if (response.ok) {
          const progress = await response.json();
          console.log('[Progress] Progress update:', progress);
          onProgress(progress);

          // Stop polling when complete
          if (progress.status === 'completed') {
            console.log('[Progress] Job completed, stopping polling');
            clearInterval(pollInterval);
          }
        } else {
          // Job not found or expired, stop polling
          console.log('[Progress] Job not found, stopping polling');
          clearInterval(pollInterval);
        }
      } catch (error) {
        // Error polling, stop
        console.error('[Progress] Polling error:', error);
        clearInterval(pollInterval);
      }
    }, 1000); // Poll every second
  },

  /**
   * Health check
   * @returns {Promise<Object>}
   */
  async healthCheck() {
    const response = await fetch(`${API_BASE_URL}/health`);
    return await response.json();
  },
};
