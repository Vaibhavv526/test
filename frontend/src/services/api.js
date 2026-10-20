/**
 * API client for Agentic Dating Platform.
 * Communicates with FastAPI backend.
 */

// Use VITE_API_URL env var if deployed (e.g. Vercel pointing to Render), or fallback to relative /api for local Vite proxy
const rawApiUrl = import.meta.env.VITE_API_URL || '';
const API_BASE = rawApiUrl ? `${rawApiUrl.replace(/\/$/, '')}/api` : '/api';

async function request(endpoint, options = {}) {
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, config);
    if (!res.ok) {
      let errorMsg = `Error ${res.status}: ${res.statusText}`;
      try {
        const errorData = await res.json();
        if (errorData.detail) {
          errorMsg = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
        }
      } catch (_) {}
      throw new Error(errorMsg);
    }
    return await res.json();
  } catch (err) {
    console.error(`API Request to ${endpoint} failed:`, err);
    throw err;
  }
}

export const api = {
  // System status & health
  getStatus: () => request('/status'),

  // Profiles
  getProfiles: (params = {}) => {
    const query = new URLSearchParams();
    if (params.source) query.append('source', params.source);
    if (params.search) query.append('search', params.search);
    if (params.limit) query.append('limit', params.limit);
    const qs = query.toString();
    return request(`/profiles${qs ? `?${qs}` : ''}`);
  },

  getProfile: (id) => request(`/profiles/${id}`),

  submitIntake: (data) => request('/profiles/intake', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  generateSynthetic: (count = 5) => request('/profiles/generate-synthetic', {
    method: 'POST',
    body: JSON.stringify({ count }),
  }),

  seedProfiles: () => request('/seed', {
    method: 'POST',
  }),

  deleteProfile: (id) => request(`/profiles/${id}`, {
    method: 'DELETE',
  }),

  // Date Simulation
  simulateDate: (payload) => request('/dates/simulate', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),

  getDateBetween: (profileAId, profileBId) => request(`/dates/between/${profileAId}/${profileBId}`),

  getDateById: (simId) => request(`/dates/${simId}`),

  getDateHistory: (limit = 15) => request(`/dates?limit=${limit}`),

  // Compatibility Rankings
  getRankings: (personId, limit = 25) => request(`/rankings/${personId}?limit=${limit}`),
};
