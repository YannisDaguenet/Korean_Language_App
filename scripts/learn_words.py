# %%
# This script provides an interactive word-by-word vocabulary review system based on a ranked 
# Korean word frequency list. It loads previously saved known and unknown word sets (if they exist),
# and reads a CSV file containing pre-tokenized and ranked Korean words.
# For each word, the user is asked whether they know it ('y'), don't know it ('n'), or want to quit ('q').
# The results are stored persistently in JSON files and can be downloaded after the session.

import os
import json
import pandas as pd
from IPython.display import display, clear_output
import ipywidgets as widgets
from pathlib import Path

# ✅ File paths
BASE_DIR = Path("../data")  # adjust as needed
known_words_path = BASE_DIR / "json" / "known_words_tokenized.json"
unknown_words_path = BASE_DIR / "json" / "unknown_words.json"
word_freq_path = BASE_DIR / "vocab" / "korean_token_frequency.csv"

# ✅ Load known/unknown words
def load_words(path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_words(words, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sorted(list(words)), f, ensure_ascii=False, indent=2)

known_words = load_words(known_words_path)
unknown_words = load_words(unknown_words_path)

# ✅ Load frequency dataset
df = pd.read_csv(word_freq_path)
tokens = df["token"].tolist()

# Remove already reviewed tokens
tokens = [t for t in tokens if t not in known_words and t not in unknown_words]

# ✅ Set up widgets
token_label = widgets.HTML(value="")
known_button = widgets.Button(description="✅ Known", button_style='success')
unknown_button = widgets.Button(description="❌ Unknown", button_style='danger')
quit_button = widgets.Button(description="⏹️ Quit", button_style='warning')
progress = widgets.Label()
button_box = widgets.HBox([known_button, unknown_button, quit_button])
display_box = widgets.VBox([token_label, button_box, progress])

# ✅ Logic for reviewing
index = 0
reviewed = 0

def update_display():
    if index < len(tokens):
        token_label.value = f"<h2>{tokens[index]}</h2>"
        progress.value = f"Token {index + 1} of {len(tokens)}"
    else:
        finish_review()

def on_known_clicked(b):
    global index, reviewed
    known_words.add(tokens[index])
    index += 1
    reviewed += 1
    update_display()

def on_unknown_clicked(b):
    global index, reviewed
    unknown_words.add(tokens[index])
    index += 1
    reviewed += 1
    update_display()

def on_quit_clicked(b):
    finish_review()

def finish_review():
    global index
    # Save progress
    save_words(known_words, known_words_path)
    save_words(unknown_words, unknown_words_path)
    
    # Disable buttons
    known_button.disabled = True
    unknown_button.disabled = True
    quit_button.disabled = True
    
    # Clear token display
    token_label.value = ""
    progress.value = ""
    
    # Final message
    clear_output()
    display(widgets.HTML(
        f"<h3>✅ Review complete. {reviewed} tokens reviewed.</h3>"
        f"<p>📁 Files saved to:</p>"
        f"<ul><li>{known_words_path.resolve()}</li><li>{unknown_words_path.resolve()}</li></ul>"
    ))

known_button.on_click(on_known_clicked)
unknown_button.on_click(on_unknown_clicked)
quit_button.on_click(on_quit_clicked)

# ✅ Start interface
if tokens:
    display(display_box)
    update_display()
else:
    print("🎉 All tokens have already been reviewed!")

# %%
