/**
 * api.js
 * Handles communication with the backend.
 */

// USE A RELATIVE PATH so it works regardless of how you access localhost
const API_BASE_URL = '/api'; 

async function _fetchJson(url, opts) {
    try {
        const res = await fetch(url, opts);
        if (!res.ok) {
            const text = await res.text();
            let errData;
            try { errData = JSON.parse(text); } catch(e) { errData = text; }
            return { error: errData || `Status: ${res.status}`, isError: true };
        }
        return await res.json();
    } catch (err) {
        console.error("Fetch error:", err);
        return { error: "Could not connect to server", isError: true };
    }
}

export const API = {
    async health() {
        return _fetchJson(`${API_BASE_URL}/health`);
    },

    async getStats() {
        return _fetchJson(`${API_BASE_URL}/stats`);
    },

    async search(query) {
        if (!query) return [];
        const encoded = encodeURIComponent(query);
        return _fetchJson(`${API_BASE_URL}/search?q=${encoded}`);
    },

    async autocomplete(prefix) {
        if (!prefix) return [];
        const encoded = encodeURIComponent(prefix);
        const data = await _fetchJson(`${API_BASE_URL}/autocomplete?q=${encoded}`);
        // Ensure we always return an array to avoid .forEach crashes
        return Array.isArray(data) ? data : [];
    },

    async addDocument(doc) {
        return _fetchJson(`${API_BASE_URL}/upload`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(doc)
        });
    }
};