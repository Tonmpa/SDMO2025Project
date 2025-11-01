from Node.src.duplicates_grok import compute_similarity, process_csv, read_csv
import csv

EXPECTED_MINIMUM_SIMILARITY = 65

def test_compute_similarity_same_name_email():
    """Test algorithm for same name and email"""
    name_sim = compute_similarity("Alice Johnson", "Alice Johnson")
    email_sim = compute_similarity("alice@example.com", "alice@example.com")
    assert name_sim == 100, "Name similarity should be 100"
    assert email_sim == 100, "Email similarity should be 100"
    print("Algorithm output: name_sim=", name_sim, " email_sim=", email_sim)

def test_compute_similarity_different_name():
    """Test algorithm for different name"""
    result = compute_similarity("Alice Johansson", "Alice Johnson")
    assert result >= EXPECTED_MINIMUM_SIMILARITY, f"Name similarity should be above {EXPECTED_MINIMUM_SIMILARITY}"
    print("Algorithm output:", result)

def test_compute_similarity_different_email():
    """Test algorithm for different email"""
    result = compute_similarity("alice.johnson@outlook.com", "alice.johnson12@example.com")
    assert result >= EXPECTED_MINIMUM_SIMILARITY, f"Email similarity should be above {EXPECTED_MINIMUM_SIMILARITY}"
    print("Algorithm output:", result)


def test_compute_similarity_different_people():
    """Test algorithm for different people"""
    name_sim = compute_similarity("Alice Johnson", "Bob Smith")
    email_sim = compute_similarity("alice@example.com", "bobberoo@example.com")
    assert name_sim <= EXPECTED_MINIMUM_SIMILARITY, f"Name similarity should be below {EXPECTED_MINIMUM_SIMILARITY}"
    assert email_sim <= EXPECTED_MINIMUM_SIMILARITY, f"Email similarity should be below {EXPECTED_MINIMUM_SIMILARITY}"
    print("Algorithm output: name_sim=", name_sim, " email_sim=", email_sim)


def test_process_csv(tmp_path):
    """Test outputting data to CSV file and check for exactly three data rows (plus headers)."""
    # Use data that SHOULD produce exactly three duplicate pairs (all pairs >75% similarity)
    csv_content = (
        "name,email\n"
        "Alice Johnson,alice.johnson@example.com\n"
        "Alicia Johnson,alice.j@example.com\n"
        "Alyce Johnson,alyce.johnson@example.com\n"
    )
    test_input_csv = tmp_path / "input_test.csv"
    test_input_csv.write_text(csv_content)
    
    data = read_csv(str(test_input_csv))  # Convert Path to str for read_csv
    print("Input data:", data)
    
    # Use a temporary output path (avoids hardcoding "Node/results.csv" and path issues)
    output_filename = str(tmp_path / "results.csv")
    process_csv(data, threshold=EXPECTED_MINIMUM_SIMILARITY, output_filename=output_filename, num_processes=1)  # Use 1 process to avoid Windows issues in tests
    
    # Assert: Check if output file exists and has expected content
    assert tmp_path / "results.csv"  # File exists
    
    with open(output_filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
        # Assert: Exactly four rows total (headers + three data rows)
        assert len(rows) == 4, f"Expected 4 rows (headers + 3 data rows), but got {len(rows)}"
        
        # Assert: Headers are correct
        assert rows[0] == ['name1', 'email1', 'name2', 'email2', 'similarity_percentage']
        
        # Assert: All three expected duplicate pairs are present (in any order, but code sorts by descending similarity)
        expected_pairs = [
            ("Alice Johnson", "alice.johnson@example.com", "Alyce Johnson", "alyce.johnson@example.com"),  # High sim
            ("Alice Johnson", "alice.johnson@example.com", "Alicia Johnson", "alice.j@example.com"),    # High sim
            ("Alicia Johnson", "alice.j@example.com", "Alyce Johnson", "alyce.johnson@example.com")     # High sim
        ]
        data_rows = [tuple(row[:4]) for row in rows[1:]]  # Extract name1,email1,name2,email2 from each data row
        for expected in expected_pairs:
            assert expected in data_rows or expected[::-1] in data_rows, f"Missing expected pair: {expected}"  # Allow reverse order (e.g., name1/name2 swapped)
        
        # Assert: Similarity percentages are present and > threshold (basic check)
        for row in rows[1:]:
            sim = float(row[4])
            assert sim > EXPECTED_MINIMUM_SIMILARITY, f"Similarity {sim} is not > {EXPECTED_MINIMUM_SIMILARITY}"
    
    print(f"Output CSV contents: {rows}")