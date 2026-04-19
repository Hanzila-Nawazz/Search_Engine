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
        UI.renderError('Failed to load system stats. See console for details.');
    }

    // 1b. Autocomplete wiring
    try {
        UI.initAutocomplete(API.autocomplete.bind(API));
    } catch (err) {
        console.error('Failed to initialize autocomplete:', err);
        // no visual needed here — autocomplete will silently be unavailable
    }

    // 2. Setup Search Listener
    UI.onSearch(async (query) => {
        console.log('Searching for:', query);
        UI.setLoading(true);

        try {
            const results = await API.search(query);
            // API may return an error object with status (e.g., 503). Handle that gracefully
            if (results && results.error) {
                UI.renderError(results.error);
            } else {
                UI.renderResults(results);
            }
        } catch (err) {
            console.error('Search failed:', err);
            UI.renderError('Search failed. See console for details.');
        } finally {
            UI.setLoading(false);
        }
    });

    // 3. Add Document button — uses the styled modal from UI
    const addBtn = document.getElementById('add-doc-btn');
    if (addBtn) {
        addBtn.addEventListener('click', () => {
            UI.showAddDocumentModal(async (formData, closeModal) => {
                try {
                    const res = await API.addDocument(formData);
                    if (res && res.isError) {
                        UI.showDiag('Failed to add document: ' + (res.error?.message || res.error), 'error');
                    } else {
                        UI.showDiag(`Document "${formData.title || formData.id}" indexed successfully!`, 'info');
                        // Refresh stats to reflect the new document
                        const stats = await API.getStats();
                        UI.updateStats(stats);
                        closeModal();
                    }
                } catch (err) {
                    console.error('Failed to add document:', err);
                    UI.showDiag('Failed to add document. See console for details.', 'error');
                }
            });
        });
    }

    // Run a health check and display diagnostics
    try {
        const health = await API.health();
        if (health && health.error) {
            UI.showDiag('Backend health check failed: ' + health.error, 'error');
        } else if (health) {
            UI.showDiag(`Engine: ${health.engineAvailable ? 'OK' : 'Unavailable'} | Autocomplete: ${health.autocompleteAvailable ? 'OK' : 'Unavailable'} | Documents: ${health.documents}`, 'info');
            if (!health.engineAvailable) UI.showDiag('Search engine not initialized. Search will be unavailable until dependencies are installed or files provided.', 'warning');
        }
    } catch (err) {
        console.error('Health check failed', err);
        UI.showDiag('Health check failed. See console.', 'error');
    }
});
