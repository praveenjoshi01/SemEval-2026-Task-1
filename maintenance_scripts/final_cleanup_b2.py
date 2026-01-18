import pandas as pd
import re

# Read the file
df = pd.read_csv('output/task-b2.tsv', sep='\t')

print(f"Processing {len(df)} rows...")

def final_quote_cleanup(text):
    if pd.isna(text):
        return text
    
    text = str(text)
    
    # Remove ""... pattern (double quotes followed by ellipsis)
    text = re.sub(r'""\.\.\.', '', text)
    
    # Remove standalone double quotes at the beginning
    text = re.sub(r'^""\s*', '', text)
    
    # Remove standalone double quotes "" in the middle or end
    text = re.sub(r'\s*""\s*', ' ', text)
    
    # Remove leading/trailing quotes if they're orphaned
    text = text.strip('"').strip("'").strip()
    
    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

# Apply cleanup
df['text'] = df['text'].apply(final_quote_cleanup)

# Save
df.to_csv('output/task-b2.tsv', sep='\t', index=False)

print("Cleanup complete!")

# Verify
verify_df = pd.read_csv('output/task-b2.tsv', sep='\t')
print(f"Final row count: {len(verify_df)}")

# Check for remaining patterns
has_double_quote_ellipsis = verify_df['text'].astype(str).str.contains(r'""\.\.\.').sum()
print(f"Entries with '\"\"...': {has_double_quote_ellipsis}")

print("\n[SUCCESS] Final cleanup done!")
