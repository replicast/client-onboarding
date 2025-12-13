import api from './api';

const siteService = {
  /**
   * Get all sites for a specific client
   */
  async getSitesForClient(clientId) {
    const response = await api.get(`/sites/clients/${clientId}/sites`);
    return response.data;
  },

  /**
   * Get a single site by ID
   */
  async getSite(id) {
    const response = await api.get(`/sites/${id}`);
    return response.data;
  },

  /**
   * Create a new site for a client
   */
  async createSite(clientId, siteData) {
    const response = await api.post(`/sites/clients/${clientId}/sites`, siteData);
    return response.data;
  },

  /**
   * Update an existing site
   */
  async updateSite(id, siteData) {
    const response = await api.put(`/sites/${id}`, siteData);
    return response.data;
  },

  /**
   * Delete a site
   */
  async deleteSite(id) {
    await api.delete(`/sites/${id}`);
  },
};

export default siteService;
