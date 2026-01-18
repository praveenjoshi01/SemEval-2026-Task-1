import pandas as pd
import re

print("="*80)
print("COMPREHENSIVE OUTPUT ANALYSIS FOR ALL TASKS")
print("="*80)

# Task definitions based on templates
task_configs = {
    'task-a-en.tsv': {
        'name': 'Task A (English)',
        'type': 'text-based',
        'input_col': 'headline',
        'requirements': ['1-3 sentences', 'topical humor', 'original']
    },
    'task-a-es.tsv': {
        'name': 'Task A (Spanish)',
        'type': 'text-based',
        'input_col': 'headline',
        'requirements': ['1-3 sentences', 'topical humor', 'original']
    },
    'task-a-zh.tsv': {
        'name': 'Task A (Chinese)',
        'type': 'text-based',
        'input_col': 'headline',
        'requirements': ['1-3 sentences', 'topical humor', 'original']
    },
    'task-b1.tsv': {
        'name': 'Task B1 (GIF Captions)',
        'type': 'multimodal',
        'input_col': 'url',
        'requirements': ['<=20 words', 'punchy caption', 'viral-style']
    }
}

def count_sentences(text):
    """Count sentences in text"""
    if pd.isna(text):
        return 0
    # Split by sentence terminators
    sentences = re.split(r'[.!?]+', str(text))
    # Filter out empty strings
    sentences = [s for s in sentences if s.strip()]
    return len(sentences)

def count_words(text):
    """Count words in text"""
    if pd.isna(text):
        return 0
    return len(str(text).split())

def analyze_task(input_file, output_file, config):
    """Analyze a specific task"""
    print(f"\n{'='*80}")
    print(f"TASK: {config['name']}")
    print(f"{'='*80}")
    
    # Read data
    input_df = pd.read_csv(f'data/{input_file}', sep='\t')
    output_df = pd.read_csv(f'output/{output_file}', sep='\t')
    
    # Merge
    merged = input_df.merge(output_df, on='id', how='inner')
    
    print(f"\nBasic Statistics:")
    print(f"  Input rows: {len(input_df)}")
    print(f"  Output rows: {len(output_df)}")
    print(f"  Matched rows: {len(merged)}")
    
    # Check for missing or error outputs
    errors = output_df['text'].astype(str).str.contains('ERROR|error|null|NaN', case=False, na=False).sum()
    empty = output_df['text'].isna().sum()
    
    print(f"\nData Quality:")
    print(f"  Empty outputs: {empty}")
    print(f"  Error outputs: {errors}")
    
    # Task-specific analysis
    if config['type'] == 'text-based':
        # Analyze Task A (sentence count)
        sentence_counts = output_df['text'].apply(count_sentences)
        word_counts = output_df['text'].apply(count_words)
        
        print(f"\nTask A Requirements Analysis:")
        print(f"  Requirement: {config['requirements']}")
        print(f"\n  Sentence Count Distribution:")
        print(f"    1 sentence: {(sentence_counts == 1).sum()} entries")
        print(f"    2 sentences: {(sentence_counts == 2).sum()} entries")
        print(f"    3 sentences: {(sentence_counts == 3).sum()} entries")
        print(f"    4+ sentences: {(sentence_counts > 3).sum()} entries")
        print(f"\n  Word Count Statistics:")
        print(f"    Average: {word_counts.mean():.1f} words")
        print(f"    Median: {word_counts.median():.0f} words")
        print(f"    Min: {word_counts.min()} words")
        print(f"    Max: {word_counts.max()} words")
        
        # Check for 1-3 sentence compliance
        compliant = ((sentence_counts >= 1) & (sentence_counts <= 3)).sum()
        print(f"\n  COMPLIANCE: {compliant}/{len(output_df)} ({compliant/len(output_df)*100:.1f}%) meet 1-3 sentence requirement")
        
    elif config['type'] == 'multimodal':
        # Analyze Task B1 (word count ≤20)
        word_counts = output_df['text'].apply(count_words)
        
        print(f"\nTask B1 Requirements Analysis:")
        print(f"  Requirement: {config['requirements']}")
        print(f"\n  Word Count Distribution:")
        print(f"    <=10 words: {(word_counts <= 10).sum()} entries")
        print(f"    11-15 words: {((word_counts > 10) & (word_counts <= 15)).sum()} entries")
        print(f"    16-20 words: {((word_counts > 15) & (word_counts <= 20)).sum()} entries")
        print(f"    21-25 words: {((word_counts >20) & (word_counts <= 25)).sum()} entries")
        print(f"    >25 words: {(word_counts > 25).sum()} entries")
        print(f"\n  Word Count Statistics:")
        print(f"    Average: {word_counts.mean():.1f} words")
        print(f"    Median: {word_counts.median():.0f} words")
        print(f"    Min: {word_counts.min()} words")
        print(f"    Max: {word_counts.max()} words")
        
        # Check for <=20 word compliance
        compliant = (word_counts <= 20).sum()
        violations = word_counts[word_counts > 20]
        print(f"\n  COMPLIANCE: {compliant}/{len(output_df)} ({compliant/len(output_df)*100:.1f}%) meet <=20 word requirement")
        
        if len(violations) > 0:
            print(f"\n  VIOLATIONS ({len(violations)} entries exceeding 20 words):")
            violations_df = output_df[word_counts > 20].copy()
            violations_df['word_count'] = word_counts[word_counts > 20]
            violations_df = violations_df.sort_values('word_count', ascending=False).head(5)
            for idx, row in violations_df.iterrows():
                print(f"    {row['id']}: {int(row['word_count'])} words")
                print(f"      Text: {row['text'][:80]}...")
    
    print(f"\n  [OK] Analysis complete for {config['name']}")
    
    return {
        'name': config['name'],
        'total': len(output_df),
        'errors': errors,
        'empty': empty
    }

# Analyze all tasks
results = []
for filename, config in task_configs.items():
    result = analyze_task(filename, filename, config)
    results.append(result)

# Final summary
print(f"\n{'='*80}")
print("FINAL SUMMARY")
print(f"{'='*80}")
for result in results:
    status = "OK" if result['errors'] == 0 and result['empty'] == 0 else "NEEDS REVIEW"
    print(f"  {result['name']:<30} {result['total']} rows [{status}]")

print(f"\n{'='*80}")
print("[SUCCESS] Comprehensive analysis complete!")
print(f"{'='*80}\n")
