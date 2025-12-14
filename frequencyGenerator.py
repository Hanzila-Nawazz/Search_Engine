#This is a helper function for my auto complete script. We could have just simply implemented the auto complete based on the alphabetic vocabulary and the suggestions would have been appeared in the alphabetical order but it does not fullfill (according to me) the actual purpose of the auto complete which based on the freq presents the suggestions not merely the vocab.

#Since we had no explicit source for the freq of each word and if we would have tried to implement the changes for having freq for each word of lexicon within the lexicon would have caused us a huge cost for changes in many of our code so we generated simply another .txt file which has freq of each word against the word itself.
import os

#Path and directories 
LEXICON_PATH = "lexicon.txt"
BARRELS_DIR = "barrels"
OUTPUT_FILE = "word_frequency.txt"

#Loading the lexicon 
def load_lexicon():

    print("Loading Lexicon...")
    lexicon_dictionary = {}

    if not os.path.exists(LEXICON_PATH):
        print("Error: Lexicon not found!")
        return {}

    with open(LEXICON_PATH, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split(" : ")

            if len(parts) == 2:
                lexicon_dictionary[int(parts[0])] = parts[1]

    return lexicon_dictionary

#Generating the frequency of each word through barrels going through each barrel one by one and adding all the frequencies against each document to be mapped to a single word and then writing it in another .txt file 
def generate_frequency():

    id_to_word = load_lexicon()
    
    if not id_to_word:
        return

    word_frequencies = {} 

    print("Scanning Barrels for frequencies...")
    

    if not os.path.exists(BARRELS_DIR):
        print(f"Error: {BARRELS_DIR} directory not found.")
        return

    
    barrel_files = [f for f in os.listdir(BARRELS_DIR) if f.startswith("barrel_")]
    
    for b_file in barrel_files:
        path = os.path.join(BARRELS_DIR, b_file)
        print(f"Processing {b_file}...")
        
        with open(path, "r", encoding="utf-8") as file:
            for line in file:

                parts = line.strip().split(" : ")
                if len(parts) < 2: continue
                
                word_id_string = parts[0]
                data_string = parts[1]
                
                if not word_id_string.isdigit(): continue
                word_id = int(word_id_string)
                
                word = id_to_word.get(word_id)
                if not word: continue
                
                total_freq = 0
                entries = data_string.split(",")
                for entry in entries:
    
                    doc_data = entry.strip().rsplit(" ", 1)

                    if len(doc_data) == 2:
                        try:
                            total_freq += int(doc_data[1])
                        except ValueError:
                            pass
                
                word_frequencies[word] = total_freq


    print(f"Saving {len(word_frequencies)} words to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        
        for word, freq in word_frequencies.items():
            f.write(f"{word} : {freq}\n")
            
    print("Done! You can now run the Autocomplete system.")

if __name__ == "__main__":
    generate_frequency()