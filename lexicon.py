import pandas as pd 
import re
# Haseem in the house
WORDS_TO_REMOVE = set(["the", "of", "and", "a", "to", "in", "is", "you", "that", "it", "he", "was", "for", "on","are", "as", "with", "his", "they", "at", "be", "this", "have", "from", "or", "one", "had", "by", "word", "but", "not", "what", "all", "were", "we", "when", "your", "can", "said", "there", "use", "an", "each", "which", "she", "do", "how", "their", "if"])
#So we have created a list of words that are the supporting words and we dont actaully need them in our lexicon dictionary 

#Added a further improvement to distinguish between the similar terms ending with different suffixes yet having the same meaning in the context

def simplify_word(word):
    if len(word) < 4:
        return word

    if word.endswith("ational"): return word[:-7] + "ate"  # relational -> relate
    if word.endswith("tional"):  return word[:-6] + "tion" # conditional -> condition
    if word.endswith("ization"): return word[:-7] + "ize"  # optimization -> optimize
    if word.endswith("bility"):  return word[:-6] + "ble"  # capability -> capable

    if word.endswith("ment"): return word[:-4]  # adjustment -> adjust
    if word.endswith("ness"): return word[:-4]  # darkness -> dark
    if word.endswith("able"): return word[:-4]  # adjustable -> adjust
    if word.endswith("ible"): return word[:-4]  # flexible -> flex
    if word.endswith("less"): return word[:-4]  # wireless -> wire
    if word.endswith("ship"): return word[:-4]  # friendship -> friend

    if word.endswith("ing"): return word[:-3]   # running -> run
    if word.endswith("ion"): return word[:-3]   # connection -> connect
    if word.endswith("ive"): return word[:-3]   # active -> act
    if word.endswith("ous"): return word[:-3]   # continuous -> continu
    if word.endswith("ful"): return word[:-3]   # helpful -> help
    if word.endswith("ize"): return word[:-3]   # modernize -> modern
    if word.endswith("ate"): return word[:-3]   # activate -> activ
    if word.endswith("iti"): return word[:-3]   # activity -> activ

    # We require length > 5 here to be safe (don't turn "real" into "re")
    if word.endswith("al") and len(word) > 5: return word[:-2]  # electrical -> electric
    if word.endswith("er") and len(word) > 5: return word[:-2]  # driver -> driv
    if word.endswith("or") and len(word) > 5: return word[:-2]  # creator -> creat
    if word.endswith("ly"): return word[:-2]                    # quickly -> quick
    if word.endswith("ed"): return word[:-2]                    # worked -> work

    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word

def clean_and_tokenize_text(text):
    text = text.lower() #We make all the text in the lower case to have a consistent dictionary and no case difference affects our search results and lexcion generation.
    text = re.sub(r'[^a-z0-9]', ' ' , text) #This line is written and is very cruical.This line uses the regular expressions library and with help of them we are excluding evry charcater other than alphabets and digits and sub function does the task of replacing the charactrs other than alphabets and numbers with the empty strings.
    text = re.sub(r'\s+', ' ', text).strip() #Here extra spaces other than a single space are remoed to make the tokenization easy and clean.
    tokens = text.split() #Here text is splitted based upon the spaces and is stored in a list named tokens. But this token still can have additional helping words which we need to remove to further clean our lexicon dictionary.
    filtered_tokens = [] #Creating a list of filtered tokens
    for word in tokens: #individually checking tokens in the list and only taking those which are not in the list and have length > 1 so only meaningful words are added in our final lexicon.
        if((word not in WORDS_TO_REMOVE) and (len(word) > 1) and (not word.isdigit())):
            processed_word = simplify_word(word)
            filtered_tokens.append(processed_word)
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
    lexicon = set() #Here we have created a single new set for our lexicon since we had vectors of words for each file in our token column in the data frame. This vector of words for each patent can have duplicate words or overall there may be duplication . In order to avoid the duplicate words we have used a set data structure which ignores the duplicate words and keep only unique words.
    for token_list_of_each_patent in dataframe['tokens']:
        lexicon.update(token_list_of_each_patent) #We have used the update function rather than add because we are throwing a list of words against each patent.

    print(f"Total unique words in lexicon : {len(lexicon)}\n")
    #Ok , so we could have done it inside the tokenizer but we preffered to do here because we can later use that function in our frequency check without eliminating our duplicate words which is helpful in page ranking.

    print("Sorting the lexicon list in the alphabetical order for better indexing................\n")
    sorted_lexicon = sorted(list(lexicon)) #Here we have first converted our lexicon set into a list because sort function can be applied to the list not a set since sets are unordered and a list is ordered data strucure.

    print("Generating a .txt lexicon file with correct indices.....................\n")
    with open("lexicon.txt", "w", encoding="utf-8") as f: #Opening file in write mode alongwith using with open structure that opens the file safely and is closed automatically in case of program crash and prevents the data corruption. If file does exist it overwrites and if not it simply creates a file. We have done this in order to make sure that in case of new document upload lexicon is regenerated safely and efficiently.
        for word_id, word in enumerate(sorted_lexicon): #This way it automatically asigns the id to the words and uses a for loop to iterate over multiple words along with their ids and write it in the lexicon.txt file and adding a new line character after every line.
            f.write(f"{word_id} : {word}\n")
            
    print("Lexicon file has been successfully generated.\n")

lexicon_generator()
