# %%
# main.py - Full interactive notebook workflow for Korean learning

import json
from pathlib import Path
from IPython.display import display, clear_output
import ipywidgets as widgets

# Paths
BASE_DIR = Path("data")
JSON_DIR = BASE_DIR / "json"
CONTENT_DIR = BASE_DIR / "content"
VOCAB_DIR = BASE_DIR / "vocab"

# Create folders if missing
for d in [JSON_DIR, CONTENT_DIR, VOCAB_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# --- Step 1: ARTICLE SELECTION ---
def launch_article_selector():
    import pandas as pd
    csv_file = CONTENT_DIR / "wikipedia_korean_articles_cleaned.csv"
    print("🔍 Looking for CSV at:", csv_file.resolve())
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV not found: {csv_file}")

    df = pd.read_csv(csv_file)
    df['combined'] = df['title_ko'] + " — " + df['title_final']
    options = df['combined'].tolist()

    selector = widgets.SelectMultiple(
        options=options,
        description='Articles',
        rows=20,
        layout=widgets.Layout(width='100%')
    )
    save_btn = widgets.Button(description="💾 Save Selection", button_style='success')
    output = widgets.Output()

    def on_save(b):
        selected = [s.split(" — ")[0] for s in selector.value]
        with (JSON_DIR / "selected_articles.json").open("w", encoding="utf-8") as f:
            json.dump(selected, f, ensure_ascii=False, indent=2)
        with output:
            output.clear_output()
            print(f"✅ {len(selected)} article titles saved.")
            download_paragraphs()

    save_btn.on_click(on_save)
    display(widgets.VBox([selector, save_btn, output]))

# --- Step 2: DOWNLOAD WIKIPEDIA PARAGRAPHS ---
def download_paragraphs():
    import wikipediaapi
    from tqdm.notebook import tqdm

    wiki_kr = wikipediaapi.Wikipedia(language='ko', user_agent='Yannis-KoreanCorpus/1.0')
    input_file = JSON_DIR / "selected_articles.json"
    output_file = JSON_DIR / "selected_wikipedia_paragraphs.json"

    with input_file.open("r", encoding="utf-8") as f:
        titles = json.load(f)

    data = {}
    for title in tqdm(titles):
        page = wiki_kr.page(title)
        if page.exists():
            paras = [p.strip() for p in page.text.split("\n") if p.strip()]
            if paras:
                data[title] = paras

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ Wikipedia paragraphs downloaded.")
    choose_next_action()

# --- Step 3: CHOOSE ACTION ---
def choose_next_action():
    prompt = widgets.HTML("<h3>What would you like to do next?</h3>")
    learn_btn = widgets.Button(description="🔤 Learn New Words", button_style='info')
    read_btn = widgets.Button(description="📘 Read Adapted Text", button_style='primary')
    box = widgets.HBox([learn_btn, read_btn])

    def on_learn(b):
        clear_output()
        from learn_words import launch_review
        launch_review(callback=choose_next_action)

    def on_read(b):
        clear_output()
        from get_adapted_text import launch_adapted_reader
        launch_adapted_reader(fallback=choose_next_action)

    learn_btn.on_click(on_learn)
    read_btn.on_click(on_read)

    display(widgets.VBox([prompt, box]))

# --- Launch ---
launch_article_selector()

# %%
