# %%
# This script provides an interactive sentence block review interface for Korean learners using ipywidgets.
# It loads paragraphs from a Wikipedia paragraph dataset, computes token-level coverage using the Okt tokenizer,
# and selects blocks with 93–97% known word coverage. Sentence blocks are shown one at a time, and the user can
# mark words as known or unknown via toggle buttons. The app updates progress with a progress bar and saves
# session data to persistent JSON files.

# 📁 Imports
import os
import json
import pandas as pd
from pathlib import Path
from konlpy.tag import Okt
from IPython.display import display, clear_output
import ipywidgets as widgets
import matplotlib.pyplot as plt
import threading

# ✅ File paths
BASE_DIR = Path("data")
known_path = BASE_DIR / "json" / "known_words_tokenized.json"
unknown_path = BASE_DIR / "json" / "unknown_words.json"
seen_path = BASE_DIR / "json" / "seen_sentences.json"
json_path = BASE_DIR / "json" / "selected_wikipedia_paragraphs.json"

# ✅ Load + Save helpers
def load_json_set(path):
    return set(json.load(open(path, encoding='utf-8'))) if path.exists() else set()

def save_json_set(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sorted(list(data)), f, ensure_ascii=False, indent=2)

known_words = load_json_set(known_path)
unknown_words = load_json_set(unknown_path)
seen_sentences = load_json_set(seen_path)

# ✅ Load Wikipedia paragraph dataset
with open(json_path, "r", encoding="utf-8") as f:
    wiki_paragraphs = json.load(f)

paragraphs = [para.strip() for paras in wiki_paragraphs.values() for para in paras if para.strip()]
df = pd.DataFrame(paragraphs, columns=["korean"])

# ✅ Tokenizer + coverage
okt = Okt()

def korean_known_coverage(text):
    tokens = okt.morphs(str(text))
    if not tokens:
        return 0
    known = [t for t in tokens if t in known_words]
    return len(known) / len(tokens) * 100

df["coverage"] = df["korean"].apply(korean_known_coverage)

# ✅ Filter eligible sentence blocks
eligible_df = df[(df["coverage"] >= 93) & (df["coverage"] <= 97) & (~df["korean"].isin(seen_sentences))].reset_index(drop=True)

# 🔢 Coverage statistics
bins = [0, 0.1, 20, 30, 40, 50, 60, 70, 80, 90, 92.9, 97, 99.9, 100]
labels = [
    "0%", "0.1%-20%", "20.1%-30%", "30.1%-40%", "40.1%-50%", "50.1%-60%",
    "60.1%-70%", "70.1%-80%", "80.1%-90%", "90.1%-92.9%", "93%-97%",
    "97.1%-99.9%", "100%"
]
df["coverage_range"] = pd.cut(df["coverage"], bins=bins, labels=labels, right=True, include_lowest=True)

coverage_distribution = df["coverage_range"].value_counts().sort_index()
print("\n📊 Distribution of sentence blocks by known word coverage:")
for label, count in coverage_distribution.items():
    print(f"{label:>12}: {count}")

# Optional: Show as bar chart with timeout fallback
import time
if not hasattr(plt, 'get_backend') or 'inline' not in plt.get_backend().lower():
    plt.use('Agg')  # Safe fallback for non-notebook environments

def attempt_plot():
    try:
        plt.figure(figsize=(10, 5))
        coverage_distribution.plot(kind="bar", color="#4caf50")
        plt.title("Distribution of Sentence Blocks by Known Word Coverage")
        plt.ylabel("Number of Blocks")
        plt.xlabel("Coverage Range")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"⚠️ Could not plot chart: {e}")

plot_thread = threading.Thread(target=attempt_plot)
plot_thread.start()
plot_thread.join(timeout=15)
if plot_thread.is_alive():
    print("⚠️ Plotting timed out. Showing stats as text only.")
    plot_thread.join(0)

# ✅ Build the interface
class TokenButton(widgets.Button):
    def __init__(self, token):
        super().__init__(description=token)
        self.token = token
        self.state = "neutral"
        self.layout.width = 'auto'
        self.style.font_weight = 'bold'
        self.update_color()
        self.on_click(self.toggle_state)

    def toggle_state(self, b):
        if self.state == "neutral":
            self.state = "known"
        elif self.state == "known":
            self.state = "unknown"
        else:
            self.state = "neutral"
        self.update_color()

    def update_color(self):
        colors = {"neutral": "#616161", "known": "#2e7d32", "unknown": "#c62828"}
        self.style.button_color = colors[self.state]

# ✅ Main review function
index = 0

def review_block():
    global index
    clear_output()

    if index >= len(eligible_df):
        print("🎉 No more eligible sentence blocks to review.")
        save_all()
        return

    row = eligible_df.iloc[index]
    sentence = row["korean"]
    tokens = okt.morphs(sentence)
    new_tokens = [t for t in tokens if t not in known_words]

    # Skip block if all tokens already known
    if not new_tokens:
        seen_sentences.add(sentence)
        index += 1
        return review_block()

    # UI Elements
    sentence_label = widgets.HTML(f"<b>📝 Sentence {index+1}/{len(eligible_df)}</b><br><i>{sentence}</i>")
    token_buttons = [TokenButton(t) for t in new_tokens]
    rows = [widgets.HBox(token_buttons[i:i+8]) for i in range(0, len(token_buttons), 8)]
    token_box = widgets.VBox(rows)

    # Progress bar
    progress = widgets.IntProgress(
        value=len(seen_sentences),
        min=0,
        max=len(df[(df["coverage"] >= 93) & (df["coverage"] <= 97)]),
        description='Progress:',
        bar_style='info',
        style={'bar_color': '#2e7d32'},
        layout=widgets.Layout(width='100%')
    )

    # Buttons
    submit_button = widgets.Button(description="✅ Submit", button_style='success')
    exit_button = widgets.Button(description="🚪 Exit", button_style='danger')
    output = widgets.Output()

    def on_submit(b):
        for btn in token_buttons:
            if btn.state == "known":
                known_words.add(btn.token)
                unknown_words.discard(btn.token)
            elif btn.state == "unknown":
                unknown_words.add(btn.token)
        seen_sentences.add(sentence)
        save_all()
        index_increment()

    def on_exit(b):
        save_all()
        clear_output()
        print("👋 Review session saved and exited.")

    def index_increment():
        global index
        index += 1
        review_block()

    submit_button.on_click(on_submit)
    exit_button.on_click(on_exit)

    display(widgets.VBox([
        sentence_label,
        token_box,
        widgets.HBox([submit_button, exit_button]),
        progress,
        output
    ]))

# ✅ Save helper

def save_all():
    save_json_set(known_words, known_path)
    save_json_set(unknown_words, unknown_path)
    save_json_set(seen_sentences, seen_path)

def launch_adapted_reader(fallback=None):
    global index
    index = 0

    if eligible_df.empty:
        print("😕 No eligible sentence blocks found. Try learning more words first.")
        if fallback:
            fallback()
        return

    review_block()

launch_adapted_reader()