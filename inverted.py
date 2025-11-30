import traceback
import os

def build_inverted_index():
    inverted_index = {}

    

    try:
        with open("forward_index.txt", "r", encoding="utf-8") as f:
            check = 0 
            check_in_tens = 1
            for line in f:
                check = check +1
                line = line.strip()
                if not line:
                    continue

                # Example line:
                # US-2015000659-A1 : 53360 1, 91317 1, 64866 2
                try:
                    pub_no, rest = line.split(" : ")
                except ValueError:
                    print("Skipping malformed line:", line)
                    continue

                # Each pair looks like "53360 1"
                pairs = rest.split(",")

                for pair in pairs:
                    pair = pair.strip()
                    if not pair:
                        continue

                    try:
                        word_id_str, freq_str = pair.split()
                        word_id = int(word_id_str)
                        freq = int(freq_str)
                    except ValueError:
                        print("Skipping malformed pair:", pair)
                        continue

                    # Add to inverted index
                    if word_id not in inverted_index:
                        inverted_index[word_id] = []

                    # append (pub_no, frequency)
                    inverted_index[word_id].append((pub_no, freq))
                

        # Validate that we built a non-empty index
        if not inverted_index:
            print("Warning: Inverted index is empty. Check if forward_index.txt contains data.")
            return

        # Sort inverted index by word_id
        sorted_word_ids = sorted(inverted_index.keys())

        # Write to file in your preferred format (txt)
        with open("inverted_index.txt", "w", encoding="utf-8") as out:
            for word_id in sorted_word_ids:
                postings = inverted_index[word_id]

                # Format:  ID : pub_no freq, pub_no freq, ...
                postings_str = ", ".join([f"{pub} {freq}" for pub, freq in postings])
                out.write(f"{word_id} : {postings_str}\n")

        # Print summary statistics
        total_postings = sum(len(postings) for postings in inverted_index.values())
        print(f"\nInverted index successfully saved to inverted_index.txt")
        print(f"  - Total unique words (lexicon entries): {len(inverted_index)}")
        print(f"  - Total postings (word, doc) pairs: {total_postings}")

    except Exception:
        print("An error occurred while building the inverted index.")
        traceback.print_exc()



# -----------------------------
# Run the builder
# -----------------------------
build_inverted_index()
