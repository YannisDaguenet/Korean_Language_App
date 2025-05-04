# %%
# This script uploads a csv file containing wikipedia articles, and allows you to 
#   interactively select the wikipedia articles based on their titles. It saves the 
#   articles into a json and downloads it to be used in the words frequency creation script. 
#   For it to run properly, two options: 
#   "Run cell" above, or
#   right click on the script and 
#   "Run in interactive Window" -> "Run current file in interactive Window"

# article_selection_interface.py
import pandas as pd
import json
import ipywidgets as widgets
from IPython.display import display
from pathlib import Path

# Use absolute path based on your workspace root:
WORKSPACE_ROOT = Path("/Users/yannis.daguenet/Documents/korean_language_app")

DATA_DIR = WORKSPACE_ROOT / "data/content"
JSON_DIR = WORKSPACE_ROOT / "data/json"
JSON_DIR.mkdir(parents=True, exist_ok=True)

# --- Setup file paths ---
DATA_DIR = Path("data/content")
JSON_DIR = Path("data/json")
JSON_DIR.mkdir(parents=True, exist_ok=True)

# --- Load your cleaned Wikipedia article list ---
csv_file = DATA_DIR / "wikipedia_korean_articles_cleaned.csv"

if not csv_file.exists():
    raise FileNotFoundError(f"⚠️ CSV file not found: {csv_file.resolve()}")

df = pd.read_csv(csv_file)

# --- Preview loaded DataFrame ---
print("✅ Loaded CSV successfully. Previewing first 10 entries:")
display(df[['title_ko', 'title_final']].head(10))

# --- Interactive selection with ipywidgets ---
df['combined'] = df['title_ko'] + " — " + df['title_final']
options = df['combined'].tolist()

selector = widgets.SelectMultiple(
    options=options,
    description='Select',
    rows=20,
    layout=widgets.Layout(width='100%')
)

save_button = widgets.Button(description="💾 Save selected titles to JSON", button_style='success')
output = widgets.Output()

def save_selected_titles(b):
    selected_korean = [item.split(" — ")[0] for item in selector.value]
    json_file = JSON_DIR / "selected_articles.json"
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(selected_korean, f, ensure_ascii=False, indent=2)
    
    with output:
        output.clear_output()
        print(f"✅ Saved {len(selected_korean)} articles to {json_file.resolve()}")

display(widgets.VBox([selector, save_button, output]))
save_button.on_click(save_selected_titles)

# %%
