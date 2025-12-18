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

    // 3. Add Document button behavior
    const addBtn = document.getElementById('add-doc-btn');
    if (addBtn) {
        addBtn.addEventListener('click', (e) => {
            console.log('Add Document button clicked');
            const overlay = document.createElement('div');
            overlay.style = 'position:fixed;left:0;top:0;right:0;bottom:0;background:rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center;z-index:999;';
            const form = document.createElement('form');
            form.style = 'background:var(--bg);padding:1rem;border-radius:8px;min-width:320px;';
            form.innerHTML = `
                <h3>Add Document</h3>
                <label>Id<br><input name="id" required placeholder="AU-2001234567-C1"></label><br><br>
                <label>Title<br><input name="title" placeholder="Title"></label><br><br>
                <label>Abstract<br><textarea name="abstract" rows="6" placeholder="Abstract"></textarea></label><br><br>
                <div style="display:flex;gap:0.5rem;justify-content:flex-end;">
                    <button type="button" id="cancel-add">Cancel</button>
                    <button type="submit">Save</button>
                </div>
            `;
            overlay.appendChild(form);
            document.body.appendChild(overlay);

            form.querySelector('#cancel-add').addEventListener('click', () => {
                document.body.removeChild(overlay);
            });

            form.addEventListener('submit', async (ev) => {
                ev.preventDefault();
                const id = form.elements.id.value.trim();
                const title = form.elements.title.value.trim();
                const abstract = form.elements.abstract.value.trim();
                if (!id) {
                    alert('Id required');
                    return;
                }
                try {
                    const res = await API.addDocument({ id, title, abstract });
                    if (res && res.error) {
                        alert('Failed: ' + res.error);
                    } else {
                        alert('Document saved. Note: index not updated automatically.');
                        // refresh stats
                        const stats = await API.getStats();
                        UI.updateStats(stats);
                        UI.clearDiag();
                    }
                } catch (err) {
                    console.error('Failed to add document:', err);
                    alert('Failed to add document. See console for details.');
                } finally {
                    if (document.body.contains(overlay)) document.body.removeChild(overlay);
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
