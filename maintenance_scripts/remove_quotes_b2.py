import pandas as pd
import re

# Read the file
df = pd.read_csv('output/task-b2.tsv', sep='\t')

print(f"Processing {len(df)} rows...")

def remove_unnecessary_quotes(text):
    if pd.isna(text):
        return text
    
    text = str(text)
    
    # Remove outer wrapping quotes if the text starts and ends with a quote
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    
    # Replace double quotes "" with single quotes ' (these are likely meant to be emphasis)
    text = re.sub(r'""', "'", text)
    
    # Clean up any remaining standalone quotes at start/end
    text = text.strip('"').strip("'").strip()
    
    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

# Apply cleanup
print("Removing unnecessary quotes...")
df['text'] = df['text'].apply(remove_unnecessary_quotes)

# Save
df.to_csv('output/task-b2.tsv', sep='\t', index=False)

print("Cleanup complete!")

# Verify
verify_df = pd.read_csv('output/task-b2.tsv', sep='\t')
print(f"Final row count: {len(verify_df)}")

# Check for remaining double quotes
has_double_quotes = verify_df['text'].astype(str).str.contains('""').sum()
print(f"Entries with '\"\"': {has_double_quotes}")

# Show a few sample cleaned entries
print("\n=== Sample cleaned entries ===")
for idx in [2, 5, 10, 13]:
    if idx < len(verify_df):
        print(f"\n{verify_df.iloc[idx]['id']}:")
        print(f"  {verify_df.iloc[idx]['text'][:100]}...")

print("\n[SUCCESS] Quote cleanup done!")
