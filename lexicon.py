import pandas as pd 
import re

WORDS_TO_REMOVE = set(["the", "of", "and", "a", "to", "in", "is", "you", "that", "it", "he", "was", "for", "on","are", "as", "with", "his", "they", "at", "be", "this", "have", "from", "or", "one", "had", "by", "word", "but", "not", "what", "all", "were", "we", "when", "your", "can", "said", "there", "use", "an", "each", "which", "she", "do", "how", "their", "if"])
#So we have created a list of words that are the supporting words and we dont actaully need them in our lexicon dictionary 
def clean_and_tokenize_text(text):
    text = text.lower() #We make all the text in the lower case to have a consistent dictionary and no case difference affects our search results and lexcion generation.
    text = re.sub(r'[^a-z0-9]', ' ' , text) #This line is written and is very cruical.This line uses the regular expressions library and with help of them we are excluding evry charcater other than alphabets and digits and sub function does the task of replacing the charactrs other than alphabets and numbers with the empty strings.
    text = re.sub(r'\s+', ' ', text).strip() #Here extra spaces other than a single space are remoed to make the tokenization easy and clean.
    tokens = text.split() #Here text is splitted based upon the spaces and is stored in a list named tokens. But this token still can have additional helping words which we need to remove to further clean our lexicon dictionary.
    filtered_tokens = [] #Creating a list of filtered tokens
    for word in tokens: #individually checking tokens in the list and only taking those which are not in the list and have length > 1 so only meaningful words are added in our final lexicon.
        if(word not in WORDS_TO_REMOVE) and (len(word) > 1):
            filtered_tokens.append(word)
    return filtered_tokens


#Main code cotaining the logic for creating the lexicon
def lexicon_generator():
    print("\nLoading the data set............\n")
    columns_to_use = ["title" , "abstract"]
    #We are using only two columns of our data set in our case of our csv files because these are the two only columns generating the lexicon dictionary of our project. Rest would only be used in foward and inverted indexing or ranking the results in the end.
    dataframe = pd.read_csv("data/patents_dataset.csv" , usecols=columns_to_use) 
    #We are using pandas library to crawl through our dataset and create our lexicon dictionary.The reason for using pandas is that there are most of the complex tasks that can be done easily with pandas however if we use simple csv file handling that would break down since our data set is huge and much more complex.
    dataframe = dataframe.fillna("") #Handling the missing / not avaialable values with empty strings to have a refined result
    #Since we need both our abstract and title to build the lexicon dictionary for our search engine we would first merge them both into a single string in a new column 'text':
    print("Merging the two columns..................\n")
    dataframe['text'] = dataframe['title'].astype(str) + " " + dataframe['abstract'].astype(str)
    #Now we have combined them both.

    print("Tokenizing and Cleaning the text , removing the junk characters and words , generating a clean lexicon............\n")
    dataframe['tokens'] = dataframe['text'].apply(clean_and_tokenize_text) 
    #Here we have created a new column of tokens which consists of list of filtered and final and clean tokens against each file i.e, against each patent in our dataset.

    print("Building a unique lexicon set.................\n")
    lexicon = set() #Here we have created a single new set for our lexicon since we had vectors of words for each file in our token column in the data frame. This vector of words for each patent can have duplicate words or overall there may be duplication . In order to avoid the duplicate words 
    for token_list_of_each_patent in dataframe['tokens']:
        lexicon.update(token_list_of_each_patent)