# %%
# initialize_known_words.py
# This script helps bootstrap a known Korean vocabulary list for intermediate learners
# by allowing them to pre-load punctuation, grammar endings, and common verbs based on what they already know.

import json
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output
from pathlib import Path

# ✅ File paths
BASE_DIR = Path("data/json")
known_words_path = BASE_DIR / "known_words_tokenized.json"

BASE_DIR.mkdir(parents=True, exist_ok=True)

# ✅ Starter sets
punctuation = [".", ",", "(", ")", "!", "?", "\"", "'", ":"]
particles = ["은", "는", "이", "가", "에", "에서", "을", "를", "의"]
basic_verbs = ["하다", "가다", "오다", "보다", "있다", "없다", "먹다", "마시다"]
past_endings = ["았어요", "었어요", "였어요", "았어", "었어", "였어"]
polite_endings = ["아요", "어요", "해요"]

# ✅ User selections
known_words = set()

# ✅ Grammar questions
grammar_questions = {
    "Have you learned past tense?": past_endings,
    "Do you know the polite present tense?": polite_endings,
}

# ✅ UI Elements
punct_toggle = widgets.Checkbox(value=True, description="Add punctuation")
particles_toggle = widgets.Checkbox(value=True, description="Add topic/subject/object particles")
verbs_toggle = widgets.Checkbox(value=True, description="Add basic verbs")

grammar_boxes = {
    q: widgets.Checkbox(value=False, description=q) for q in grammar_questions
}

confirm_button = widgets.Button(description="✅ Generate Known Words", button_style='success')
output = widgets.Output()

# ✅ Interactive core word selection
def build_core_word_selector():
    # Load top frequency list if available
    try:
        df_freq = pd.read_csv("../data/vocab/korean_token_frequency.csv")
        top_tokens = df_freq["token"].head(30).tolist()
    except Exception:
        top_tokens = ["좋다", "예쁘다", "많이", "사람", "시간"]

    token_buttons = []
    for token in top_tokens:
        btn = widgets.ToggleButton(value=False, description=token)
        token_buttons.append(btn)

    rows = [widgets.HBox(token_buttons[i:i+8]) for i in range(0, len(token_buttons), 8)]
    return widgets.VBox(rows), token_buttons

word_ui, word_buttons = build_core_word_selector()

# ✅ Confirmation logic

def on_generate(b):
    known_words.clear()
    if punct_toggle.value:
        known_words.update(punctuation)
    if particles_toggle.value:
        known_words.update(particles)
    if verbs_toggle.value:
        known_words.update(basic_verbs)

    for q, box in grammar_boxes.items():
        if box.value:
            known_words.update(grammar_questions[q])

    for btn in word_buttons:
        if btn.value:
            known_words.add(btn.description)

    # Save to file
    with open(known_words_path, "w", encoding="utf-8") as f:
        json.dump(sorted(list(known_words)), f, ensure_ascii=False, indent=2)

    with output:
        clear_output()
        print(f"✅ Saved {len(known_words)} known words to {known_words_path.resolve()}")

confirm_button.on_click(on_generate)

# ✅ Layout
layout = widgets.VBox([
    widgets.HTML("<h3>🧠 Korean Known Word Initialization</h3>"),
    punct_toggle,
    particles_toggle,
    verbs_toggle,
    widgets.HTML("<b>📘 Grammar Features</b>"),
    *grammar_boxes.values(),
    widgets.HTML("<b>🔤 Top Morphemes — Toggle as Known</b>"),
    word_ui,
    confirm_button,
    output
])

display(layout)

# %%
