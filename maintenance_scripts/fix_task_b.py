import pandas as pd
import os
import time
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv
import base64
from jinja2 import Environment, FileSystemLoader

load_dotenv()
MODEL = "gpt-4o-mini"
DATA_DIR = "data"
OUTPUT_DIR = "output"
TEMPLATE_DIR = "templates"
client = OpenAI()

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def get_rendered_prompt(template_name, user_input):
    template = env.get_template(template_name)
    return template.render(user_input=user_input)

def generate_humor(prompt, vision_url=None):
    max_retries = 5
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            system_prompt = "You are a master of humor and wit. Follow the detailed instructions provided in the prompt."
            messages = [{"role": "system", "content": system_prompt}]
            
            if vision_url:
                if os.path.exists(vision_url):
                    with open(vision_url, "rb") as image_file:
                        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                    ext = os.path.splitext(vision_url)[1].lower()
                    mime_type = "image/gif" if ext == ".gif" else "image/jpeg"
                    messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
                        ]
                    })
                else:
                    messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": vision_url}}
                        ]
                    })
            else:
                messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                max_tokens=300,
                temperature=0.8
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            if "rate_limit_exceeded" in str(e).lower() or "429" in str(e):
                wait_time = retry_delay * (2 ** attempt)
                print(f"Rate limit hit. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Error: {e}")
                return f"ERROR: {str(e)}"
    
    return "ERROR: Max retries reached"

def format_user_input(row, filename):
    if "task-a" in filename:
        word1, word2, headline = str(row.get('word1', '-')), str(row.get('word2', '-')), str(row.get('headline', '-'))
        if word1 != '-' and word2 != '-':
            return f"Words: '{word1}', '{word2}'. Headline: '{headline}'" if headline != '-' else f"Words: '{word1}', '{word2}'"
        return f"Headline: '{headline}'"
    elif "task-b1" in filename:
        return "Generate a punchy, surprising caption for this GIF."
    elif "task-b2" in filename:
        return f"Prompt: {row.get('prompt', '')}"
    return str(row)

def process_tasks(tasks):
    for filename, template_name in tasks:
        print(f"Checking {filename}...")
        input_path = os.path.join(DATA_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        if not os.path.exists(input_path):
            print(f"Input file {input_path} missing. Skipping.")
            continue
            
        input_df = pd.read_csv(input_path, sep='\t')
        
        if os.path.exists(output_path):
            try:
                current_out_df = pd.read_csv(output_path, sep='\t')
                valid_rows = current_out_df[~current_out_df['text'].fillna('').str.startswith('ERROR')].copy()
            except Exception:
                valid_rows = pd.DataFrame(columns=['id', 'text'])
        else:
            valid_rows = pd.DataFrame(columns=['id', 'text'])
            
        completed_ids = set(valid_rows['id'])
        to_process = input_df[~input_df['id'].isin(completed_ids)]
        
        if len(to_process) == 0:
            print(f"No missing/failed rows for {filename}.")
            continue
            
        print(f"Generating {len(to_process)} rows for {filename}...")
        results = valid_rows.to_dict('records')
        
        for _, row in tqdm(to_process.iterrows(), total=len(to_process)):
            id_val = row['id']
            user_input = format_user_input(row, filename)
            prompt = get_rendered_prompt(template_name, user_input)
            
            vision_url = row.get('url') if "task-b" in filename else None
            text = generate_humor(prompt, vision_url=vision_url)
            
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
                
            results.append({'id': id_val, 'text': text})
            time.sleep(0.05)
            
        out_df = pd.DataFrame(results)
        # Sort back to original order
        out_df = input_df[['id']].merge(out_df, on='id', how='left')
        out_df.to_csv(output_path, sep='\t', index=False)

if __name__ == "__main__":
    semeval_tasks = [
        ("task-b1.tsv", "task_b1.j2"),
        ("task-b2.tsv", "task_b2.j2")
    ]
    process_tasks(semeval_tasks)
    print("Task B processing complete.")
