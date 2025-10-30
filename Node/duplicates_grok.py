import csv
import difflib
import sys
import multiprocessing
from itertools import combinations

def levenshtein_distance(s1, s2):
    """Compute the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def compute_similarity(str1, str2):
    """Compute similarity percentage using Levenshtein distance (case-insensitive)."""
    if str1 is None:
      str1 = ''
    if str2 is None:
      str2 = ''
    str1 = str1.lower()
    str2 = str2.lower()
    dist = levenshtein_distance(str1, str2)
    max_len = max(len(str1), len(str2))
    if max_len == 0:
        return 100.0
    return (1 - (dist / max_len)) * 100

def init_worker(shared_data):
    """Initializer for multiprocessing workers to set global data."""
    global data
    data = shared_data

def compute_pair_similarity(args):
    """Compute overall similarity for a pair (i, j) using global data."""
    i, j = args
    name1 = data[i]['name']
    email1 = data[i]['email']
    name2 = data[j]['name']
    email2 = data[j]['email']
    
    name_sim = compute_similarity(name1, name2)
    email_sim = compute_similarity(email1, email2)
    overall_sim = (name_sim + email_sim) / 2
    
    return (name1, email1, name2, email2, overall_sim)

def read_csv(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except csv.Error:
        print("Error: Invalid CSV format. Ensure it has 'name' and 'email' headers.")
        sys.exit(1)

def process_csv(data, threshold, output_filename, num_processes=2):
    # Check for required columns
    if 'name' not in data[0] or 'email' not in data[0]:
        print("Error: CSV must have 'name' and 'email' columns.")
        sys.exit(1)
    
    n = len(data)
    if n < 2:
        print("Not enough data for duplicate detection.")
        return
    
    # Generate all unique pairs (i, j) where i < j
    pairs = list(combinations(range(n), 2))
    
    if not pairs:
        print("No pairs available for processing.")
        return
    
    print(f"Comparing {len(pairs)} pairs using {num_processes} processes...")
    
    # Use multiprocessing Pool with initializer to share data
    with multiprocessing.Pool(processes=num_processes, initializer=init_worker, initargs=(data,)) as pool:
        results = pool.map(compute_pair_similarity, pairs)
    
    # Filter results above threshold and sort by descending similarity
    duplicates = [res for res in results if res[4] > threshold]
    duplicates.sort(key=lambda x: x[4], reverse=True)

    # Write filtered results to CSV
    try:
        with open(output_filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            # Write headers
            writer.writerow(['name1', 'email1', 'name2', 'email2', 'similarity_percentage'])
            # Write rows
            i = 0
            for name1, email1, name2, email2, overall_sim in duplicates:
                writer.writerow([name1, email1, name2, email2, f"{overall_sim:.2f}"])
                i += 1
                if i >= 1000:
                    break
        print(f"Output written to '{output_filename}' with {len(duplicates)} pairs above {threshold}% threshold.")
    except IOError:
        print(f"Error: Could not write to '{output_filename}'.")
        sys.exit(1)
    
    if not duplicates:
        print(f"No pairs found above {threshold}% threshold. Empty CSV written with headers.")

def main():
    global data  # Make data accessible to worker functions
    
    if len(sys.argv) < 2:
        print("Usage: python script.py <csv_file> [threshold] [processes] [output_file]")
        sys.exit(1)
    
    filename = sys.argv[1]
    try:
        threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 80.0
    except ValueError:
        print("Error: Threshold must be a number (e.g., 80).")
        sys.exit(1)
    
    if threshold < 0 or threshold > 100:
        print("Error: Threshold must be between 0 and 100.")
        sys.exit(1)
    
    # Parse processes (optional)
    try:
        num_processes_arg_index = 3 if len(sys.argv) > 3 else None
        if num_processes_arg_index and sys.argv[num_processes_arg_index].isdigit():
            num_processes = int(sys.argv[num_processes_arg_index])
        else:
            num_processes = multiprocessing.cpu_count() - 1
        if num_processes < 1:
            raise ValueError
    except ValueError:
        print("Error: Processes must be a positive integer (e.g., 4).")
        sys.exit(1)
    
    # Parse output file (optional, after processes if provided)
    output_file_arg_index = 3 if len(sys.argv) == 4 else 4 if len(sys.argv) > 4 else None
    output_filename = sys.argv[output_file_arg_index] if output_file_arg_index else 'duplicates.csv'
    
    # Read only the first 1000 rows of the CSV file
    data = read_csv(filename)
    
    if not data:
        print("No data found in CSV.")
        return
    
    process_csv(data, threshold, output_filename, num_processes)

if __name__ == "__main__":
    # Global data for multiprocessing (set here to avoid pickling issues on some platforms)
    data = []  # Will be populated in main
    main()