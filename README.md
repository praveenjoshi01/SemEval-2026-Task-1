# 🎭 MWAHAHA: Interactive Humor Visualizer

This project is a visual tool designed for the **SemEval 2026 Task: MWAHAHA (Multimodal Wit and Humor Analysis for Human-centric AI)**. It allows researchers and developers to interactively explore humor datasets, engineer prompts using Jinja2 templates, and test them against GPT models.

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- OpenAI API Key (configured in `.env`)

### Installation
1. Clone the repository.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
Launch the interactive visualizer using Streamlit:
```bash
.\venv\Scripts\streamlit.exe run streamlit_app.py
```

## 🛠 Configuration

On the **Sidebar**, you can configure:
- **OpenAI API Key**: If not provided in a `.env` file, you can enter it directly in the app. If a key exists in `.env`, the app will show a masked version (e.g., `SK-abcd...`).
- **Model Selection**: Switch between different OpenAI models (e.g., `gpt-4o-mini`, `gpt-4o`).

## 🛠 Features

- **Interactive Data Browser**: Browse through Task A (Text) and Task B (Multimodal/GIF) datasets.
- **GIF Caching**: Automatically caches GIFs locally to improve performance and reduce bandwidth.
- **Jinja2 Template Editor**: Real-time editing of prompt templates.
- **Live Testing**: Test your prompts on specific data points and see LLM outputs instantly.
- **Batch Processing**: Run your refined prompts on the entire dataset and save outputs for submission.

## 📂 Project Structure

- `streamlit_app.py`: The main UI application.
- `baseline_generator.py`: Backend logic for API interaction and template rendering.
- `data/`: Contains the task TSV files.
- `templates/`: Jinja2 prompt templates (`.j2`).
- `output/`: Generated results for submission.
- `gif_cache/`: Local cache for GIF files (automatically git-ignored).

---
*Developed for SemEval 2026.*
