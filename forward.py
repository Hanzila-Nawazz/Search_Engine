import pandas as pd
import gc
import os
import traceback
from collections import Counter

# Reuse your existing clean & tokenize function
from lexicon import clean_and_tokenize_text


def load_lexicon():
    lexicon_dictionary = {}
    with open("lexicon.txt", "r", encoding="utf-8") as f:
        for line in f:
            try:
                # tolerate variations in the separator and extra spaces
                parts = line.strip().split(":", 1)
                if len(parts) != 2:
                    continue
                word_id = parts[0].strip()
                word = parts[1].strip()
                # if the file format was `id : word`, parts[1] may start with the word; handle both
                # drop any leading colon or separators
                if word.startswith(":"):
                    word = word.lstrip(": ")
                lexicon_dictionary[word] = int(word_id)
            except:
                continue
    return lexicon_dictionary


def forward_index_generator():
    print("\nLoading lexicon...")
    lexicon_dictionary = load_lexicon()
    print(f"Loaded {len(lexicon_dictionary)} lexicon entries.\n")

    CHUNK_SIZE = 10000
    csv_file_path = "patents_dataset.csv"

    if not os.path.exists(csv_file_path):
        print("Dataset not found!")
        return

    print("Creating forward index...\n")

    columns_to_use = ["publication_number", "title", "abstract"]

    chunk_iterator = pd.read_csv(csv_file_path,
                                 usecols=columns_to_use,
                                 chunksize=CHUNK_SIZE)

    with open("forward_index.txt", "w", encoding="utf-8") as out:

        for chunk_index, df in enumerate(chunk_iterator):
            df = df.fillna("")

            # Combine the text per patent
            df["text"] = df["title"].astype(str) + " " + df["abstract"].astype(str)

            for _, row in df.iterrows():
                try:
                    pub_no = row["publication_number"]
                    text = row["text"]

                    # skip empty or invalid publication numbers
                    if pub_no is None or (isinstance(pub_no, float) and pd.isna(pub_no)) or str(pub_no).strip() == "":
                        continue

                    tokens = clean_and_tokenize_text(text)

                    # count tokens first, then map to word_ids to avoid creating large intermediate lists
                    token_counts = Counter(tokens)
                    freq_map = {lexicon_dictionary[w]: c for w, c in token_counts.items() if w in lexicon_dictionary}

                    # skip patents that have no lexicon words
                    if not freq_map:
                        continue

                    # format: pub_no : word_id freq , word_id freq , ...
                    parts = [f"{wid} {cnt}" for wid, cnt in freq_map.items()]
                    out.write(f"{pub_no} : {', '.join(parts)}\n")
                except Exception:
                    # don't let one bad row stop the entire run
                    traceback.print_exc()
                    continue

            print(f"Processed chunk {chunk_index+1}")

            del df
            gc.collect()

    print("Forward index successfully written to forward_index.txt")

forward_index_generator()
