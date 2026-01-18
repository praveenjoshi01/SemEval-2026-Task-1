import pandas as pd
import re
import os

OUTPUT_FILE = "output/task-b2.tsv"

def clean_text(text):
    """Clean a single text entry comprehensively."""
    if pd.isna(text) or not text:
        return text
    
    # Convert to string and work with it
    text = str(text)
    
    # Remove triple quotes at start/end
    text = text.strip('"""').strip("'''")
    
    # Remove "Prompt: " prefix (with varying spaces)
    text = re.sub(r'^Prompt:\s*', '', text, flags=re.IGNORECASE)
    
    # Remove blank patterns
    text = text.replace('______ ', '')
    text = text.replace('______', '')
    
    # Remove metadata in parentheses at end of line
    text = re.sub(r'\s*\([^)]*\)\s*$', '', text)
    
    # Remove leading ellipsis
    text = re.sub(r'^\.\.\.+', '', text)
    
    # Remove square brackets
    text = text.replace('[', '').replace(']', '')
    
    # Remove double asterisks
    text = text.replace('**', '')
    
    # Normalize quotes - replace doubled quotes with singles where appropriate
    # First handle the case of "" used for emphasis
    text = re.sub(r'""([^"]+)""', r"'\1'", text)
    
    # Consolidate whitespace
    text = ' '.join(text.split())
    
    # Strip leading/trailing whitespace and quotes
    text = text.strip().strip('"').strip("'").strip()
    
    return text

def main():
    print("Reading task-b2.tsv...")
    df = pd.read_csv(OUTPUT_FILE, sep='\t')
    
    print(f"Original row count: {len(df)}")
    
    # Clean the text column
    print("Cleaning text entries...")
    df['text'] = df['text'].apply(clean_text)
    
    # Save back to TSV
    print("Saving cleaned file...")
    df.to_csv(OUTPUT_FILE, sep='\t', index=False)
    
    # Verification
    print("\n=== Verification ===")
    print(f"Final row count: {len(df)}")
    
    # Re-read to verify TSV integrity
    print("Re-reading file to verify TSV integrity...")
    verify_df = pd.read_csv(OUTPUT_FILE, sep='\t')
    print(f"Verification row count: {len(verify_df)}")
    
    if len(verify_df) == len(df):
        print("[OK] TSV file structure is intact")
    else:
        print("[WARNING] Row count mismatch after re-reading!")
    
    # Check for tabs in text content
    tabs_in_text = verify_df['text'].astype(str).str.contains('\t').sum()
    if tabs_in_text == 0:
        print("[OK] No tabs found in text content")
    else:
        print(f"[WARNING] Found {tabs_in_text} entries with tabs in text!")
    
    # Show sample
    print("\n=== Sample cleaned entries ===")
    for idx in [0, 1, 5, 10]:
        if idx < len(verify_df):
            print(f"\n{verify_df.iloc[idx]['id']}:")
            print(f"  {verify_df.iloc[idx]['text'][:100]}...")
    
    print("\n[SUCCESS] Cleanup complete!")

if __name__ == "__main__":
    main()
