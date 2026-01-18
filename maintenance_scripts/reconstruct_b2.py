import pandas as pd
import re

# Read input data (original prompts)
input_df = pd.read_csv('data/task-b2.tsv', sep='\t')

# Read cleaned output
output_df = pd.read_csv('output/task-b2.tsv', sep='\t')

# Merge to have both prompts and outputs
merged = input_df.merge(output_df, on='id', how='inner', suffixes=('_input', '_output'))

# Function to check if text needs reconstruction
def needs_reconstruction(text):
    if pd.isna(text):
        return False
    text_str = str(text)
    # Check if starts with ellipsis or is very short without the prompt
    return text_str.startswith('...') or text_str.startswith('…')

# Function to reconstruct the full sentence
def reconstruct_sentence(row):
    output_text = str(row['text'])
    prompt = str(row['prompt'])
    
    # If output starts with ellipsis, it's a continuation
    if output_text.startswith('...') or output_text.startswith('…'):
        # Remove ellipsis
        continuation = re.sub(r'^\.\.\.+', '', output_text).strip()
        continuation = re.sub(r'^…+', '', continuation).strip()
        
        # Combine prompt with continuation
        # Remove the blank pattern from prompt if present
        prompt_clean = prompt.replace('______', '').strip()
        
        # Create full sentence
        full_sentence = f"{prompt_clean} {continuation}"
        return full_sentence.strip()
    
    return output_text

# Find and reconstruct incomplete entries
count = 0
for idx, row in merged.iterrows():
    if needs_reconstruction(row['text']):
        reconstructed = reconstruct_sentence(row)
        output_df.loc[output_df['id'] == row['id'], 'text'] = reconstructed
        count += 1
        print(f"Reconstructed {row['id']}:")
        print(f"  Before: {row['text'][:80]}...")
        print(f"  After:  {reconstructed[:80]}...")
        print()

print(f"\n=== Summary ===")
print(f"Total reconstructed: {count}")

# Save updated file
output_df.to_csv('output/task-b2.tsv', sep='\t', index=False)
print("Updated file saved!")

# Verify  
print("\nRe-reading to verify...")
verify_df = pd.read_csv('output/task-b2.tsv', sep='\t')
print(f"Row count: {len(verify_df)}")
print("[SUCCESS] Reconstruction complete!")
