from lexicon import clean_and_tokenize_text
import gensim
import traceback
import os
class SearchEngine:
    def __init__(self):
        print("Making the engine ready for query...")
        print("Loading lexicon...")
        self.lexicon = self.__load_lexicon()
        print("Loading the semantic model...")
        self.model = self.__load_semantic_model()
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
    

    def __load_semantic_model(self):
        MODEL_PATH = "word2vec-google-patents-dataset.model"

        if not os.path.exists(MODEL_PATH):
            print(f"Caution! The model not found. Only query-words based results would be returned!")
            return None
        else:
            print("Smeantic Model loaded successfully!")
            return gensim.models.Word2Vec.load(MODEL_PATH)
        

    def __get_word_id_from_lexicon(self , word):
        
        word_ID = self.lexicon.get(word)

        if word_ID is None:
            print("No results found!")
            return None 
        
        return word_ID
    
    def barrel_lookup(self , word_ID):

        documet_frequency_map = {}

        barrel_ID = word_ID % 10
        barrel_filename = f"barrel_{barrel_ID}.txt"
        barrel_path = os.path.join("barrels" , barrel_filename)

        if not os.path.exists(barrel_path):
            print(f"Error : Barrel not found!")
            return {}

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
        
        return documet_frequency_map
    
    def expand_query_with_semantics(self , word):
        if not self.model : return []

        try:
            raw_suggestions = self.model.wv.most_similar(word , topn=10)
            valid_suggestions = []

            for suggestion , score in raw_suggestions:
                if suggestion in self.lexicon:
                    valid_suggestions.append((suggestion , score))

            
            return valid_suggestions[:3]
        except KeyError:
            return []
        
    
    def normal_scores_scale_of_100(self , raw_scores):
        if not raw_scores : return []

        max_score = max(raw_scores.values())
        if max_score == 0: return []

        final_scores = []

        for document_id , scores in raw_scores.items():

            percentage = (scores/max_score) * 100

            if percentage > 10:
                final_scores.append((document_id , percentage))

        
        final_scores.sort(key=lambda x : x[1] , reverse=True)

        return final_scores



    def ranked_search(self , tokens):
        final_scores = {}

        EXACT_WEIGHT = 1.0
        SUGGESTIONS_WEIGHT = 0.4

        for token in tokens:
            word_ID = self.__get_word_id_from_lexicon(token)
            if word_ID is not None:
                exact_matched_documents = self.barrel_lookup(word_ID)

                for document_id , frequency in exact_matched_documents.items():

                    if document_id not in final_scores:
                        final_scores[document_id] = 0.0

                    final_scores[document_id] += (int(frequency) * EXACT_WEIGHT)

            
            suggestions = self.expand_query_with_semantics(token)

            
            for suggestion , score in suggestions:
                suggestion_word_id = self.__get_word_id_from_lexicon(suggestion)
                if suggestion_word_id is not None:
                    suggestion_documents = self.barrel_lookup(suggestion_word_id)

                    for suggested_document_id , frequency in suggestion_documents.items():

                        if suggested_document_id not in final_scores:
                            final_scores[document_id] = 0.0

                        final_scores[document_id] += (int(frequency) * score * SUGGESTIONS_WEIGHT)

        return self.normal_scores_scale_of_100(final_scores)


    def search(self, string):
        tokens = clean_and_tokenize_text(string)

        if not tokens:
            print("Please enter a valid query.")
            return
        
        ranked_documents = self.ranked_search(tokens)
        
        if not ranked_documents:
            print("No matching documents found.")

        else:
            print(f"Found {len(ranked_documents)} documents.")
            print("-" * 40)
            print(f"{'RANK':<5} | {'DOC ID':<15} | {'RELEVANCE'}")
            print("-" * 40)
            
            for i, (document_id, score) in enumerate(ranked_documents[:10]):
                print(f"#{i+1:<4} | {document_id:<15} | {score:.1f}%")
            print("-" * 40)


if __name__ == "__main__":
    instance1 = SearchEngine()
    
    while True:
        query_string = input("Enter a string to search: ")
        if query_string.lower() == "exit":
            break
        instance1.search(query_string)

