
# -----------------------------------------------
# barrels.py
# Reads inverted.txt and assigns each posting list to its corresponding barrel based on word ID. Each barrel is saved as a separate text file.
# -----------------------------------------------

# Usage:
# python barrels.py
# Make sure inverted.txt exists in the same directory.


import os # Importing os module to handle file and directory operations
import psutil #Importing it to check the ram usage side-by-side to avoid crashing and testing the efficieny of the code

def print_memory_usage():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    # Convert bytes to MB to check the ram consumption during the process 
    current_ram = mem_info.rss / (1024 * 1024) 
    print(f"   [RAM Usage: {current_ram:.2f} MB]")


# Define the number of barrels. We divide the inverted index into NUM_BARRELS smaller files (barrels) to make searches faster and reduce memory usage when handling large indexes:

NUM_BARRELS = 10  # We can change NUM_BARRELS = 10 to another number if needed 

# Path to the inverted index file
INPUT_FILE = "inverted_index.txt" # This is the main inverted index containing wordID: postings 

# Directory to store barrels
OUTPUT_DIR = "barrels" # Folder where each barrel file will be stored. Helps organize data and prevent clutter

# Just a starting statement for clarity that the program has started 
print("Starting barrel creation process...")

# Create barrels directory if it doesn't exist. This ensures that later when we write files, we won't encounter errors due to missing folder
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Initialize empty lists for each barrel
# We will append each line from inverted.txt to the appropriate barrel based on its wordID
barrels = [[] for _ in range(NUM_BARRELS)]

# Check if inverted.txt exists
# This prevents the program from crashing if the input file is missing and informs the user
if not os.path.exists(INPUT_FILE):
    print("Error: inverted_index.txt not found.")
    exit()

line_count = 0
# Read the inverted file line by line 
# Each line represents a wordID and its postings
with open(INPUT_FILE, "r", encoding="utf-8") as file:
    for line in file:           # Loop through every line in the inverted index 
        line = line.strip()     # Remove extra spaces and newline characters
        if not line:
            continue  # skip empty lines as they don't contain any data 

        # Each line has format: wordID: postings
        try:
            word_id_str, postings = line.split(":", 1) # split into ID and postings
            word_id = int(word_id_str.strip()) # Convert wordID to integer for further calculations
        except ValueError: # If the line cannot be split or converted, it is invalid
            print("Skipping invalid line:", line)  # Inform the user that this line is being skipped
            continue # Skip to the next line

        # Determine which barrel this word belongs to
        # Using modulo ensures that wordIDs are evenly distributed across barrels
        barrel_index = word_id % NUM_BARRELS  # Compute the barrel index 

        # Append the line to the correct barrel
        # This is a temporary in-memory storage before writing to disk
        barrels[barrel_index].append(line)  # Add the current line to the corresponding barrel 

        #Updating line count every iteration and after every 5000 lines of the inverted index check the ram usage during the looping . We could have simply checked it in the last iteration where the usage is max but we wanted to check the efficiency throughout the program so we can debug (if any crash occurs) due to memeory

        line_count+=1
        #Having a safe check to avoid spamming in the terminal and checking it after every 5000 lines 
        if line_count % 5000 == 0:
            print(f"Processed {line_count} lines....")
            print_memory_usage()

# Write each barrel to a separate file
# This converts our in-memory lists into actual text files for persistent storage
for i in range(NUM_BARRELS):
    print(f"Barrel {i} contains {len(barrels[i])} entries.") # debug print for barrel entry counts
    barrel_file = os.path.join(OUTPUT_DIR, f"barrel_{i}.txt")  # Create a file path for the current barrel
    with open(barrel_file, "w", encoding="utf-8") as f:  # Open the barrel file for writing
        for entry in barrels[i]: 
            f.write(entry + "\n")  # Write each entry followed by a newline to the file

# Inform the user that all barrels have been successfully created (Completion Message   )
print(NUM_BARRELS , "Barrels created successfully!")
