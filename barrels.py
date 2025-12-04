
# -----------------------------------------------
# barrels.py
# Reads inverted.txt and assigns each posting list to its corresponding barrel based on word ID. Each barrel is saved as a separate text file.
# -----------------------------------------------

# Usage:
# python barrels.py
# Make sure inverted.txt exists in the same directory.


import os

# Define the number of barrels 
NUM_BARRELS = 10  

# Path to the inverted index file
INPUT_FILE = "inverted.txt"

# Directory to store barrels
OUTPUT_DIR = "barrels"

# Just a starting statement for clarity that the program has started 
print("Starting barrel creation process...")

# Create barrels directory if it doesn't exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Initialize empty lists for each barrel
barrels = [[] for _ in range(NUM_BARRELS)]

# Read the inverted file
with open(INPUT_FILE, "r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()
        if not line:
            continue  # skip empty lines

        # Each line has format: wordID: postings
        try:
            word_id_str, postings = line.split(":", 1)
            word_id = int(word_id_str.strip())
        except ValueError:
            print("Skipping invalid line:", line)
            continue

        # Determine which barrel this word belongs to
        barrel_index = word_id % NUM_BARRELS

        # Append the line to the correct barrel
        barrels[barrel_index].append(line)

# Write each barrel to a separate file
for i in range(NUM_BARRELS):
    barrel_file = os.path.join(OUTPUT_DIR, f"barrel_{i}.txt")
    with open(barrel_file, "w", encoding="utf-8") as f:
        for entry in barrels[i]:
            f.write(entry + "\n")

print(NUM_BARRELS , "Barrels created successfully!")
