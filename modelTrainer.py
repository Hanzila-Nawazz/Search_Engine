#In order to implement the semantic search we need a model. We could have used a pre defined / pre trained model but that would not have such better results because they are normally trained on the wikipedia and all that so they might not be able to be synchronized with the smantics of patents data set. That's why training your own model is a better approach and thats why we trained our own model with the data set of google patents which had stunning results. We did this using genism library thats why we have added it.

#Loads the NLP library. This contains the Word2Vec algorithm we need to create the semantic embeddings.
import gensim 
#Using pandas since we would access our raw .csv file for the data set and would be doing that chunk wise so pandas is the best option to do with.
import pandas as pd 
#OS for basic try checks and os commands
import os
import traceback

#Columns we would only be using title and abstract because they cotain all the vocabulary
columns_to_use = ["title" , "abstract"]
#Path of the file for the source file
CSV_FILE_PATH = "patents_dataset.csv"
#Chunk size 
CHUNK_SIZE = 10000

#Defined a class patent Itertator for intertaing over the patents. This class acts as a "feeder." It streams data to the model one piece at a time.
class PatentIterator:

    #The constructor for the class. It runs once when we start. It saves the file path and sets our progress counter to zero.
    def __init__(self , csv_file_path):
        self.csv_file_path = csv_file_path
        self.chunks_processed = 0
    
    #A special Python method. It makes our class "iterable," meaning Word2Vec can ask it for the "next" item repeatedly.
    def __iter__(self):
        #Basic check for th file to be existing in the directory
        if not os.path.exists(self.csv_file_path):
            print(f"Error: File not found at the path : {self.csv_file_path}")
            return 
            
        #Here our iterator logic exists not to entirely load the big .csv file into RAM which would cause a crash rather load it in the ram in chunks of 10,000
        chunk_iterator = pd.read_csv(self.csv_file_path , usecols=columns_to_use , chunksize=CHUNK_SIZE)
        print("Reading chunks from CSV file for model training...")

        #Try catch block for addressing any crashes 
        try:
            #This loop starts reading the file batch-by-batch.
            for chunk in chunk_iterator:
                #Data cleaning. If a patent has no abstract (an empty cell/NaN), this replaces it with an empty string so the code doesn't break.
                chunk = chunk.fillna("")

                #This creates a temporary column called text. It combines the Title and Abstract into one long sentence. This is crucial because it links the "summary" keywords in the title to the "detailed" keywords in the abstract.
                chunk['text'] = chunk['title'].astype(str) + " " + chunk['abstract'].astype(str)

                #Loops through the 10,000 combined sentences in the current chunk.
                for text in chunk['text']:

                    #The cleaner. It removes punctuation, lowercases everything , and splits the sentence into a list of words.
                    tokens = gensim.utils.simple_preprocess(text)

                    #This is the most important line of the code . Instead of returning a list which fills RAM, it yields one sentence at a time to the model, waits for the model to process it, and then continues.
                    if len(tokens) > 2:
                        yield tokens
                
                #Counter check for the CLI
                self.chunks_processed += 1
                print(f"Chunk {self.chunks_processed} processed successfully!")

        #Excecption handling
        except Exception as e:
            print("An error occured while reading the file")
            traceback.print_exc()

#Main Function
if __name__ == "__main__":

    #This line intializes the iterator 
    sentences = PatentIterator(CSV_FILE_PATH)
    print("Starting training the model...")

    #Defining the model object with argumnets where first onnects our data feeder to the model. The model automatically starts pulling data using your iter method. Second argument tells the dimensions of vector for each word. We have set it to 200 ideal for our case. Third argument is the window siz how many words at a time are taken into context for semantics.Min count tells min how many words in a sentence to keep sentence. Fourth argument tells how many cores of processor to use. And last one enables the Skip-Gram Algorithm for sharp semantics.
    model = gensim.models.Word2Vec(
        sentences=sentences,
        vector_size=200,
        window=7,
        min_count=2,
        workers=4,
        sg=1
    )

    #When complete simply print and save the model in the directory for semantic search
    print("Training complete. Saving the model..")
    model.save("./word2vec-google-patents-dataset.model")
    print("Model saved successfully!")