import pandas as pd

# Path to your file
filename = "project1devs/Evaluated_similiarity_csv.csv"

# Read CSV with fallback encoding
try:
    df = pd.read_csv(filename, sep=";", encoding="utf-8-sig")
except UnicodeDecodeError:
    df = pd.read_csv(filename, sep=";", encoding="latin1")

last_col = df.columns[-1]

# Skip the first row
data_df = df.iloc[1:]

# Find the first row with empty last column
empty_idx = data_df[data_df[last_col].isna() | (data_df[last_col].str.strip() == "")].index
if not empty_idx.empty:
    first_empty = empty_idx[0]
    print(f"Stopping at row {first_empty} due to empty last column.")
    data_df = data_df.loc[:first_empty-1]

# Compute FP rate on remaining rows
fp_rate = (data_df[last_col].str.strip().eq("FP")).mean()
tp_rate = (data_df[last_col].str.strip().eq("TP")).mean()
print(f"Processed rows: {len(data_df)}")
print(f"FP rows: {(data_df[last_col].str.strip().eq('FP')).sum()}")
print(f"TP rows: {(data_df[last_col].str.strip().eq('TP')).sum()}")
print(f"FP rate: {fp_rate:.4f} ({fp_rate*100:.2f}%)")


