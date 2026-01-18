import pandas as pd
import os

DATA_DIR = "data"
OUTPUT_DIR = "output"

def clean_file(filename):
    print(f"Cleaning {filename}...")
    input_path = os.path.join(DATA_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(input_path):
        print(f"  Input {filename} not found. Skipping.")
        return
    if not os.path.exists(output_path):
        print(f"  Output {filename} not found. Skipping.")
        return
        
    input_df = pd.read_csv(input_path, sep='\t')
    # Use keep='first' or 'last'. Let's trust the first valid non-error one.
    try:
        output_df = pd.read_csv(output_path, sep='\t')
    except Exception as e:
        print(f"  Error reading {output_path}: {e}")
        return

    # Filter out rows where text starts with ERROR
    output_df = output_df[~output_df['text'].fillna('').str.startswith('ERROR')]
    
    # Deduplicate by ID
    output_df = output_df.drop_duplicates(subset=['id'], keep='first')
    
    # Merge with input IDs to ensure we have all rows in correct order
    final_df = input_df[['id']].merge(output_df, on='id', how='left')
    
    # Check for missing values
    missing_count = final_df['text'].isna().sum()
    if missing_count > 0:
        print(f"  WARNING: {filename} has {missing_count} missing rows after cleanup!")
        
    final_df.to_csv(output_path, sep='\t', index=False)
    print(f"  Done. Rows: {len(final_df)}")

if __name__ == "__main__":
    tasks = [
        "task-a-en.tsv",
        "task-a-es.tsv",
        "task-a-zh.tsv",
        "task-b1.tsv",
        "task-b2.tsv"
    ]
    for task in tasks:
        clean_file(task)
