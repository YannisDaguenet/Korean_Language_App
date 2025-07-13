# %%
import json
import re
import pandas as pd
from pathlib import Path
from collections import Counter
from konlpy.tag import Okt
from IPython.display import display, clear_output
import ipywidgets as widgets

# ✅ Paths & load data
DATA_DIR = Path("data")
lyrics_file = DATA_DIR / "content박소은_lyrics.json"
known_words_path = DATA_DIR / "json/known_words_tokenized.json"
unknown_words_path = DATA_DIR / "json/unknown_words.json"
seen_sentences_path = DATA_DIR / "json/seen_sentences.json"

def load_words(path):
    return set(json.load(open(path, encoding="utf-8"))) if path.exists() else set()

def save_words(words, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sorted(list(words)), f, ensure_ascii=False, indent=2)

with open(lyrics_file, "r", encoding="utf-8") as f:
    lyrics_data = json.load(f)

known_words = load_words(known_words_path)
unknown_words = load_words(unknown_words_path)
seen_sentences = load_words(seen_sentences_path)

okt = Okt()

# ✅ Interactive dropdowns
artist_list = sorted(set(song["Artist"] for song in lyrics_data))
artist_dropdown = widgets.Dropdown(options=artist_list, description="🎤 Artist")
song_dropdown = widgets.Dropdown(description="🎵 Song")

def update_songs(change):
    selected_artist = artist_dropdown.value
    song_dropdown.options = [song["Song Name"] for song in lyrics_data if song["Artist"] == selected_artist]

artist_dropdown.observe(update_songs, names='value')
update_songs(None)

mode_dropdown = widgets.Dropdown(
    options=["Learn Words", "Read Paragraphs"],
    description="📚 Mode"
)
launch_button = widgets.Button(description="🚀 Start Session", button_style='success')

# ✅ Launch session
def launch_session(b):
    clear_output()
    selected_artist = artist_dropdown.value
    selected_song = song_dropdown.value
    lyrics_text = next(song["Lyrics"] for song in lyrics_data
                       if song["Artist"] == selected_artist and song["Song Name"] == selected_song)
    if mode_dropdown.value == "Learn Words":
        launch_word_review(lyrics_text)
    else:
        ask_to_read_paragraphs(lyrics_text)

launch_button.on_click(launch_session)
display(widgets.VBox([artist_dropdown, song_dropdown, mode_dropdown, launch_button]))

# ✅ Vocab review session
def launch_word_review(lyrics_text):
    tokens = okt.morphs(lyrics_text)
    tokens = [t for t in tokens if re.search(r"[가-힣]", t) and len(t) > 1]
    token_list = [t for t, _ in Counter(tokens).most_common()
                  if t not in known_words and t not in unknown_words]

    print(f"✅ Found {len(token_list)} new words.")
    if len(token_list) < 10:
        ask_to_review_unknowns_in_paragraphs(lyrics_text)
    else:
        start_token_review_session(token_list, lyrics_text)

def ask_to_review_unknowns_in_paragraphs(lyrics_text):
    paragraph_tokens = okt.morphs(lyrics_text)
    paragraph_tokens = [t for t in paragraph_tokens if re.search(r"[가-힣]", t) and len(t) > 1]
    unknown_tokens = list(dict.fromkeys([t for t in paragraph_tokens if t in unknown_words]))

    print(f"✅ Found {len(unknown_tokens)} previously unknown words.")
    yes_button = widgets.Button(description="✅ Yes, review", button_style='success')
    no_button = widgets.Button(description="🚫 No thanks", button_style='danger')

    def on_yes(b):
        clear_output()
        start_token_review_session(unknown_tokens, lyrics_text)
    def on_no(b):
        clear_output()
        ask_to_read_paragraphs(lyrics_text)

    display(widgets.VBox([
        widgets.HTML("<h4>⚠️ Less than 10 new words. Want to review previous unknown words instead?</h4>"),
        widgets.HBox([yes_button, no_button])
    ]))
    yes_button.on_click(on_yes)
    no_button.on_click(on_no)

def start_token_review_session(token_list, lyrics_text):
    index = 0
    reviewed = 0

    token_label = widgets.HTML()
    progress = widgets.Label()
    known_button = widgets.Button(description="✅ Known", button_style='success')
    unknown_button = widgets.Button(description="❌ Unknown", button_style='danger')
    quit_button = widgets.Button(description="⏹️ Quit", button_style='warning')

    def update_display():
        if index < len(token_list):
            token_label.value = f"<h2>{token_list[index]}</h2>"
            progress.value = f"Token {index + 1} of {len(token_list)}"
        else:
            finish_review()

    def finish_review():
        save_words(known_words, known_words_path)
        save_words(unknown_words, unknown_words_path)
        clear_output()
        display(widgets.HTML(
            f"<h3>✅ Review complete ({reviewed} tokens).</h3>"
            f"<ul><li>{known_words_path.name}</li><li>{unknown_words_path.name}</li></ul>"
        ))
        ask_to_read_paragraphs(lyrics_text)

    def on_known(b):
        nonlocal index, reviewed
        known_words.add(token_list[index])
        index += 1
        reviewed += 1
        update_display()
    def on_unknown(b):
        nonlocal index, reviewed
        unknown_words.add(token_list[index])
        index += 1
        reviewed += 1
        update_display()
    def on_quit(b):
        finish_review()

    known_button.on_click(on_known)
    unknown_button.on_click(on_unknown)
    quit_button.on_click(on_quit)

    display(widgets.VBox([token_label, widgets.HBox([known_button, unknown_button, quit_button]), progress]))
    update_display()

# ✅ Choose paragraph bin to read
def ask_to_read_paragraphs(lyrics_text):
    lines = [line.strip() for line in lyrics_text.split("\n") if line.strip()]
    paragraphs = ["\n".join(lines[i:i+7]) for i in range(0, len(lines), 7)]
    df = pd.DataFrame(paragraphs, columns=["korean"])

    def korean_known_coverage(text):
        tokens = okt.morphs(text)
        tokens = [t for t in tokens if re.search(r"[가-힣]", t) and len(t) > 1]
        known = [t for t in tokens if t in known_words]
        return len(known) / len(tokens) * 100 if tokens else 0

    df["coverage"] = df["korean"].apply(korean_known_coverage)
    bins = [0,20,40,60,80,92.9,97,100]
    labels = ["0-20%","20-40%","40-60%","60-80%","80-92.9%","93-97%","97-100%"]
    df["coverage_bin"] = pd.cut(df["coverage"], bins=bins, labels=labels, include_lowest=True)
    dist = df["coverage_bin"].value_counts().sort_index()

    bin_buttons = []
    for label in labels:
        count = dist.get(label, 0)
        btn = widgets.Button(description=f"{label} ({count})",
                             button_style='info' if count > 0 else '',
                             disabled=bool(count == 0))
        def make_onclick(l):
            return lambda b: launch_paragraph_reader_for_bin(df, l)
        btn.on_click(make_onclick(label))
        bin_buttons.append(btn)

    display(widgets.HTML("<h4>📊 Click on a coverage range to start reading paragraphs in that range:</h4>"))
    display(widgets.VBox([widgets.HBox(bin_buttons[i:i+3]) for i in range(0, len(bin_buttons), 3)]))
    skip_button = widgets.Button(description="🚫 Skip", button_style='warning')
    skip_button.on_click(lambda b: (clear_output(), print("👍 Session complete.")))
    display(skip_button)

# ✅ Launch reading paragraphs in selected bin
def launch_paragraph_reader_for_bin(df, coverage_label):
    clear_output()
    filtered_df = df[df["coverage_bin"] == coverage_label].reset_index(drop=True)

    if filtered_df.empty:
        print(f"😕 No paragraphs found in range {coverage_label}.")
        return

    index = 0

    def review_block():
        nonlocal index
        clear_output()
        if index >= len(filtered_df):
            save_words(seen_sentences, seen_sentences_path)
            save_words(known_words, known_words_path)
            save_words(unknown_words, unknown_words_path)
            print(f"🎉 Finished reading all paragraphs in {coverage_label}.")
            return

        para = filtered_df.iloc[index]["korean"]
        tokens = okt.morphs(para)
        tokens = [t for t in tokens if re.search(r"[가-힣]", t) and len(t) > 1]

        # local state of word statuses
        word_status = {}
        for t in tokens:
            if t in known_words:
                word_status[t] = 'green'
            elif t in unknown_words:
                word_status[t] = 'red'
            else:
                word_status[t] = 'grey'

        # create buttons
        buttons = []
        for t in tokens:
            btn = widgets.Button(description=t, 
                                 layout=widgets.Layout(width='auto', height='auto', padding='1px', margin='1px'),
                                 style={'button_color': color_for_status(word_status[t])})
            def make_onclick(word):
                def on_click(b):
                    current = word_status[word]
                    new_state = next_status(current)
                    word_status[word] = new_state
                    b.style.button_color = color_for_status(new_state)
                return on_click
            btn.on_click(make_onclick(t))
            buttons.append(btn)

        # display horizontally wrapping
        button_grid = widgets.HBox()
        rows = []
        row_size = 8
        for i in range(0, len(buttons), row_size):
            rows.append(widgets.HBox(buttons[i:i+row_size]))
        button_grid = widgets.VBox(rows)

        mark_button = widgets.Button(description="📌 Mark Seen & Next", button_style='success')
        next_button = widgets.Button(description="➡️ Next (don't mark)", button_style='info')

        def on_mark(b):
            seen_sentences.add(para)
            update_global_word_lists()
            move_next()
        def on_next(b):
            update_global_word_lists()
            move_next()

        def update_global_word_lists():
            for word, status in word_status.items():
                if status == 'green':
                    known_words.add(word)
                    unknown_words.discard(word)
                elif status == 'red':
                    unknown_words.add(word)
                    known_words.discard(word)
                # grey does nothing

        def move_next():
            nonlocal index
            index += 1
            review_block()

        mark_button.on_click(on_mark)
        next_button.on_click(on_next)
        display(widgets.VBox([
            widgets.HTML(f"<pre style='font-size:16px'>{para}</pre>"),
            button_grid,
            widgets.HBox([mark_button, next_button])
        ]))

    def color_for_status(status):
        if status == 'green': return 'lightgreen'
        elif status == 'red': return 'lightcoral'
        else: return 'lightgrey'

    def next_status(current):
        if current == 'grey': return 'green'
        if current == 'green': return 'red'
        return 'grey'

    review_block()

# %%
