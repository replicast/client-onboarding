import api, { uploadFile } from './api';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const documentService = {
  /**
   * Get all documents for a client
   */
  async getDocuments(clientId) {
    const response = await api.get(`/documents/clients/${clientId}/documents`);
    return response.data;
  },

  /**
   * Get a single document by ID
   */
  async getDocument(documentId) {
    const response = await api.get(`/documents/${documentId}`);
    return response.data;
  },

  /**
   * Upload a document for a client
   * @param {number} clientId - The client ID
   * @param {File} file - The file to upload
   * @param {function} onProgress - Progress callback (0-100)
   */
  async uploadDocument(clientId, file, onProgress) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await uploadFile(
      `/documents/clients/${clientId}/documents`,
      formData,
      onProgress
    );
    return response.data;
  },

  /**
   * Delete a document
   */
  async deleteDocument(documentId) {
    await api.delete(`/documents/${documentId}`);
  },

  /**
   * Get the download URL for a document (redirect-based)
   */
  getDownloadUrl(documentId) {
    return `${API_BASE_URL}/documents/${documentId}/download`;
  },

  /**
   * Get the direct SAS URL for a document (no redirect)
   */
  async getDirectUrl(documentId) {
    const response = await api.get(`/documents/${documentId}/url`);
    return response.data.url;
  },

  /**
   * Format file size for display
   */
  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },
};

export default documentService;
