import streamlit as st
import pandas as pd
import os
import baseline_generator as gen
import requests
import hashlib
from pathlib import Path
from jinja2 import Environment

st.set_page_config(page_title="MWAHAHA Interactive Visualizer", layout="wide")

DATA_DIR = "data"
OUTPUT_DIR = "output"
TEMPLATE_DIR = "templates"
CACHE_DIR = "gif_cache"

# Create cache directory if it doesn't exist
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cached_gif(url):
    """Downloads a GIF and returns the local path. Returns the URL if download fails."""
    if not url or not isinstance(url, str) or not url.startswith("http"):
        return url
    
    # Create hash of URL for unique filename
    url_hash = hashlib.md5(url.encode()).hexdigest()
    # Try to guess extension or default to .gif
    ext = os.path.splitext(url)[1]
    if not ext or len(ext) > 5:
        ext = ".gif"
    
    local_filename = f"{url_hash}{ext}"
    local_path = os.path.join(CACHE_DIR, local_filename)
    
    if os.path.exists(local_path):
        return local_path
    
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return local_path
    except Exception as e:
        st.warning(f"Failed to cache GIF: {e}")
    
    return url

def load_template(filename):
    path = os.path.join(TEMPLATE_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def save_template(filename, content):
    path = os.path.join(TEMPLATE_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    st.success(f"Saved to {filename}")

def on_task_change():
    # Clear session state when task changes
    for key in ['test_result', 'rendered_prompt', 'selected_row_index', 'last_selected_row', 'template_content']:
        if key in st.session_state:
            del st.session_state[key]

def main():
    st.title("🎭 MWAHAHA: Interactive Humor Visualizer")
    
    # --- Sidebar Selection ---
    st.sidebar.header("Configuration")
    
    # OpenAI API Key Input
    env_key = os.getenv("OPENAI_API_KEY", "")
    placeholder = f"SK-{env_key[:4]}..." if env_key else "Enter OpenAI API Key"
    api_key = st.sidebar.text_input("OpenAI API Key", type="password", placeholder=placeholder)
    
    # Model Selection
    model_choice = st.sidebar.selectbox("Model Selection", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"], index=0)
    
    # Update Backend Config
    if api_key or model_choice:
        gen.set_config(api_key=api_key if api_key else env_key, model=model_choice)

    st.sidebar.divider()
    st.sidebar.header("Task Selection")
    task_files = {
        "None": None,
        "Task A (EN)": "task-a-en.tsv",
        "Task A (ES)": "task-a-es.tsv",
        "Task A (ZH)": "task-a-zh.tsv",
        "Task B1 (GIF)": "task-b1.tsv",
        "Task B2 (GIF+Prompt)": "task-b2.tsv"
    }
    task_label = st.sidebar.selectbox("Choose Task", list(task_files.keys()), index=0, on_change=on_task_change)
    filename = task_files[task_label]
    
    if filename is None:
        # --- Landing Page ---
        with st.container(border=True):
            st.markdown(f"""
            ### 👋 Welcome to the MWAHAHA Interactive Visualizer!
            
            This tool helps you explore the SemEval 2026 Humor dataset and refine your prompt templates.
            
            #### 🛠 Setup & Browser:
            1. **API Key**: Currently using: `{placeholder}`. You can override it in the sidebar.
            2. **Model**: Using `{model_choice}`.
            3. **Select a Task**: Choose a task from the sidebar to get started!
            
            #### 🏁 Workflow:
            - **Browse**: Explore entries and sort/search the dataset.
            - **Edit**: Use the live Jinja2 template editor to craft your humor logic.
            - **Test**: See real-time results from the LLM.
            - **Batch**: Run your finalized prompt on the entire task.
            
            ---
            > [!TIP]
            > **Multimodal Support**: For Task B, the app handles GIF visuals and local caching automatically!
            """)
        return
    
    template_map = {
        "task-a-en.tsv": "task_a_en.j2",
        "task-a-es.tsv": "task_a_es.j2",
        "task-a-zh.tsv": "task_a_zh.j2",
        "task-b1.tsv": "task_b1.j2",
        "task-b2.tsv": "task_b2.j2"
    }
    template_filename = template_map[filename]
    
    # Load Data
    input_df = pd.read_csv(os.path.join(DATA_DIR, filename), sep='\t')
    
    # Load Output Data if exists to show in table
    output_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(output_path):
        try:
            out_df = pd.read_csv(output_path, sep='\t')
            # Merge to show current saved text
            display_df = input_df.merge(out_df, on='id', how='left')
        except:
            display_df = input_df.copy()
            display_df['text'] = ""
    else:
        display_df = input_df.copy()
        display_df['text'] = ""

    # --- 1. Table with Input and Output ---
    st.subheader(f"📊 Dataset: {task_label}")
    
    column_config = {
        "id": st.column_config.TextColumn("ID", width="small"),
        "text": st.column_config.TextColumn("Saved Output", width="large")
    }
    
    if "task-b" in filename:
        # Cache thumbnails for display if needed
        # Note: streamlit's ImageColumn works better with URLs for performance in large tables, 
        # but for individual display we definitely want the cache.
        # We can also pre-cache the whole column if we want.
        column_config["url"] = st.column_config.ImageColumn("Thumbnail", help="GIF Thumbnail")
    
    # Reorder columns for better visibility
    cols = ['id']
    if "task-b" in filename:
        cols.append('url')
        if "b2" in filename:
            cols.append('prompt')
    else:
        if 'headline' in display_df.columns:
            cols.append('headline')
        if 'word1' in display_df.columns:
            cols.extend(['word1', 'word2'])
    
    if 'text' in display_df.columns:
        cols.append('text')
    
    # Dataframe with selection
    event = st.dataframe(
        display_df[cols],
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    selected_rows = event.get("selection", {}).get("rows", [])
    
    if not selected_rows:
        st.info("👆 Select a row in the table above to test prompts.")
    else:
        # Process Selection
        row_idx = selected_rows[0]
        selected_row = display_df.iloc[row_idx]
        
        # Check if row selection changed to clear test results if needed
        if st.session_state.get('last_selected_row_idx') != row_idx:
            st.session_state.last_selected_row_idx = row_idx
            if 'test_result' in st.session_state:
                del st.session_state.test_result
            if 'rendered_prompt' in st.session_state:
                del st.session_state.rendered_prompt

        st.divider()
        
        # --- 2. Prompt Editor and Test Button ---
        st.subheader(f"🛠️ Testing Row: `{selected_row['id']}`")
        
        # Load Template
        if 'template_content' not in st.session_state:
            st.session_state.template_content = load_template(template_filename)

        col_edit, col_details = st.columns([2, 1])
        
        with col_details:
            with st.container(border=True):
                st.markdown("**Data Details**")
                if "task-b" in filename:
                    cached_path = get_cached_gif(selected_row['url'])
                    st.image(cached_path, caption="Input GIF (Cached)", use_container_width=True)
                    if "b2" in filename:
                        st.info(f"**Context Prompt:** {selected_row['prompt']}")
                else:
                    for col in display_df.columns:
                        if col not in ['id', 'text', 'url']:
                            st.markdown(f"**{col.capitalize()}:** {selected_row[col]}")
                
                # Show Previous Response if available
                prev_text = selected_row.get('text', "")
                if pd.notna(prev_text) and prev_text:
                    st.markdown("---")
                    st.markdown("**Previous Response:**")
                    st.info(prev_text)

        with col_edit:
            new_template = st.text_area("Jinja2 Template Editor", value=st.session_state.template_content, height=250)
            st.session_state.template_content = new_template
            
            if st.button("🚀 Test Prompt", use_container_width=True):
                with st.spinner("Generating..."):
                    user_input = gen.format_user_input(selected_row, filename)
                    prompt = gen.get_rendered_prompt(template_filename, user_input, template_content=st.session_state.template_content)
                    
                    vision_url = selected_row.get('url') if "task-b" in filename else None
                    if vision_url:
                        vision_url = get_cached_gif(vision_url)
                    
                    result = gen.generate_humor(prompt, vision_url=vision_url)
                    st.session_state.test_result = result
                    st.session_state.rendered_prompt = prompt

        # --- 3. Results Section ---
        if 'test_result' in st.session_state:
            st.markdown("---")
            res_c1, res_c2 = st.columns([1, 1])
            with res_c1:
                st.markdown("**Rendered Prompt:**")
                st.code(st.session_state.rendered_prompt, language="text")
            with res_c2:
                st.markdown("**LLM Output:**")
                if st.session_state.test_result.startswith("ERROR"):
                    st.error(st.session_state.test_result)
                else:
                    st.success(st.session_state.test_result)

            # --- 4. Action Buttons (Save/Run All) ---
            st.divider()
            st.markdown("### ⚡ Actions")
            act_c1, act_c2 = st.columns(2)
            
            if act_c1.button("💾 Save Template", use_container_width=True):
                save_template(template_filename, st.session_state.template_content)
                
            if act_c2.button("🔥 Run All & Save Output", use_container_width=True):
                with st.spinner(f"Processing all {len(input_df)} rows..."):
                    save_template(template_filename, st.session_state.template_content)
                    gen.process_task(filename, template_filename)
                    st.balloons()
                    st.success(f"Batch processing complete! Output saved to `{output_path}`")
                    st.rerun() # Rerun to refresh the main table with new outputs

if __name__ == "__main__":
    main()
