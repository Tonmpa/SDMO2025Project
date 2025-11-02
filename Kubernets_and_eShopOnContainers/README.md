# Source Code & Project Workflow

This document outlines the structure of the source code, the project workflow from data mining to analysis, and the testing procedures.

## Files

### Core Logic
- **`enhanced_deduplication.py`**: The main analysis module containing the `EnhancedDeveloperDeduplication` class. This implements the enhanced Bird heuristic (C1-C10) with weighted confidence scoring and clustering functionality.
- **`deduplication_config.ini`**: Configuration file for the deduplication process. It allows setting parameters like the confidence threshold and input/output file paths.

### Scripts
- **`run_kubernetes_experiment.py`**: A script to run the full deduplication analysis on the large Kubernetes dataset. It imports the logic from `enhanced_deduplication.py` and handles the entire analysis process.

## Project Workflow

The project is divided into two main phases: mining the data and running the analysis. Below are two examples for a small and a large repository.

### Example 1: Small Repository (eShopOnContainers)

This was the initial repository used for development and testing.

**1. Mining:**
The developer data was originally mined and is available at `data/ShopOnContainers/devs.csv`.

**2. Analysis:**
The analysis can be run by executing the main analysis module directly, which is configured by default to use the eShopOnContainers data:
```bash
python enhanced_deduplication.py
```
This loads `data/ShopOnContainers/devs.csv`, applies the enhanced heuristic, and saves results to `data/ShopOnContainers/results/`.

### Example 2: Large-Scale Repository (Kubernetes)

For larger repositories, a more robust workflow with dedicated scripts is used.

**1. Mining:**
The developer data was originally mined and is available at `data/kubernetes/devs.csv`.

**2. Analysis:**
A separate script runs the analysis on the large dataset. Run it from the project root directory:
```bash
python run_kubernetes_experiment.py
```
This loads the Kubernetes data, applies the algorithm, and saves the results to `data/kubernetes/results/`.

## Testing

The project includes a suite of unit tests to ensure the core logic of the deduplication algorithm is correct.

- **Test File**: `test_enhanced_deduplication.py`
- **Framework**: Python's built-in `unittest` library.

### Test Coverage
The test suite includes 9 tests that cover key functionality:
- **T1**: Perfect matches (identical name/email).
- **T2**: Similar names with the same email domain.
- **T3**: Same name with different email formats.
- **T4**: Completely different developers (should not match).
- **T5**: Unicode normalization for names with accents.
- **T6**: Correct application of the institutional domain bonus score.
- **T7**: Loading and processing of a real data file (`eShopOnContainers`).
- **T8**: Correct functionality of the duplicate clustering logic.
- **T9**: Sensitivity of the confidence threshold.

### How to Run Tests

To run the full test suite, execute the following command from the project root directory:

```bash
python test_enhanced_deduplication.py
```
The tests will run and print a summary of the results.
