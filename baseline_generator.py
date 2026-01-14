import pandas as pd
import os
import time
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv
import zipfile
import base64
from jinja2 import Environment, FileSystemLoader

load_dotenv()
client = None
MODEL = "gpt-4o-mini"

DATA_DIR = "data"
OUTPUT_DIR = "output"
TEMPLATE_DIR = "templates"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def set_config(api_key=None, model=None):
    global client, MODEL
    if api_key:
        client = OpenAI(api_key=api_key)
    if model:
        MODEL = model

# Initialize default client if key in env
if os.getenv("OPENAI_API_KEY"):
    client = OpenAI()

# Setup Jinja2 environment
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def get_rendered_prompt(template_name, user_input, template_content=None):
    if template_content:
        # If template content is provided directly (from UI editor)
        template = Environment().from_string(template_content)
    else:
        template = env.get_template(template_name)
    return template.render(user_input=user_input)

def generate_humor(prompt, max_tokens=300, vision_url=None):
    if client is None:
        return "ERROR: OpenAI API Key not configured. Please set it in the sidebar."
    try:
        system_prompt = "You are a master of humor and wit. Follow the detailed instructions provided in the prompt."
        messages = [{"role": "system", "content": system_prompt}]
        
        if vision_url:
            if os.path.exists(vision_url):
                # Handle local file
                with open(vision_url, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                
                # Determine mime type (OpenAI supports image/jpeg, image/png, image/gif, image/webp)
                ext = os.path.splitext(vision_url)[1].lower()
                mime_type = "image/gif" if ext == ".gif" else "image/jpeg" # Defaulting if unknown
                
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
                    ]
                })
            else:
                # Handle URL
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
            max_tokens=max_tokens,
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error: {e}")
        return f"ERROR: {str(e)}"

def format_user_input(row, filename):
    if "task-a" in filename:
        word1, word2, headline = row.get('word1', '-'), row.get('word2', '-'), row.get('headline', '-')
        if word1 != '-' and word2 != '-':
            user_input = f"Words: '{word1}', '{word2}'. Headline: '{headline}'" if headline != '-' else f"Words: '{word1}', '{word2}'"
        else:
            user_input = f"Headline: '{headline}'"
    elif "task-b" in filename:
        if "b2" in filename:
            user_input = f"Prompt: {row.get('prompt', '')}"
        else:
            user_input = "Generate caption for this GIF."
    else:
        user_input = str(row)
    return user_input

def process_task(filename, template_name, limit=None):
    print(f"Processing {filename}...")
    df = pd.read_csv(os.path.join(DATA_DIR, filename), sep='\t')
    if limit:
        df = df.head(limit)
        
    results = []
    for _, row in tqdm(df.iterrows(), total=len(df)):
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
    out_df.to_csv(os.path.join(OUTPUT_DIR, filename), sep='\t', index=False)
    return out_df

def create_zip():
    print("Creating ZIP...")
    with zipfile.ZipFile("submission.zip", "w") as zf:
        for f in os.listdir(OUTPUT_DIR):
            if f.endswith(".tsv"):
                zf.write(os.path.join(OUTPUT_DIR, f), f)
    print("ZIP created: submission.zip")

def main():
    process_task("task-a-en.tsv", "task_a_en.j2", limit=2)
    process_task("task-a-es.tsv", "task_a_es.j2", limit=2)
    process_task("task-a-zh.tsv", "task_a_zh.j2", limit=2)
    process_task("task-b1.tsv", "task_b1.j2", limit=2)
    process_task("task-b2.tsv", "task_b2.j2", limit=2)
    create_zip()

if __name__ == "__main__":
    main()
