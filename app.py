import atexit
import csv
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import re
import threading

# Import your custom logic
from lexicon import clean_and_tokenize_text
from searcher import SearchEngine
from autoComplete import AutoCompleteSystem

app = Flask(__name__)
CORS(app)

# Paths
DATA_DIR = "patent_docs"
CSV_PATH = "patents_dataset.csv"
FORWARD_INDEX_PATH = "forward_index.txt"

# Global Stats Cache
SERVER_STATS = {
    'documents': 0,
    'lexiconSize': 0,
    'indexedTerms': 0,
    'avgDocLength': 0
}

# In-memory metadata lookup from the CSV (keyed by publication_number)
PATENT_METADATA = {}

def load_csv_metadata():
    """Load patent metadata from the CSV into an in-memory dictionary for fast lookup."""
    global PATENT_METADATA
    if not os.path.exists(CSV_PATH):
        print(f"Warning: {CSV_PATH} not found. Document metadata will be unavailable.")
        return

    print(f"Loading patent metadata from {CSV_PATH}...")
    count = 0
    try:
        with open(CSV_PATH, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pub_num = row.get('publication_number', '').strip()
                if pub_num:
                    PATENT_METADATA[pub_num] = {
                        'title': row.get('title', 'N/A').strip(),
                        'abstract': row.get('abstract', '').strip(),
                        'filing_date': row.get('filing_date', 'N/A').strip(),
                        'publication_date': row.get('publication_date', 'N/A').strip(),
                        'cpc_codes': row.get('cpc_codes', 'N/A').strip(),
                        'ipc_codes': row.get('ipc_codes', 'N/A').strip(),
                        'inventors': row.get('inventors', 'N/A').strip(),
                        'assignees': row.get('assignees', 'N/A').strip(),
                    }
                    count += 1
        print(f"Loaded metadata for {count:,} patents.")
    except Exception as e:
        print(f"Error loading CSV metadata: {e}")

# Load CSV metadata at startup
load_csv_metadata()

# --- Initialize Systems ---
print("--- Loading NexaSearch Subsystems ---")
try:
    ENGINE = SearchEngine()
    print("Search Engine: READY")
    
    # Register the save function to run when the program closes
    atexit.register(ENGINE.save_state_to_disk)
except Exception as e:
    print(f"Search Engine: FAILED ({e})")
    ENGINE = None

try:
    AUTOCOMPLETE = AutoCompleteSystem()
    print("Autocomplete: READY")
except Exception as e:
    print(f"Autocomplete: FAILED ({e})")
    AUTOCOMPLETE = None

# --- OPTIMIZATION: Pre-calculate Stats at Startup ---
def precalculate_stats():
    print("Pre-calculating statistics... (This happens only once)")
    try:
        # 1. Document Count — use the loaded CSV metadata
        doc_count = len(PATENT_METADATA)

        # 2. Indexed Terms — count from forward_index.txt (each line = 1 doc, entries = word_id freq pairs)
        total_indexed_terms = 0
        if os.path.exists(FORWARD_INDEX_PATH):
            with open(FORWARD_INDEX_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    # Format: DOC_ID : word_id freq, word_id freq, ...
                    parts = line.split(' : ', 1)
                    if len(parts) == 2:
                        entries = parts[1].split(',')
                        total_indexed_terms += len(entries)

        avg_doc_len = (total_indexed_terms // doc_count) if doc_count > 0 else 0

        # 3. Lexicon Size
        lexicon_count = len(ENGINE.lexicon) if ENGINE else 0

        # Save to global cache
        SERVER_STATS['documents'] = f"{doc_count:,}"
        SERVER_STATS['lexiconSize'] = f"{lexicon_count:,}"
        SERVER_STATS['indexedTerms'] = f"{total_indexed_terms:,}"
        SERVER_STATS['avgDocLength'] = f"{avg_doc_len:,}"
        
        print(f"Stats calculation complete: {doc_count:,} docs, {lexicon_count:,} lexicon, {total_indexed_terms:,} terms")

    except Exception as e:
        print(f"Stats Error: {e}")

# Run pre-calculation immediately
precalculate_stats()


# --- HELPER: Parse Document ---
def _parse_document(doc_id):
    """Looks up patent metadata from the in-memory CSV dictionary."""
    meta = PATENT_METADATA.get(doc_id)
    if not meta:
        return None

    abstract = meta.get('abstract', 'No abstract available.')
    snippet = (abstract[:280] + '...') if len(abstract) > 280 else abstract

    return {
        'id': doc_id,
        'title': meta.get('title', f'Patent {doc_id}'),
        'snippet': snippet,
        'assignees': meta.get('assignees', 'Unknown'),
        'cpc': meta.get('cpc_codes', 'N/A'),
        'ipc': meta.get('ipc_codes', 'N/A'),
        'date': meta.get('publication_date', 'N/A'),
        'inventors': meta.get('inventors', 'N/A'),
        'filing_date': meta.get('filing_date', 'N/A'),
    }

# --- API Routes ---

@app.route('/api/stats')
def api_stats():
    """Returns the pre-calculated statistics instantly."""
    return jsonify(SERVER_STATS)

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    if not ENGINE or not query:
        return jsonify([])

    tokens = clean_and_tokenize_text(query)
    ranked_results = ENGINE.ranked_search(tokens) 

    final_results = []
    for doc_id, score in ranked_results[:20]: 
        doc_meta = _parse_document(doc_id)
        if doc_meta:
            final_results.append({
                'id': doc_meta['id'],
                'title': doc_meta['title'],
                'snippet': doc_meta['snippet'],
                'score': round(float(score), 1),
                'assignees': doc_meta['assignees'],
                'cpc':  doc_meta['cpc'],
                'ipc':  doc_meta['ipc'],
                'date':  doc_meta['date'],
                'inventors': doc_meta.get('inventors', 'N/A'),
                'filing_date': doc_meta.get('filing_date', 'N/A'),
            })
        else:
            final_results.append({
                'id': doc_id,
                'title': f"Patent {doc_id}",
                'snippet': "Metadata not found in dataset.",
                'score': round(float(score), 1),
                'assignees': 'N/A',
                'cpc': 'N/A',
                'ipc': 'N/A',
                'date': 'N/A',
                'inventors': 'N/A',
                'filing_date': 'N/A',
            })

    return jsonify(final_results)

@app.route('/api/patent/<path:patent_id>')
def api_patent_detail(patent_id):
    """Returns full metadata for a single patent (used by the detail popup)."""
    meta = PATENT_METADATA.get(patent_id)
    if not meta:
        return jsonify({"error": "Patent not found"}), 404
    return jsonify({
        'id': patent_id,
        'title': meta.get('title', 'N/A'),
        'abstract': meta.get('abstract', 'No abstract available.'),
        'assignees': meta.get('assignees', 'Unknown'),
        'inventors': meta.get('inventors', 'N/A'),
        'cpc': meta.get('cpc_codes', 'N/A'),
        'ipc': meta.get('ipc_codes', 'N/A'),
        'publication_date': meta.get('publication_date', 'N/A'),
        'filing_date': meta.get('filing_date', 'N/A'),
    })

@app.route('/api/health')
def api_health():
    """Simple health check without extra messages."""
    return jsonify({
        'engineAvailable': ENGINE is not None,
        'autocompleteAvailable': AUTOCOMPLETE is not None
    })

@app.route('/api/autocomplete')
def api_autocomplete():
    q = request.args.get('q', '')
    if not q or not AUTOCOMPLETE:
        return jsonify([])

    if q.endswith(' '):
        return jsonify([])

    parts = q.split(' ')
    last_word_prefix = parts[-1]
    
    prefix_context = " ".join(parts[:-1])
    if prefix_context:
        prefix_context += " " 

    suggestions = AUTOCOMPLETE.search(last_word_prefix)
    
    final_suggestions = []
    for word in suggestions:
        full_phrase = prefix_context + word
        final_suggestions.append(full_phrase)
        
    return jsonify(final_suggestions[:10])

# --- NEW: Upload Endpoint for Document Addition ---
@app.route('/api/upload', methods=['POST'])
def upload_endpoint():
    if not ENGINE:
        return jsonify({"status": "error", "message": "Engine not loaded"}), 500
        
    data = request.json
    doc_id = data.get('id', '').strip()
    title = data.get('title', '').strip()
    abstract = data.get('abstract', '').strip()
    assignees = data.get('assignees', 'Unknown').strip()
    cpc = data.get('cpc', 'N/A').strip()
    ipc = data.get('ipc', 'N/A').strip()
    pub_date = data.get('publicationDate', 'N/A').strip()
    keywords = data.get('keywords', '').strip()
    
    if not doc_id or not title:
        return jsonify({"status": "error", "message": "Missing ID or Title"}), 400

    # 1. PERSIST TO CSV SYNCHRONOUSLY — guaranteed to complete before response
    #    This ensures the doc metadata survives server restarts.
    try:
        with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                doc_id, title, abstract,
                'N/A',                        # filing_date
                pub_date or 'N/A',            # publication_date
                cpc or 'N/A',                 # cpc_codes
                ipc or 'N/A',                 # ipc_codes
                'N/A',                        # inventors
                assignees or 'Unknown'        # assignees
            ])
    except Exception as e:
        print(f"Error appending to CSV: {e}")
        return jsonify({"status": "error", "message": f"Failed to save: {e}"}), 500

    # 2. UPDATE IN-MEMORY METADATA — so the doc shows up with full details immediately
    PATENT_METADATA[doc_id] = {
        'title': title,
        'abstract': abstract,
        'filing_date': 'N/A',
        'publication_date': pub_date or 'N/A',
        'cpc_codes': cpc or 'N/A',
        'ipc_codes': ipc or 'N/A',
        'inventors': 'N/A',
        'assignees': assignees or 'Unknown',
    }

    # 3. INDEX IN BACKGROUND — adds to dynamic_index for immediate search
    def worker():
        ENGINE.add_document(
            doc_id, title, abstract,
            publication_date=pub_date or "Not Available",
            cpc_codes=cpc or "Unassigned",
            ipc_codes=ipc or "Unassigned",
            asisgnees=assignees or "Unknown"
        )
        
    thread = threading.Thread(target=worker)
    thread.start()
    
    return jsonify({"status": "success", "message": f"Document '{doc_id}' indexed successfully."})

# --- Static File Serving ---

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('js', filename)

@app.route('/styles/<path:filename>')
def serve_styles(filename):
    return send_from_directory('styles', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)