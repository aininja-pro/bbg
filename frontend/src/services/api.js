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
};
