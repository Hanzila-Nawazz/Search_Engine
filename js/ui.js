/**
 * ui.js
 * Handles UI updates, animations, and DOM manipulation.
 */

const elements = {
    docCountDisplay: document.getElementById('doc-count-display'),
    statDocuments: document.getElementById('stat-documents'),
    statLexicon: document.getElementById('stat-lexicon'),
    statIndexed: document.getElementById('stat-indexed'),
    statAvgLen: document.getElementById('stat-avg-len'),
    resultsArea: document.getElementById('results-area'),
    diagnostics: document.getElementById('diagnostics'),
    searchInput: document.getElementById('search-input'),
    searchBtn: document.getElementById('search-btn'),
    resultsArea: document.getElementById('results-area'),
    searchInput: document.getElementById('search-input'),
    searchBtn: document.getElementById('search-btn'),
    // Container for autocomplete suggestions
    searchWrapper: document.querySelector('.search-wrapper')
};

let _autocompleteContainer = null;
let _activeSuggestion = -1;
let _currentSuggestions = [];
// Create a persistent autocomplete container
let _autoContainer = null;

function _ensureAutoContainer() {
    if (_autoContainer) return _autoContainer;
    _autoContainer = document.createElement('div');
    _autoContainer.className = 'autocomplete-dropdown hidden';
    elements.searchWrapper.appendChild(_autoContainer);
    return _autoContainer;
}

function _ensureAutocompleteContainer() {
    if (_autocompleteContainer) return _autocompleteContainer;
    const wrapper = document.querySelector('.search-wrapper');
    _autocompleteContainer = document.createElement('div');
    _autocompleteContainer.className = 'autocomplete-list';
    Object.assign(_autocompleteContainer.style, {
        position: 'absolute', left: '0', right: '0', top: '56px',
        background: '#ffffff', color: '#000', border: '1px solid #ddd',
        borderRadius: '8px', zIndex: 999, maxHeight: '300px', overflowY: 'auto', display: 'none'
    });
    wrapper.appendChild(_autocompleteContainer);
    return _autocompleteContainer;
}

function _renderAutocomplete(suggestions, onSelect) {
    const container = _ensureAutocompleteContainer();
    container.innerHTML = '';
    _activeSuggestion = -1;
    
    // FIX: Ensure suggestions is actually an array before looping
    _currentSuggestions = Array.isArray(suggestions) ? suggestions : [];

    if (_currentSuggestions.length === 0) {
        container.style.display = 'none';
        return;
    }

    _currentSuggestions.forEach((s) => {
        const item = document.createElement('div');
        item.className = 'autocomplete-item';
        item.innerText = s;
        item.style.padding = '10px';
        item.style.cursor = 'pointer';
        item.addEventListener('click', () => onSelect(s));
        container.appendChild(item);
    });

    container.style.display = 'block';
}

function _hideAutocomplete() {
    if (_autocompleteContainer) _autocompleteContainer.style.display = 'none';
}

export const UI = {
    initAutocomplete(apiAutocompleteFn) {
        let debounceTimer = null;
        elements.searchInput.addEventListener('input', (e) => {
            const q = e.target.value.trim();
            clearTimeout(debounceTimer);
            if (!q) { _hideAutocomplete(); return; }
            debounceTimer = setTimeout(async () => {
                const suggestions = await apiAutocompleteFn(q);
                _renderAutocomplete(suggestions, (value) => {
                    elements.searchInput.value = value;
                    _hideAutocomplete();
                });
            }, 200);
        });
    },

    updateStats(stats) {
        // FIX: Check if stats exist and contain the numbers to prevent .toLocaleString() errors
        if (!stats || stats.isError) return;

        const docs = stats.documents ?? 0;
        const lex = stats.lexiconSize ?? 0;
        const idx = stats.indexedTerms ?? 0;
        const avg = stats.avgDocLength ?? 0;

        elements.statDocuments.innerText = docs.toLocaleString();
        elements.statLexicon.innerText = lex.toLocaleString();
        elements.statIndexed.innerText = idx.toLocaleString();
        elements.statAvgLen.innerText = `${avg.toLocaleString()} words`;
        elements.docCountDisplay.innerText = docs;
    },

    renderResults(results) {
        elements.resultsArea.classList.remove('hidden');
        elements.resultsArea.innerHTML = '';

        if (!results || results.length === 0 || results.isError) {
            elements.resultsArea.innerHTML = `<p style="padding:20px;">No results found or search failed.</p>`;
            return;
        }

        results.forEach(res => {
            const card = document.createElement('div');
            card.className = 'result-card'; 
            card.style.background = 'rgba(255,255,255,0.05)';
            card.style.padding = '15px';
            card.style.marginBottom = '10px';
            card.style.borderRadius = '8px';
            card.innerHTML = `
                <h3 style="color:var(--primary); margin:0;">${res.title}</h3>
                <small style="color:gray;">ID: ${res.id} | Score: ${res.score}</small>
                <p style="margin-top:8px;">${res.snippet}</p>
            `;
            elements.resultsArea.appendChild(card);
        });
    },

    renderError(msg) {
        this.showDiag(msg, 'error');
    },

    showDiag(message, level = 'info') {
        if (!elements.diagnostics) return;
        elements.diagnostics.classList.remove('hidden');
        elements.diagnostics.innerHTML = `<div class="diag ${level}">${message}</div>`;
    },

    clearDiag() {
        elements.diagnostics.classList.add('hidden');
    },

    setLoading(isLoading) {
        elements.searchBtn.disabled = isLoading;
        elements.searchBtn.innerText = isLoading ? 'Searching...' : 'Search';
    },

    onSearch(callback) {
        elements.searchBtn.addEventListener('click', () => {
            const q = elements.searchInput.value.trim();
            if (q) callback(q);
        });
        elements.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const q = elements.searchInput.value.trim();
                if (q) callback(q);
            }
        });
    },

    updateStats(stats) {
        if (!stats || stats.error) return;
        elements.statDocuments.innerText = (stats.documents || 0).toLocaleString();
        elements.statLexicon.innerText = stats.lexiconSize || "0";
        elements.statIndexed.innerText = stats.indexedTerms || "0";
        elements.statAvgLen.innerText = stats.avgDocLength || "0 words";
        elements.docCountDisplay.innerText = stats.documents || 0;
    },

    renderResults(results) {
        elements.resultsArea.classList.remove('hidden');
        elements.resultsArea.innerHTML = '';

        if (!Array.isArray(results) || results.length === 0) {
            elements.resultsArea.innerHTML = `
                <div class="no-results fade-in">
                    <p>0 Documents Found</p>
                </div>`;
            return;
        }

        // 1. Results Summary Bar
        const summary = document.createElement('div');
        summary.className = 'results-summary fade-in';
        summary.innerHTML = `
            <div class="summary-left">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                <span><strong>${results.length}</strong> Documents Found</span>
            </div>
            <div class="summary-right">
                <span class="pill"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> 1 ms</span>
                <span class="pill">${results.length} scanned</span>
            </div>
        `;
        elements.resultsArea.appendChild(summary);

        // 2. Patent Cards
        results.forEach((res, index) => {
            const card = document.createElement('article');
            card.className = 'modern-patent-card fade-in';
            card.style.animationDelay = `${index * 0.08}s`; // Staggered entry

            card.innerHTML = `
                <div class="card-header">
                    <h3 class="card-title">${res.title || 'Untitled Patent'}</h3>
                    <div class="relevance-score">${res.score.toFixed(1)}</div>
                </div>
                
                <p class="card-snippet">${res.snippet || 'No abstract content available for this document.'}</p>
                
                <div class="card-metadata">
                    <div class="meta-item">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
                        <span>${res.id}</span>
                    </div>
                    <div class="meta-item">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                        <span>Assignee / Inventor</span>
                    </div>
                    <div class="meta-item">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                        <span>Dec 19, 2025</span>
                    </div>
                </div>

                <div class="card-tags">
                    <span class="tag">dsa project</span>
                    <span class="tag">inverted index</span>
                    <span class="tag">patent-search</span>
                </div>
            `;
            elements.resultsArea.appendChild(card);
        });
    },

    setLoading(isLoading) {
        elements.searchBtn.innerHTML = isLoading ? '<span class="loader"></span>' : 'Search';
        elements.searchBtn.disabled = isLoading;
    },

    onSearch(callback) {
        elements.searchBtn.onclick = () => {
            const q = elements.searchInput.value.trim();
            if (q) callback(q);
        };
        elements.searchInput.onkeypress = (e) => {
            if (e.key === 'Enter') {
                const q = elements.searchInput.value.trim();
                if (q) callback(q);
            }
        };
    },

    initAutocomplete(apiFn) {
        let debounceTimer;
        elements.searchInput.oninput = () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(async () => {
                const suggestions = await apiFn(elements.searchInput.value);
                // Autocomplete rendering logic here
            }, 200);
        };
    },
    // ... updateStats and setLoading remain the same ...

    renderResults(results) {
        elements.resultsArea.classList.remove('hidden');
        elements.resultsArea.innerHTML = '';

        if (!Array.isArray(results) || results.length === 0) {
            elements.resultsArea.innerHTML = '<div class="no-results fade-in">0 Documents Found</div>';
            return;
        }

        // Results summary bar
        const summary = document.createElement('div');
        summary.className = 'results-summary fade-in';
        summary.innerHTML = `
            <div class="summary-left">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                <span><strong>${results.length}</strong> Documents Found</span>
            </div>
        `;
        elements.resultsArea.appendChild(summary);

        results.forEach((res, index) => {
            const card = document.createElement('article');
            card.className = 'modern-patent-card fade-in';
            card.style.animationDelay = `${index * 0.08}s`;

            // Build tags from CPC codes (split by comma, take first few)
            const cpcCodes = (res.cpc || '').split(',').map(c => c.trim()).filter(c => c && c !== 'N/A').slice(0, 4);
            const tagsHtml = cpcCodes.length > 0
                ? cpcCodes.map(tag => `<span class="tag">${tag}</span>`).join('')
                : '<span class="tag">Patent</span>';

            card.innerHTML = `
                <div class="card-header">
                    <h3 class="card-title">${res.title || 'Untitled Patent'}</h3>
                    <div class="relevance-score">${res.score.toFixed(1)}</div>
                </div>
                
                <p class="card-snippet">${res.snippet || 'No abstract available.'}</p>
                
                <div class="card-metadata">
                    <div class="meta-item">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
                        <span>${res.id}</span>
                    </div>
                    <div class="meta-item">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                        <span>${res.assignees || 'N/A'}</span>
                    </div>
                    <div class="meta-item">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                        <span>${res.date || 'N/A'}</span>
                    </div>
                    <div class="meta-item">
                        <span><strong>CPC:</strong> ${res.cpc || 'N/A'}</span>
                    </div>
                    <div class="meta-item">
                        <span><strong>IPC:</strong> ${res.ipc || 'N/A'}</span>
                    </div>
                </div>

                <div class="card-tags">
                    ${tagsHtml}
                </div>
            `;
            elements.resultsArea.appendChild(card);
        });
    },

    initAutocomplete(apiFn) {
        const container = _ensureAutoContainer();
        let debounceTimer;

        elements.searchInput.oninput = () => {
            const q = elements.searchInput.value.trim();
            clearTimeout(debounceTimer);
            if (!q) { container.classList.add('hidden'); return; }

            debounceTimer = setTimeout(async () => {
                const suggestions = await apiFn(q);
                if (!suggestions || suggestions.length === 0) {
                    container.classList.add('hidden');
                    return;
                }

                container.innerHTML = suggestions.map(s => `
                    <div class="auto-item">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                        ${s}
                    </div>
                `).join('');
                
                container.classList.remove('hidden');

                // Handle suggestion click
                container.querySelectorAll('.auto-item').forEach((item, i) => {
                    item.onclick = () => {
                        elements.searchInput.value = suggestions[i];
                        container.classList.add('hidden');
                    };
                });
            }, 200);
        };

        // Hide when clicking outside
        document.addEventListener('click', (e) => {
            if (!elements.searchWrapper.contains(e.target)) container.classList.add('hidden');
        });
    },

    showAddDocumentModal(onSave) {
        // 1. Create overlay container
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay fade-in-overlay';

        // 2. Define the modal HTML structure matching the design
        overlay.innerHTML = `
            <div class="modal-container scale-up-modal">
                <div class="modal-header">
                    <h3 class="modal-title">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 5V19M5 12H19" stroke="#14b8a6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        Add New Document
                    </h3>
                    <button class="modal-close-btn">&times;</button>
                </div>
                
                <div class="modal-body scrollable-content">
                    <form id="add-doc-form">
                        <div class="form-group">
                            <label for="doc-title">Title *</label>
                            <input type="text" id="doc-title" name="title" placeholder="Document title" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="doc-abstract">Abstract *</label>
                            <textarea id="doc-abstract" name="abstract" rows="5" placeholder="Document abstract or description" required></textarea>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label for="doc-id">Publication Number</label>
                                <input type="text" id="doc-id" name="id" placeholder="e.g., US-2024-001234" required>
                            </div>
                            <div class="form-group">
                                <label for="doc-date">Publication Date</label>
                                <input type="date" id="doc-date" name="publicationDate" style="color-scheme: dark;">
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="doc-assignees">Assignees</label>
                            <input type="text" id="doc-assignees" name="assignees" placeholder="Comma-separated assignees">
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label for="doc-cpc">CPC Code</label>
                                <input type="text" id="doc-cpc" name="cpc" placeholder="e.g., G06F16/00">
                            </div>
                            <div class="form-group">
                                <label for="doc-ipc">IPC Code</label>
                                <input type="text" id="doc-ipc" name="ipc" placeholder="e.g., G06F 16/00">
                            </div>
                        </div>

                         <div class="form-group" style="margin-bottom: 0;">
                            <label for="doc-keywords">Keywords</label>
                            <input type="text" id="doc-keywords" name="keywords" placeholder="Comma-separated keywords">
                        </div>
                    </form>
                </div>

                <div class="modal-footer">
                    <button type="button" class="btn-modal-cancel" id="modal-cancel-btn">Cancel</button>
                    <button type="submit" form="add-doc-form" class="btn-modal-add">Add Document</button>
                </div>
            </div>
        `;

        // 3. Append to body
        document.body.appendChild(overlay);
        // Prevent background scrolling while modal is open
        document.body.style.overflow = 'hidden';

        // 4. Event Handlers
        const close = () => {
            document.body.removeChild(overlay);
            document.body.style.overflow = ''; // Restore scrolling
        };

        overlay.querySelector('.modal-close-btn').onclick = close;
        overlay.querySelector('#modal-cancel-btn').onclick = close;
        
        // Close on clicking outside the modal container
        overlay.onclick = (e) => {
            if (e.target === overlay) close();
        };

        overlay.querySelector('#add-doc-form').onsubmit = (e) => {
            e.preventDefault();
            // Gather form data into an object
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            onSave(data, close);
        };
    },

    showDiag(message, level = 'info') {
        if (!elements.diagnostics) return;
        elements.diagnostics.classList.remove('hidden');
        elements.diagnostics.innerHTML = `<div class="diag ${level}">${message}</div>`;
        // Auto-dismiss after 5 seconds
        clearTimeout(this._diagTimer);
        this._diagTimer = setTimeout(() => this.clearDiag(), 5000);
    },

    clearDiag() {
        if (!elements.diagnostics) return;
        elements.diagnostics.classList.add('hidden');
        elements.diagnostics.innerHTML = '';
    },

    renderError(msg) {
        this.showDiag(msg, 'error');
    }

    
};