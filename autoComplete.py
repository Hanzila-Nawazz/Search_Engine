import os 

#Defined a basic structure of node of Trie Data Structure 
class TrieNode:
    #The constrcutor
    def __init__(self):

        #Each node contains a dictionary of children that stores the connection to the next letters. For example if a current node represents letter a and we have words like ant and auto in our Trie then this map would be pointing to the letter n and u 
        self.children = {}

        #Wether the current node indicates the end of a valid word or not 
        self.is_end_of_word = False

        #This is a better version of the auto complete. Suggestions would be given based on the frequency. Not merely on the alphabetical order but also on the frequency of word in the dictionary
        self.frequency_score = 0

        #This is an optimization . Whenever we have to return the result (word) rather than back-tracking all the way upto the root is a slow and time taking process we simply rturn from the same node since the complete word is stored there already.
        self.word = None


class AutoCompleteSystem:

    #Auto complete class haing constructor in which we create a root which itself indicates no letter only have the children so we create a root node and load the Trie data structure 
    def __init__(self):
        self.root = TrieNode()
        print("Initializing Autocomplete System...")

        self.load_data()
        print("Auto complete system ready")

    
    #First we need to insert all the words in the lexicon dictionary to the trie data structure so we have this insert function
    def insert(self , word , score):

        #We take the root in the variable node
        node = self.root

        #For every letter in the word we would be adding paths in the Trie
        for letter in word:

            #If it is not present in the current node's children set simply create one 
            if letter not in node.children:
                node.children[letter] = TrieNode()
            
            #If exists move forward to the node
            node = node.children[letter]

        #Mark the end of word true till we reach the very end 
        node.is_end_of_word = True
        #We initialize the frequency score 
        node.frequency_score = score
        #We also initialize the word at that node . Only at those nodes at which a valid word ends. In all the continuation nodes we simply set them all to None 
        node.word = word

    
    def load_data(self):

        #The helper lode function to load the Trie structure when auto complete system instance is created 
        frequency_file_path = "word_frequency.txt"

        if not os.path.exists(frequency_file_path):
            print(f"Error. The word frequency file {frequency_file_path} not found! Load the file first")
            return 
        
        print(f"Loading words from {frequency_file_path} ....")
        count = 0

        #Try opening the word frequency file from each line fetch the word and the frequency , add the words and the frequencies whereever required
        try:
            with open(frequency_file_path , "r" , encoding="utf-8") as file:
                for line in file:
                    parts = line.strip().split(" : ")

                    if len(parts) >= 2:

                        word = parts[0].strip().lower()

                        try:
                            score = int(parts[1].strip())
                        except ValueError:
                            score = 1

                        self.insert(word , score)
                        count += 1

                        if count % 1000 == 0:
                            print(f"Successfully  inserted {count} words into the Trie.")

        except Exception as e:
            print(f"An error occurred while processing the file...")

    
    #Since till now our Trie structure has been loaded now our task is to find the suggestions based on the structure we take the prefix which needs to be completed 
    def search(self , prefix):

        if not prefix:
            return []
        
        node = self.root
        prefix = prefix.lower()

        #For each letter in the prefix we will look for it in the map till we reach the last letter if the prefix anad we are currently pointing to the node indicating the last word of the prefix
        for letter in prefix:
            if letter not in node.children:
                return []
            node = node.children[letter]

        #Since we are currently at the last letter of the prefix node we need all the valid words down from here to be stored and then based on the frequecny we will give the suggestions
        candidates = []

        #We are calling the helper function to traverse deep down in the Trie structure taking the current node and the candidates list as argument because this is passed by reference any changes made to the list would reflect here as well 
        self.depth_first_traversal(node , candidates)

        #After that we would sort the list based on the frequecny since each entity is a tuple containing the word and the frequecny and we would sort in descending order based on the frequency.
        candidates.sort(key= lambda x: x[1] , reverse= True)

        #We would return the words only from the tuples and only top 5 we would slice the list so that we only get top ranked results 
        return [item[0] for item in candidates [:7]]
    
    
    #Depth first traversal takes current node and candidates list
    def depth_first_traversal(self , node , candidates):

        #If valid word reached we simply append the word and frequency to the list and these changes would reflect in the upper function as well 
        if node.is_end_of_word:
            candidates.append((node.word , node.frequency_score))

        #For every child node till the whole depth of Trie structure is need and we recursively call the function
        for child_node in node.children.values():
            self.depth_first_traversal(child_node , candidates)

#We create an instance and test the system 
if __name__ == "__main__":
    instance = AutoCompleteSystem()
    while True:
        user_input = input("Enter prefix for autocomplete and space to exit : ")
        if user_input == " ":
            break

        suggestions = instance.search(user_input)
        print(f"Suggestions : {suggestions} " )