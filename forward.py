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


