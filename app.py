import atexit
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import re

# Import your custom logic
from lexicon import clean_and_tokenize_text
from searcher import SearchEngine
from autoComplete import AutoCompleteSystem

app = Flask(__name__)
CORS(app)

# Paths
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data", "patent_docs")

# --- Initialize Systems ---
print("--- Loading NexaSearch Subsystems ---")
try:
    ENGINE = SearchEngine()
    print("Search Engine: READY")
except Exception as e:
    print(f"Search Engine: FAILED ({e})")
    ENGINE = None

try:
    AUTOCOMPLETE = AutoCompleteSystem()
    print("Autocomplete: READY")
except Exception as e:
    print(f"Autocomplete: FAILED ({e})")
    AUTOCOMPLETE = None

# --- MISSING LOGIC: _parse_document ---
def _parse_document(doc_id):
    """Extracted updated patent details for the modern UI."""
    filename = f"{doc_id}.txt" if not str(doc_id).endswith('.txt') else doc_id
    path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(path):
        return None

    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Extract fields using standard tags in your dataset
            def get_field(tag, default="N/A"):
                match = re.search(rf"\[{tag}\]\s*([\s\S]*?)\n\n", content)
                return match.group(1).strip() if match else default

            title = get_field("TITLE", f"Patent {doc_id}")
            abstract = get_field("ABSTRACT", "No abstract available.")
            assignees = get_field("ASSIGNEES", "Unknown Assignee")
            cpc = get_field("CPC_CODES", "N/A")
            ipc = get_field("IPC_CODES", "N/A")
            date = get_field("DATE", "Dec 19, 2025") # Fallback to current date if missing

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
    """Returns quick count of documents."""
    try:
        doc_count = len([f for f in os.listdir(DATA_DIR) if f.endswith('.txt')])
    except:
        doc_count = 0
    return jsonify({
        'documents': doc_count,
        'lexiconSize': '128k+', # Placeholder or read from lexicon.txt
        'indexedTerms': '892k+', 
        'avgDocLength': '2,847'
    })



@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    if not ENGINE or not query:
        return jsonify([])

    # 1. Process search using your DSA logic
    tokens = clean_and_tokenize_text(query)
    ranked_results = ENGINE.ranked_search(tokens) # Returns list of (doc_id, score)

    # 2. Match IDs to actual file content for the UI
    final_results = []
    for doc_id, score in ranked_results[:20]: # Show top 20
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
            # Fallback if text file is missing but ID is in index
            final_results.append({
                'id': doc_id,
                'title': f"Patent {doc_id}",
                'snippet': "Document content file not found.",
                'score': round(float(score), 1)
            })

    return jsonify(final_results)

@app.route('/api/health')
def api_health():
    """Satisfies the frontend health check to remove the 'Not Found' error."""
    return jsonify({
        # 'ok': True,
        # 'engineAvailable': ENGINE is not None,
        # 'autocompleteAvailable': AUTOCOMPLETE is not None
    })

@app.route('/api/autocomplete')
def api_autocomplete():
    q = request.args.get('q', '')
    if not q or not AUTOCOMPLETE:
        return jsonify([])
    return jsonify(AUTOCOMPLETE.search(q))

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