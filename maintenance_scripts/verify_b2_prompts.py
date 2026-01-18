import pandas as pd
import re

# Read input data (original prompts)
input_df = pd.read_csv('data/task-b2.tsv', sep='\t')

# Read output data
output_df = pd.read_csv('output/task-b2.tsv', sep='\t')

# Merge
merged = input_df.merge(output_df, on='id', how='inner', suffixes=('_input', '_output'))

print(f"Analyzing {len(merged)} rows...\n")

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
partial_matches = []
full_matches = 0

for idx, row in merged.iterrows():
    prompt = normalize_text(row['prompt'])
    output = normalize_text(row['text'])
    
    # Check if output starts with prompt
    if output.startswith(prompt):
        full_matches += 1
    # Check if prompt is contained in output
    elif prompt in output:
        partial_matches.append({
            'id': row['id'],
            'prompt': row['prompt'][:60],
            'output': row['text'][:80]
        })
    else:
        mismatches.append({
            'id': row['id'],
            'prompt': row['prompt'][:60],
            'output': row['text'][:80]
        })

print("=== ANALYSIS RESULTS ===\n")
print(f"[OK] Full matches (output starts with prompt): {full_matches}")
print(f"[~] Partial matches (prompt contained in output): {len(partial_matches)}")
print(f"[X] Mismatches (prompt NOT in output): {len(mismatches)}")

if partial_matches:
    print(f"\n=== Partial Matches ({len(partial_matches)}) ===")
    for item in partial_matches[:5]:  # Show first 5
        print(f"\nID: {item['id']}")
        print(f"  Prompt: {item['prompt']}...")
        print(f"  Output: {item['output']}...")

if mismatches:
    print(f"\n=== MISMATCHES ({len(mismatches)}) ===")
    for item in mismatches[:10]:  # Show first 10
        print(f"\nID: {item['id']}")
        print(f"  Prompt: {item['prompt']}...")
        print(f"  Output: {item['output']}...")

print(f"\n=== SUMMARY ===")
total = len(merged)
consistent = full_matches + len(partial_matches)
print(f"Consistent entries: {consistent}/{total} ({consistent/total*100:.1f}%)")
print(f"Problematic entries: {len(mismatches)}/{total} ({len(mismatches)/total*100:.1f}%)")

if len(mismatches) == 0:
    print("\n[SUCCESS] All outputs are consistent with their prompts!")
else:
    print(f"\n[WARNING] Found {len(mismatches)} entries that may need review.")
