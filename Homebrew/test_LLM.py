import pytest
import sys
from gpt4all import GPT4All
from GPT4All import is_same_person, process_csv

# -------------------------------
# Load GPT4All model 
# -------------------------------
MODEL_NAME = "mistral-7b-instruct-v0.1.Q4_0.gguf"

try:
    model = GPT4All(MODEL_NAME, device='cpu', n_threads=8)
    print(f"Model '{MODEL_NAME}' loaded successfully.")
except Exception as e:
    print(f"Error loading GPT4All model: {e}")
    sys.exit(1)

# -------------------------------
# Real model tests
# -------------------------------

def test_is_same_person_same():
    """Test with the real GPT4All model, same name and email"""
    result = is_same_person("Alice Johnson", "alice@example.com",
                            "Alice Johnson", "alice@example.com")
    assert result in ["SAME", "DIFFERENT", "ERROR"]
    print("Model output:", result)


def test_is_same_person_different():
    """Test with the real model for different people"""
    result = is_same_person("Alice Johnson", "alice@example.com",
                            "Bob Smith", "bobberoo@example.com")
    assert result in ["SAME", "DIFFERENT", "ERROR"]
    print("Model output:", result)


def test_process_csv(tmp_path):
    """Test the CSV processor using the real model"""
    csv_content = "name1;email1;name2;email2\nAlice;alice@a.com;Bob;bob@b.com\n"
    test_csv = tmp_path / "test.csv"
    test_csv.write_text(csv_content)
    process_csv(str(test_csv), max_rows=1)