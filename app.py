import atexit
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

# Global Stats Cache
SERVER_STATS = {
    'documents': 0,
    'lexiconSize': 0,
    'indexedTerms': 0,
    'avgDocLength': 0
}

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
        # 1. Document Count
        if os.path.exists(DATA_DIR):
            files = [f for f in os.listdir(DATA_DIR) if f.endswith('.txt')]
            doc_count = len(files)
            
            # 2. Token Stats (Sum file sizes)
            total_size_bytes = sum(os.path.getsize(os.path.join(DATA_DIR, f)) for f in files)
            total_indexed_terms = total_size_bytes // 6
            avg_doc_len = (total_indexed_terms // doc_count) if doc_count > 0 else 0
        else:
            doc_count = 0
            total_indexed_terms = 0
            avg_doc_len = 0

        # 3. Lexicon Size
        lexicon_count = len(ENGINE.lexicon) if ENGINE else 0

        # Save to global cache
        SERVER_STATS['documents'] = f"{doc_count:,}"
        SERVER_STATS['lexiconSize'] = f"{lexicon_count:,}"
        SERVER_STATS['indexedTerms'] = f"{total_indexed_terms:,}"
        SERVER_STATS['avgDocLength'] = f"{avg_doc_len:,}"
        
        print("Stats calculation complete.")

    except Exception as e:
        print(f"Stats Error: {e}")

# Run pre-calculation immediately
precalculate_stats()


# --- HELPER: Parse Document ---
def _parse_document(doc_id):
    """Extracted updated patent details for the modern UI."""
    filename = f"{doc_id}.txt" if not str(doc_id).endswith('.txt') else doc_id
    path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(path):
        return None

    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            def get_field(tag, default="N/A"):
                match = re.search(rf"\[{tag}\]\s*([\s\S]*?)\n\n", content)
                return match.group(1).strip() if match else default

            title = get_field("TITLE", f"Patent {doc_id}")
            abstract = get_field("ABSTRACT", "No abstract available.")
            assignees = get_field("ASSIGNEES", "Unknown Assignee")
            cpc = get_field("CPC_CODES", "N/A")
            ipc = get_field("IPC_CODES", "N/A")
            date = get_field("DATE", "Dec 19, 2025")

            snippet = (abstract[:280] + '...') if len(abstract) > 280 else abstract

            return {
                'id': doc_id,
                'title': title,
                'snippet': snippet,
                'assignees': assignees,
                'cpc': cpc,
                'ipc': ipc,
                'date': date
            }
    except Exception:
        return None

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
                'date':  doc_meta['date']
            })
        else:
            final_results.append({
                'id': doc_id,
                'title': f"Patent {doc_id}",
                'snippet': "Document content file not found.",
                'score': round(float(score), 1)
            })

    return jsonify(final_results)

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
    doc_id = data.get('id')
    title = data.get('title')
    abstract = data.get('abstract')
    
    if not doc_id or not title:
        return jsonify({"status": "error", "message": "Missing ID or Title"}), 400

    # Run in background thread so UI doesn't freeze
    def worker():
        ENGINE.add_document(doc_id, title, abstract)
        # Optional: Update stats cache after add (simple increment)
        # In a real app, you might want to re-calculate, but incrementing is faster
        pass 
        
    thread = threading.Thread(target=worker)
    thread.start()
    
    return jsonify({"status": "success", "message": "Indexing started..."})

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