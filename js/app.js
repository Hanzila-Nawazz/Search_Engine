/**
 * app.js
 * Main entry point. Connects API and UI.
 */

import { API } from './api.js';
import { UI } from './ui.js';

document.addEventListener('DOMContentLoaded', async () => {
    console.log('NexaSearch App Initializing...');

    // 1. Load Stats
    try {
        const stats = await API.getStats();
        UI.updateStats(stats);
    } catch (err) {
        console.error('Failed to load stats:', err);
    }

    // 2. Setup Search Listener
    UI.onSearch(async (query) => {
        console.log('Searching for:', query);
        UI.setLoading(true);

        try {
            const results = await API.search(query);
            UI.renderResults(results);
        } catch (err) {
            console.error('Search failed:', err);
        } finally {
            UI.setLoading(false);
        }
    });
});
