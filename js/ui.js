/**
 * ui.js
 * Handles UI updates, animations, and DOM manipulation.
 */

// DOM Elements
const elements = {
    docCountDisplay: document.getElementById('doc-count-display'),
    statDocuments: document.getElementById('stat-documents'),
    statLexicon: document.getElementById('stat-lexicon'),
    statIndexed: document.getElementById('stat-indexed'),
    statAvgLen: document.getElementById('stat-avg-len'),
    resultsArea: document.getElementById('results-area'),
    searchInput: document.getElementById('search-input'),
    searchBtn: document.getElementById('search-btn')
};

export const UI = {
    /**
     * Update the stats grid with data.
     * @param {Object} stats 
     */
    updateStats(stats) {
        if (!stats) return;

        // Animate numbers (simple implementation)
        elements.statDocuments.innerText = stats.documents.toLocaleString();
        elements.statLexicon.innerText = stats.lexiconSize.toLocaleString();
        elements.statIndexed.innerText = stats.indexedTerms.toLocaleString();
        elements.statAvgLen.innerText = `${stats.avgDocLength.toLocaleString()} words`;

        // Update hero title number as well
        elements.docCountDisplay.innerText = Math.floor(stats.documents / 1000) + 'k+'; // Just a visual touch
    },

    /**
     * Render search results to the results area.
     * @param {Array} results 
     */
    renderResults(results) {
        elements.resultsArea.classList.remove('hidden');
        elements.resultsArea.innerHTML = '';

        if (results.length === 0) {
            elements.resultsArea.innerHTML = `
                <div class="no-results">
                    <p>No results found.</p>
                </div>
            `;
            return;
        }

        const list = document.createElement('div');
        list.className = 'results-list';

        results.forEach(res => {
            const item = document.createElement('div');
            item.className = 'result-item'; // Styles for this would need to be added to components.css if we were doing full results UI
            item.innerHTML = `
                <h3>${res.title || res.id}</h3>
                <div class="meta">Score: ${res.score}% | ID: ${res.id}</div>
                <p>${res.snippet}</p>
            `;
            // Add some basic inline styles for the result item for now if not present in CSS
            item.style.padding = '1rem';
            item.style.borderBottom = '1px solid var(--border-color)';
            item.style.color = 'var(--text-muted)';

            // Fix h3 style
            item.querySelector('h3').style.color = 'var(--primary)';
            item.querySelector('h3').style.marginBottom = '0.5rem';

            list.appendChild(item);
        });

        elements.resultsArea.appendChild(list);
    },

    setLoading(isLoading) {
        if (isLoading) {
            elements.searchBtn.innerHTML = '<span class="loader"></span> Scanning...';
            elements.searchBtn.disabled = true;
        } else {
            elements.searchBtn.innerText = 'Search';
            elements.searchBtn.disabled = false;
        }
    },

    onSearch(callback) {
        elements.searchBtn.addEventListener('click', () => {
            const query = elements.searchInput.value.trim();
            if (query) callback(query);
        });

        elements.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const query = elements.searchInput.value.trim();
                if (query) callback(query);
            }
        });
    }
};
