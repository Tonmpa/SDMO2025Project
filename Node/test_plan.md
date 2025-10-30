# Testing the implementation

Purpose of testing is to ensure the proposed new algorithm works as expected to identify potential duplicates.

## Test cases
### Test 1: Are same people the same
"Alice Johnson", "alice@example.com",
"Alice Johnson", "alice@example.com"
Expected similarity: ==1

### Test 2: Are people with same name but different email the same
"Alice Johansson", "alice@example.com",
"Alice Johnson", "alice@example.com"
Expected similarity: >= 0.75

### Test 3: Are people with same email but different name the same
"Alice Johnson", "johnson.alice@example.com",
"Alice Johnson", "alice.johnson@example.com"
Expected similarity: >= 0.75

### Test 4: Are people with different email not the same
"Alice Johnson", "alice@example.com",
"Bob Smith", "bobberoo@example.com"
Expected similarity: >= 0.75

### Test 5: Test CSV processing
Expected to parse CSV contents correctly to an output CSV file.