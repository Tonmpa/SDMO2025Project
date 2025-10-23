import csv
import sys
from gpt4all import GPT4All

# -------------------------------
# Load GPT4All model. Please dont run on bad hardware this s*** takes forever
# -------------------------------
MODEL_NAME = "mistral-7b-instruct-v0.1.Q4_0.gguf"

try:
    model = GPT4All(MODEL_NAME, device='cpu', n_threads=8)
except Exception as e:
    print(f"Error loading GPT4All model: {e}")
    sys.exit(1)


def is_same_person(name1, email1, name2, email2) -> str:
    """
    Uses GPT4All model to determine if two records belong to the same person.
    Returns 'SAME', 'DIFFERENT', or 'ERROR'.
    """
    prompt = f"""
Given the following two developer records, tell me if they belong to the SAME PERSON.
Answer ONLY with 'SAME' or 'DIFFERENT'.

Record 1:
Name: {name1}
Email: {email1}

Record 2:
Name: {name2}
Email: {email2}
"""
    try:
        with model.chat_session() as session:
            try:
                response = session.generate(prompt, max_tokens=20, temp=0.2)
            except TypeError:
    
                response = session.generate(prompt, 20, 0.2)

            answer = response.strip().upper()
            if "SAME" in answer:
                return "SAME"
            elif "DIFFERENT" in answer:
                return "DIFFERENT"
            else:
                return "ERROR"
    except Exception as e:
        print(f"Model error for input ('{name1}', '{name2}'): {e}")
        return "ERROR"


def process_csv(file_path, max_rows=1340):
    with open(file_path, 'r', encoding='latin-1') as file:
        reader = csv.reader(file, delimiter=';')
        header = next(reader, None)  

        total = 0
        llm_same_count = 0
        llm_different_count = 0


        for row in reader:
            if total >= max_rows:
                break
            if len(row) < 4:
                continue

            name1, email1, name2, email2 = row[:4]

            result = is_same_person(name1, email1, name2, email2)
            print(f"{total+1}: {name1} ↔ {name2} → {result}")

            total += 1
            
            if result == "SAME":
                llm_same_count += 1
            elif result == "DIFFERENT":
                llm_different_count += 1

            total += 1

        print("\n--- Summary ---")
        print(f"Total pairs processed: {total}")
        print(f"LLM SAME count: {llm_same_count}")
        print(f"LLM DIFFERENT count: {llm_different_count}")

        print(f"\nProcessed {total} rows.")


if __name__ == '__main__':
    file_path = "project1devs/Evaluated_similiarity_csv.csv"
    process_csv(file_path)


