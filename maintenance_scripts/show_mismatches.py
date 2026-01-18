import pandas as pd
import re

# Read input data (original prompts)
input_df = pd.read_csv('data/task-b2.tsv', sep='\t')

# Read output data
output_df = pd.read_csv('output/task-b2.tsv', sep='\t')

# Merge
merged = input_df.merge(output_df, on='id', how='inner', suffixes=('_input', '_output'))

def normalize_text(text):
    """Normalize text for comparison"""
    if pd.isna(text):
        return ""
    text = str(text).lower()
    # Remove blank patterns
    text = text.replace('______', '').replace('_____', '')
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

mismatches = []

for idx, row in merged.iterrows():
    prompt = normalize_text(row['prompt'])
    output = normalize_text(row['text'])
    
    # Check if output starts with prompt
    if not output.startswith(prompt) and prompt not in output:
        mismatches.append({
            'id': row['id'],
            'prompt': row['prompt'],
            'output': row['text']
        })

print(f"=== ALL {len(mismatches)} MISMATCHED ENTRIES ===\n")
print("="*80)

for i, item in enumerate(mismatches, 1):
    print(f"\n{i}. ID: {item['id']}")
    print(f"   PROMPT: {item['prompt']}")
    print(f"   OUTPUT: {item['output']}")
    print("-"*80)

print(f"\nTotal: {len(mismatches)} entries")
