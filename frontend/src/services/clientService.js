import api from './api';

const clientService = {
  /**
   * Get all clients with optional search and filters
   */
  async getClients(params = {}) {
    const response = await api.get('/clients', { params });
    return response.data;
  },

  /**
   * Get a single client by ID
   */
  async getClient(id) {
    const response = await api.get(`/clients/${id}`);
    return response.data;
  },

  /**
   * Create a new client
   */
  async createClient(clientData) {
    const response = await api.post('/clients', clientData);
    return response.data;
  },

  /**
   * Update an existing client
   */
  async updateClient(id, clientData) {
    const response = await api.put(`/clients/${id}`, clientData);
    return response.data;
  },

  /**
   * Delete a client
   */
  async deleteClient(id) {
    await api.delete(`/clients/${id}`);
  },

  /**
   * Search clients by name or country
   */
  async searchClients(searchTerm) {
    const response = await api.get('/clients', {
      params: { search: searchTerm },
    });
    return response.data;
  },
};

export default clientService;
