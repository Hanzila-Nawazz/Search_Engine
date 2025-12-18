/**
 * api.js
 * Handles communication with the backend.
 * Currently mocks data until backend API is ready.
 */

const API_BASE_URL = 'http://localhost:5000/api'; // Placeholder

export const API = {
    /**
     * Fetch system statistics (doc count, lexicon size, etc.)
     */
    async getStats() {
        // Mock delay
        await new Promise(resolve => setTimeout(resolve, 500));
        
        return {
            documents: 45892,
            lexiconSize: 128456,
            indexedTerms: 892341,
            avgDocLength: 2847
        };
    },

    /**
     * Search for documents given a query string.
     * @param {string} query 
     */
    async search(query) {
        // Mock delay
        await new Promise(resolve => setTimeout(resolve, 800));

        if (!query) return [];

        // Mock results based on query
        return [
            {
                id: 'doc_12345',
                title: 'Introduction to Data Structures',
                snippet: '...efficient storage and retrieval of data is crucial for <b>' + query + '</b> performance...',
                score: 98.5
            },
            {
                id: 'doc_67890',
                title: 'Advanced Algorithms: Graph Theory',
                snippet: '...optimizing search paths using Dijkstra methods related to <b>' + query + '</b>...',
                score: 85.2
            },
            {
                id: 'doc_54321',
                title: 'System Design Patterns',
                snippet: '...scalability considerations for <b>' + query + '</b> based microservices...',
                score: 76.0
            }
        ];
    }
};
