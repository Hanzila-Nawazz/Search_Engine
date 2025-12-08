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
    
    def __get_word_id_from_lexicon(self , string):
        tokens = clean_and_tokenize_text(string)

        if len(tokens) != 1 : 
            print("Single word queries allowed for searching the corresponding word id.")
            return None 

        word = tokens[0]
        word_ID = self.lexicon.get(word)

        if word_ID is None:
            print("No results found!")
            return None 
        
        return word_ID


    def single_word_search(self , string):
        
        documet_frequency_map = {}

        word_ID = self.__get_word_id_from_lexicon(string)

        if word_ID is None:
            return {}
        
        barrel_ID = word_ID % 10
        barrel_filename = f"barrel_{barrel_ID}.txt"
        barrel_path = os.path.join("barrels" , barrel_filename)

        if not os.path.exists(barrel_path):
            print(f"Error : Barrel not found!")
            return 

        current_word_id = -1
        found_target_block = False


        with open(barrel_path , "r" , encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line :
                    continue

                parts = line.split(" : " , 1)
                string_to_parse = ""

                if len(parts) == 2 and parts[0].isdigit():
                    current_word_id = int(parts[0])
                    string_to_parse = parts[1]

                    if found_target_block and current_word_id != word_ID:
                        break

                    if current_word_id == word_ID:
                        found_target_block = True
                
                else:
                    if found_target_block:
                        string_to_parse = line
                    else:
                        continue
                
                if current_word_id == word_ID: 
                    entries = [e.strip() for e in string_to_parse.split(",")] 

                    for entry in entries:
                        entry = entry.strip()
                        if not entry : 
                            continue

                        document_data = entry.rsplit(" " , 1)

                        if len(document_data) != 2 :
                            continue

                        document_ID = document_data[0]
                        
                        try:
                            frequency = int(document_data[1])
                            documet_frequency_map[document_ID] = frequency
                        except ValueError:
                            continue

        if documet_frequency_map:
            print(f"Results returned from the barrels :  {len(documet_frequency_map)} documents returned!") 
            return documet_frequency_map
        else:
            print(f"Word found in lexicon but no documents in the barrel.") 
            return {}

                        
instance1 = SearchEngine()
while(True) : 
    string = input("Enter the single word you want to search for and enter no if exit: ")
    if string == "exit":
        break
    instance1.single_word_search(string)
