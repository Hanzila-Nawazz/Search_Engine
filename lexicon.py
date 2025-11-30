import pandas as pd 
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter
import gc
import os
import traceback

#Importing the defined basic supportive words of english language to not include them in the lexicon using nltk library and also creating an object lemmatizer. Lemmatizer is also a predefined library part of nltk which looks for the adverbs to convert to basic verbs making them root words by using english dictionary. 
stop_words = set(stopwords.words('english'))  
lemmatizer = WordNetLemmatizer()

#Defining a clean and tokenize function which makes all words lowercase then using regular expressions pattern extracting only a-z alphabets , no punctuation no special symbols no numbers then splitting the words into tokens.After that checking for them in the stop words , removing extra spaces and tokens having all same letters , storing the tokens in a list and returning the list.
def clean_and_tokenize_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z]', ' ' , text)
    text = re.sub(r'\s+', ' ', text).strip() 
    tokens = text.split() 
    filtered_tokens = [] 
    for token in tokens: 
        if((token not in stop_words) and (len(token) > 2) and (not token.isdigit()) and (not re.fullmatch(r'(.)\1{2,}' , token))):
            try:
                processed_word = lemmatizer.lemmatize(token)
                processed_word = lemmatizer.lemmatize(processed_word , pos= 'v')
            except Exception:
                # Any error from NLTK (missing data or corrupted files) -> fall back to raw token
                processed_word = token
            filtered_tokens.append(processed_word)
    return filtered_tokens


#Main code cotaining the logic for creating the lexicon
def lexicon_generator():
    print("\nLoading the data set...")
    #Taking only two columns in the lexicon vocab from the data set since these are the only core columns forming the dictionary of the whole lexicon rest would just help in indexing , ranking and cleaning the results in the later stage.
    columns_to_use = ["title" , "abstract"]
    #Since we have a large data set of approx 0.9 million patents so taking them in one go would significantly increase the ram usage and would cause the program to crash so we are dealing it in chunks of 10,000 files/patents.


    #(the reason for taking that large dataset in our case was that we had a dataset having all the core keywords and definition in our title and abstract only. The description would only increase the lookup time and would not significantly contribute to the lexicon because they are more like numerical having details about the patents ownership , dimensions , numerical and methamatical formulae).
    CHUNK_SIZE = 10000

    #Defining a list to temporarily handle the tokens so calculate their frequency and discarding the words having a frequency of 1 since most of them are NOISE so we want to remove them.
    all_tokens = []

    csv_file_path = "patents_dataset.csv"

    #Error handling if the file path casues error in global case.
    if not os.path.exists(csv_file_path):
        print(f"Error: File not found at the path : {csv_file_path}")
        return {}
    
    #Here our core logic lies all in it. We have made an iterator that would simply iteratre over the chunks that we have made for our data. In each iteration it would perform the cleaning task and then it would dump the data from the ram and storing it in the map and lexicon .txt file too.
    chunk_iterator = pd.read_csv(csv_file_path , usecols=columns_to_use , chunksize= CHUNK_SIZE) 

    print("Processing the files in chunks..")

    #Maintaining the counter for the progress bar
    total_processed = 0
    try:
        #For loop handling multiple chunks of data to keep the program running.
        for chunk_index, chunk_dataframe in enumerate(chunk_iterator):
            #Handling the empty data spots
            chunk_dataframe = chunk_dataframe.fillna("") 
            #Combining both the columns so we can simply perform functions on single strings per patent / file.
            chunk_dataframe['text'] = chunk_dataframe['title'].astype(str) + " " + chunk_dataframe['abstract'].astype(str)
            #Applying the cleaning function on each patent set of lexicon and we have many of them.
            chunk_dataframe['tokens'] = chunk_dataframe['text'].apply(clean_and_tokenize_text) 
    
            #Storing the tokens in the vector of each patent 
            for token_list_of_each_patent in chunk_dataframe['tokens']:
                all_tokens.extend(token_list_of_each_patent)
            
            #Maintainig the counter
            total_processed += len(chunk_dataframe)
            print(f"Processing chunk number :  {chunk_index+1} (Toal Documents Processed: {total_processed})")

            #Deleting the processed ones from the ram to reduce the ram consumption as much as possible.
            del chunk_dataframe
            gc.collect()
    
    except KeyboardInterrupt:
        print("User stopped the execution! Exiting!")
    except Exception as e:
        print("An error occured during processing the file!")
        print(f"Exception: {e}")
        traceback.print_exc()

    
    #Creating a counter to count  the frequecy of each word 
    word_frequency = Counter(all_tokens)

    #Keeping only the words having frequency more than one 
    lexicon = set([word for word, freq in word_frequency.items() if freq > 1])

    print(f"Total unique words in lexicon : {len(lexicon)}")
    print("Sorting the lexicon list in the alphabetical order for better indexing...")
    #Sorting the list for better searching algorithm later helping in reduncing the time complexity for the search function.
    sorted_lexicon = sorted(list(lexicon)) 

    #Dfefining the lexcion dictionary which would map the words against their index nmbers would be helping in developing the forward index and the inverted index.
    lexicon_dictionary = {}
    print("Generating and mapping lexicon with correct indices...")
    #Writing in the .txt file 
    with open("lexicon.txt", "w", encoding="utf-8") as f: 

        for word_id, word in enumerate(sorted_lexicon):
            f.write(f"{word_id} : {word}\n")
            lexicon_dictionary[word] = word_id
            
    print("Lexicon file has been successfully generated.")

lexicon_generator()
