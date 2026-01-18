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

def generate_humor(id_val, user_input, template_name, vision_url=None):
    try:
        # Load the template text to use as system instructions
        with open(os.path.join(TEMPLATE_DIR, template_name), 'r', encoding='utf-8') as f:
            template_text = f.read()
        
        # Remove the variable placeholder from the system prompt part
        system_instructions = template_text.replace("{{ user_input }}", "").strip()
        
        messages = [{"role": "system", "content": system_instructions}]
        
        if vision_url and os.path.exists(vision_url):
            with open(vision_url, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            ext = os.path.splitext(vision_url)[1].lower()
            mime_type = "image/gif" if ext == ".gif" else "image/jpeg"
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": user_input},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
                ]
            })
        else:
            messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=300,
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"

def fix_7():
    missing_ids = ['img_2_0876', 'img_2_0874', 'img_2_0854', 'img_2_0853', 'img_2_0828', 'img_2_0802', 'img_2_0725']
    input_df = pd.read_csv(os.path.join(DATA_DIR, "task-b2.tsv"), sep='\t')
    output_df = pd.read_csv(os.path.join(OUTPUT_DIR, "task-b2.tsv"), sep='\t')
    
    to_generate = input_df[input_df['id'].isin(missing_ids)]
    
    new_results = []
    for _, row in tqdm(to_generate.iterrows(), total=len(to_generate)):
        id_val = row['id']
        user_input = f"Prompt: {row.get('prompt', '')}"
        vision_url = row.get('url')
        
        text = generate_humor(id_val, user_input, "task_b2.j2", vision_url=vision_url)
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        new_results.append({'id': id_val, 'text': text})
        time.sleep(1)

    # Update output_df
    new_df = pd.DataFrame(new_results)
    output_df = output_df.set_index('id')
    new_df = new_df.set_index('id')
    output_df.update(new_df)
    output_df.reset_index().to_csv(os.path.join(OUTPUT_DIR, "task-b2.tsv"), sep='\t', index=False)

if __name__ == "__main__":
    fix_7()
