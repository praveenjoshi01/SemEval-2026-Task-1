import pandas as pd
import os
import time
from openai import OpenAI
from jinja2 import Environment, FileSystemLoader
from baseline_generator import format_user_input, get_rendered_prompt, generate_humor, set_config

# Constants
DATA_DIR = "data"
OUTPUT_DIR = "output"
TASK_FILE = "task-a-es.tsv"
TEMPLATE_NAME = "task_a_es.j2"
TARGET_IDS = ["es_2133", "es_2134", "es_2135"]

def main():
    print(f"Starting fix for {TASK_FILE}...")
    
    # Load data
    data_path = os.path.join(DATA_DIR, TASK_FILE)
    output_path = os.path.join(OUTPUT_DIR, TASK_FILE)
    
    if not os.path.exists(output_path):
        print(f"Error: Output file {output_path} not found.")
        return

    df_data = pd.read_csv(data_path, sep='\t')
    df_output = pd.read_csv(output_path, sep='\t')

    # Configure client (assumes .env is set up)
    set_config()
    
    for id_val in TARGET_IDS:
        print(f"Fixing ID: {id_val}...")
        
        # Get input row
        row = df_data[df_data['id'] == id_val].iloc[0]
        user_input = format_user_input(row, TASK_FILE)
        prompt = get_rendered_prompt(TEMPLATE_NAME, user_input)
        
        # Generate humor
        text = generate_humor(prompt)
        
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        
        if "ERROR" in text:
            print(f"Failed to generate for {id_val}: {text}")
            continue

        # Update output dataframe
        df_output.loc[df_output['id'] == id_val, 'text'] = text
        print(f"Updated {id_val} with: {text[:50]}...")
        time.sleep(1) # Extra buffer for rate limits

    # Save updated output
    df_output.to_csv(output_path, sep='\t', index=False)
    print(f"Successfully updated {output_path}")

if __name__ == "__main__":
    main()
