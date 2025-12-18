#Calling our clean and tokenize funcion from the lexicon file in order to match the results so that the lookup from the lexicon can return the results. If we use raw query words we would never be able to get the results. Thats why we have used our tokenizer from lexicon here to tokenize the query words.
from lexicon import clean_and_tokenize_text
#Importing gensim library for the semantic model we previously trained on our data set for the semantic search. Not only depending upon the word-match only but also the semantics search for better results against the query.
import gensim
#Operating system for file existance checks 
import os
#We have enclosed all of our logic inside OOP structure because we need huge data structures to be loaded in the ram like our semantic model , lexicon file. We need it to be loaded only once when the search engine starts.Thats why we have used OOP architecture for this purpose.

from autoComplete import AutoCompleteSystem

import msvcrt 

class SearchEngine:
    #The initializer which runs automatically when the instance of the object is created. Inside this we are loading our lexicon and our semantic model in our RAM for faster access and results.
    def __init__(self):
        print("Making the engine ready for query...")
        print("Loading lexicon...")
        self.lexicon = self.__load_lexicon()
        print("Loading the semantic model...")
        self.model = self.__load_semantic_model()
        self.autocomplete = AutoCompleteSystem()
        print("Search Engine is Ready! Enter your query")
    
    #Load lexicon function . Simply checks for lexicon file to be exist in our directory. If exists simply load lexicon into a dictionary in which word ID's are mapped against the words. It returns a dictionary which is stored in RAM.
    def __load_lexicon(self):
        lexicon_dictionary = {}
        lexicon_path = "lexicon.txt"

        if not os.path.exists(lexicon_path):
            print(f"Error : {lexicon_path} not found!")
            return {}
        
        #Open the lexicon file , iterates over each line in the lexicon file and splits it into word ID and word itself and stores in the dictionary.
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
    

    #Function for loading the semantic model into RAM by checking its existance in the project directory.We load this model by simply using word2vecotr model load function. This model has the semantic logic for our dataset and this model has been specifically trained for our data set.
    def __load_semantic_model(self):
        MODEL_PATH = "word2vec-google-patents-dataset.model"

        if not os.path.exists(MODEL_PATH):
            print(f"Caution! The model not found. Only query-words based results would be returned!")
            return None
        else:
            print("Smeantic Model loaded successfully!")
            return gensim.models.Word2Vec.load(MODEL_PATH)
        

    #Helper function that returns the word ID by taking the word as argument and checks it in the dictionary . If word not exists simply return None which would be handled in the next logics.
    def __get_word_id_from_lexicon(self , word):
        
        word_ID = self.lexicon.get(word)

        if word_ID is None:
            print("No results found!")
            return None 
        
        return word_ID
    
    #This is the cruical function for our search logic. Based on the word ID we first check for the specific barrel by checking the range of the wordID. Then simply go to that barrel and return the document conatining that word alongwith their frequencies in the documents.
    def barrel_lookup(self , word_ID):
        #The function originally returns a dictionary for a specific word containing the document name mapped against the frequency of that word in that document.
        documet_frequency_map = {}

        #Calculating the correct barrel file depending upon the word ID. Using the same logic used in the barrles generator
        barrel_ID = word_ID % 10
        #Barrel filename format
        barrel_filename = f"barrel_{barrel_ID}.txt"
        #Overall path of the specific barrel joined
        barrel_path = os.path.join("barrels" , barrel_filename)

        #Existance check for the barrel file if not found simply return an empty dictionary
        if not os.path.exists(barrel_path):
            print(f"Error : Barrel not found!")
            return {}
        
        #Since barrel file is too large we want to go through the specific word ID and all the documents against it. We set current word id to -1 and create a boolean found target block false which we will set to true after finding the specific block. We do not want to add the unrelated results in the final results. Since each block can be multi lined and we can only iterate through the document line by line so in order to have a single block to store the documents we ar doing all this logic.
        current_word_id = -1
        found_target_block = False

        #We open that specific barrel file 
        with open(barrel_path , "r" , encoding="utf-8") as file:
            #Iterate line by line for valid line
            for line in file:
                line = line.strip()
                if not line :
                    continue

                #Split the line into two parts based on the separator ':' which would only exist in the first line of the block in this way we would indentify the start of the block and when again another line would come like this we would know new block has been started and we would simply break through the loop
                parts = line.split(" : " , 1)
                string_to_parse = ""

                #If length of the parts is two which means line divided successfully it means it indicates start of the block and the first part starts with digit which means the word ID 
                if len(parts) == 2 and parts[0].isdigit():
                    #We store the first part in the current word id variable and when this variable changes we exit from the loop
                    current_word_id = int(parts[0])
                    #String to parse is the second part which contains all the documents of that specific word.
                    string_to_parse = parts[1]

                    #If target block is already found and the current word id does not matches the word_ID we are looking for it means we have encountreed the next block so we simply exit from the loop.
                    if found_target_block and current_word_id != word_ID:
                        break

                    #And this logic keeps a check wether the block found or not and if found set to true so that we can break from the loop rather than keep iterating over the barrel.
                    if current_word_id == word_ID:
                        found_target_block = True
                
                #If its the continuation line not the first line of the block and found target block is set to true so we pass the entire line to be parsed since it would contain all the documents related to that word.
                else:
                    if found_target_block:
                        string_to_parse = line
                    else:
                        continue
                
                #Here we added another safety check so that we make sure the word id in the current iteration matches our required word id
                if current_word_id == word_ID: 
                    #Take the indiviual docuemnts in the line which are separated with columns . Name them as entries because each entry contains both the document name and the frequency against that. We also need to separate the frequency for page rank logic afterwards.
                    entries = [e.strip() for e in string_to_parse.split(",")] 

                    #Iterate over the entries remove extra spaces 
                    for entry in entries:
                        entry = entry.strip()
                        if not entry : 
                            continue

                        #Now if we split from the right side till the first space occurs we get the frequecny of that word in each document and store both parts in document data variable 
                        document_data = entry.rsplit(" " , 1)

                        #If the number of parts is not 2 it means frequency not found so we simply continue to prevent crash and bad results
                        if len(document_data) != 2 :
                            continue

                        #Otherwise store the first part as the document id 
                        document_ID = document_data[0]
                        
                        #We are enclosing the frequecny logic in try block it is possible that the second part we got might not be a number so this is exceptional case and would cause program to crash and abort apruptly due to datatype mismatch
                        try:
                            #Storing the second part as frequency by storing it in the the form of int from string
                            frequency = int(document_data[1])
                            #Now map the document ID and frequency in our dictionary 
                            documet_frequency_map[document_ID] = frequency
                        except ValueError:
                            continue
        
        #At the end of the function simply return the dictionary 
        return documet_frequency_map
    

    #Helper function for semantic search . It basically looks for the top related words semantically and expnads the query by also returning results for the semantically suggested words.
    def expand_query_with_semantics(self , word):
        #If model not available simply return null list no semantic search only word to word match 
        if not self.model : return []

        try:
            #Get the top 10 suggestions from the model
            raw_suggestions = self.model.wv.most_similar(word , topn=10)
            valid_suggestions = []

            #Check wether these suggestions exist in lexicon or not if yes simply return the top 3 valis suggestions which include the words that are available in the lexicon
            for suggestion , score in raw_suggestions:
                if suggestion in self.lexicon:
                    valid_suggestions.append((suggestion , score))

            #We return the top 3 suggested words to expand the query
            return valid_suggestions[:3]
        except KeyError:
            return []
        
    
    #Here what the heart of our search logic lies . It takes the tokens as the arguments 
    def ranked_search(self , tokens):
        #Define a ductionary for final scores and document token matches this would help in the ranking logic which would be implemented later in this function
        final_scores = {}
        document_token_matches = {}
        
        #For the exact results we are having a weight factor of 1.0 and for the suggested words we are having a weight of 0.4 to rank these results differently from the original query words
        EXACT_WEIGHT = 1.0
        SUGGESTIONS_WEIGHT = 0.4

        #Total number of query tokens (used later for coverage based scoring)
        total_query_tokens = len(tokens)

        import math  #IMPROVEMENT: required for log based frequency scaling

        #For each token in our query
        for token in tokens:
            #Get the word id from the lexicon which is loaded in our ram
            word_ID = self.__get_word_id_from_lexicon(token)
            #If a valid word ID is returnd check for the barrel lookup
            if word_ID is not None:
                #exact documents stored 
                exact_matched_documents = self.barrel_lookup(word_ID)

                #The variable contains document id and the frequency which are in the form of dictionary mapped to each other
                for document_id , frequency in exact_matched_documents.items():

                    #If the document id is not present in our final scores dictionary simply initialize that word docuemnt with score 0.0
                    if document_id not in final_scores:
                        final_scores[document_id] = 0.0
                        #In the second dictionary which contains the words matched set (so that it stores unique words) from the query against the document ID we create a set against each document
                        document_token_matches[document_id] = set()

                    #Using log scaled frequency instead of raw frequency to avoid domination of high frequency terms
                    scaled_frequency = math.log(1 + int(frequency))

                    #We add the score for each document
                    final_scores[document_id] += (scaled_frequency * EXACT_WEIGHT)

                    #We also add the tokens found in the list against the document
                    document_token_matches[document_id].add(token)

            
            #The above logic we do all same for the semantic words just the socre is calculated by product of frequency , weight we gave to it and cosine weight from the model
            suggestions = self.expand_query_with_semantics(token)

            
            for suggestion , score in suggestions:
                suggestion_word_id = self.__get_word_id_from_lexicon(suggestion)
                if suggestion_word_id is not None:
                    suggestion_documents = self.barrel_lookup(suggestion_word_id)

                    for suggested_document_id , frequency in suggestion_documents.items():

                        if suggested_document_id not in final_scores:
                            final_scores[suggested_document_id] = 0.0
                            document_token_matches[suggested_document_id] = set()

                        #Log scaled frequency for semantic matches as well
                        scaled_frequency = math.log(1 + int(frequency))

                        final_scores[suggested_document_id] += (scaled_frequency * score * SUGGESTIONS_WEIGHT)
                        document_token_matches[suggested_document_id].add(token)

        #This logic ranks the documents first based upon the number of matched keywords from the query and then the frequecy score .
        ranking_data = []
        for document_id , score in final_scores.items():
            words_matched = len(document_token_matches[document_id])

            # Keyword coverage factor (documents matching more query tokens are rewarded)
            coverage_factor = words_matched / total_query_tokens

            #Adjusting the score using coverage factor
            adjusted_score = score * coverage_factor

            ranking_data.append((document_id , words_matched , adjusted_score))

        #We sort the data first based on number of matchd keywords and then the score and reverse means in descending order 
        ranking_data.sort(key= lambda x: (x[1] , x[2]) , reverse=True)

        #This is the final result list which we would be returning.
        final_results = []

        #Better normalization using min-max scaling instead of max only
        if ranking_data:
            
            scores = [item[2] for item in ranking_data]
            min_score = min(scores)
            max_score = max(scores)

            score_range = max_score - min_score
            if score_range == 0:
                score_range = 1

            for document_id , _ , score in ranking_data:
                percentage = ((score - min_score) / score_range) * 100
                percentage = min(max(percentage , 0.0) , 100.0)
                final_results.append((document_id , percentage))

        return final_results


    #simply tokenize the query with our function and call the search logic for it . Rest is just formatting and testing purposes. All this would be taken over by th front end.
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

    #Temporary function import for testing in CLI 
    def get_autocomplete_suggestions(self, full_query):
     
        #Handle empty input
        if not full_query: return []

        #Split the query to find the last word being typed

        parts = full_query.split(" ")
        
        #The word currently being typed
        last_word_prefix = parts[-1]
        
       
        prefix_context = " ".join(parts[:-1])
        if prefix_context: 
            prefix_context += " "

        if not last_word_prefix:
            return [] 
            
        suggestions = self.autocomplete.search(last_word_prefix)
        
        final_suggestions = []
        for word in suggestions:
    
            full_phrase = prefix_context + word
            final_suggestions.append(full_phrase)
            
        return final_suggestions

#Temporary testing logic in the CLI for search suggestions actual implementation in the web page 
if __name__ == "__main__":
    engine = SearchEngine()
    
    print("REAL-TIME SEARCH (Type below). Press ENTER to search, ESC to exit.")
    current_query = ""

    while True:
        os.system('cls') # Clear screen
        print(f"SEARCH > {current_query}")
        print("-" * 30)

       
        if current_query:
            suggestions = engine.get_autocomplete_suggestions(current_query)
            for i, word in enumerate(suggestions):
                print(f"   {i+1}. {word}")
        
       
        key = msvcrt.getch()

        if key == b'\r': # Enter
            print("\nSearching...")
            engine.search(current_query)
            input("\nPress Enter to continue...")
            current_query = ""
        elif key == b'\x08': # Backspace
            current_query = current_query[:-1]
        elif key == b'\x1b': # ESC
            break
        else:
            try:
                current_query += key.decode('utf-8')
            except: pass

