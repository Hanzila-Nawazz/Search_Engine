from lexicon import clean_and_tokenize_text
import os
class SearchEngine:
    def __init__(self):
        print("Making the engine ready for query...")
        self.lexicon = self.__load_lexicon()
        print("Search Engine is Ready! Enter your query")
    
    def __load_lexicon(self):
        lexicon_dictionary = {}
        lexicon_path = "lexicon.txt"

        if not os.path.exists(lexicon_path):
            print(f"Error : {lexicon_path} not found!")
            return {}
        
        with open(lexicon_path,"r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(" : ",1)
                if len(parts) == 2:
                    word_id_string = parts[0]
                    word = parts[1]
                    lexicon_dictionary[word] = int(word_id_string)
        print("Lexicon loaded successfully!")
        return lexicon_dictionary
    
    def single_word_search(self , string):
        tokens = clean_and_tokenize_text(string)
        if len(tokens) == 1:
            word = tokens[0]
            word_ID = self.lexicon.get(word)
            if word_ID is None:
                print("No results found!")
                return
            else:
                barrel_ID = word_ID % 10
                barrel_filename = f"barrel_{barrel_ID}.txt"
                barrel_path = os.path.join("barrels" , barrel_filename)
                
                with open(barrel_path , "r" , encoding="utf-8") as file:
                    for line in file:
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split(" : ")
                        if len(parts) == 2:
                            current_word_id = parts[0]
                            list_of_docs_string = parts[1]


                            if current_word_id == word_ID:
                                doc_ids = []
                                entries = list_of_docs_string.split(" , ")

                                for entry in entries:
                                    document_data = entry.rsplit(" " , 1)
                                    if len(document_data == 2):
                                        doc_ids.append()

instance1 = SearchEngine()