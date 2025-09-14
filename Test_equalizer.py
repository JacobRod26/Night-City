import random
import time

global output
# Song parameters
song_duration_seconds = 180  # 3 minutes
num_chunks = 4096

# Calculate chunk duration (for reference)
chunk_duration = song_duration_seconds / num_chunks

def generate_percentages():
    # Generate random percentages that sum to 1.0
    values = [random.random() for _ in range(4)]
    total = sum(values)
    normalized = [v / total for v in values]
    return {
        'drums': round(normalized[0], 3),
        'bass': round(normalized[1], 3),
        'other': round(normalized[2], 3),
        'vocals': round(normalized[3], 3)
    }

def main():
    for chunk in range(num_chunks):

        #data we want to pull is "output" for the test
        # the format is "Chunk #### {'drums': 0.123, 'bass': 0.456, 'other': 0.234, 'vocals': 0.187}"
        # or call generate_percentages() directly 
        output = generate_percentages()
        #generate a print every.1 seconds
        time.sleep(0.1)
        print(f"Chunk {chunk+1}: {output}")

if __name__ == "__main__":
    main()