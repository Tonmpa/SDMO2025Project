import os
import sys
import time

# Add src to path to allow importing from enhanced_deduplication
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_deduplication import EnhancedDeveloperDeduplication

# --- Configuration ---
INPUT_CSV = "/Users/ikwunna/dev/SDMO2025Project/data/kubernetes/devs.csv"
RESULTS_DIR = "/Users/ikwunna/dev/SDMO2025Project/data/kubernetes/results/"
CONFIDENCE_THRESHOLD = 0.75 # Default threshold
# -------------------

def run_experiment():
    """
    Runs the enhanced deduplication analysis on the Kubernetes dataset.
    """
    print("="*80)
    print("Starting Enhanced Deduplication for Kubernetes")
    print(f"Input data: {INPUT_CSV}")
    print(f"Results will be saved in: {RESULTS_DIR}")
    print(f"Confidence Threshold: {CONFIDENCE_THRESHOLD}")
    print("This may take a very long time.")
    print("="*80)

    start_time = time.time()

    # Initialize the analyzer with the Kubernetes CSV path
    analyzer = EnhancedDeveloperDeduplication(csv_path=INPUT_CSV)

    # Set the results directory and create it
    analyzer.results_dir = RESULTS_DIR
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Load developers
    print("Step 1/3: Loading developers from CSV...")
    analyzer.load_developers()
    dev_count = len(analyzer.developers)
    pair_count = int((dev_count * (dev_count - 1)) / 2)
    print(f"-> Loaded {dev_count} developers.")

    # Find duplicates
    print(f"\nStep 2/3: Finding duplicates (comparing {pair_count:,} pairs)...")
    analyzer.find_duplicates(threshold=CONFIDENCE_THRESHOLD)
    duplicate_count = len(analyzer.duplicates)
    print(f"-> Found {duplicate_count} potential duplicate pairs.")

    # Save results
    print("\nStep 3/3: Saving results...")
    analyzer.save_results()
    print(f"-> Results saved to {RESULTS_DIR}")

    end_time = time.time()
    total_minutes = (end_time - start_time) / 60

    print("\n" + "="*80)
    print("Experiment complete!")
    print(f"Total time: {total_minutes:.2f} minutes.")
    print("="*80)


if __name__ == "__main__":
    run_experiment()
