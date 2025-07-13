# %%
import json
import re
import pandas as pd
import wikipediaapi
from pathlib import Path
from collections import Counter
from konlpy.tag import Okt
from IPython.display import display, clear_output
import ipywidgets as widgets

# ✅ Paths
WORKSPACE_ROOT = Path("/Users/yannis.daguenet/Documents/korean_language_app")  # adjust as needed
DATA_DIR = WORKSPACE_ROOT / "data"
JSON_DIR = DATA_DIR / "json"
JSON_DIR.mkdir(parents=True, exist_ok=True)

known_path = JSON_DIR / "known_words_tokenized.json"
unknown_path = JSON_DIR / "unknown_words.json"
seen_path = JSON_DIR / "seen_sentences.json"
articles_json = JSON_DIR / "selected_articles.json"
paragraphs_json = JSON_DIR / "selected_wikipedia_paragraphs.json"
csv_file = DATA_DIR / "content" / "wikipedia_korean_articles_cleaned.csv"

# ✅ Load JSON helpers
def load_json_set(path):
    return set(json.load(open(path, encoding="utf-8"))) if path.exists() else set()

def save_json_set(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sorted(list(data)), f, ensure_ascii=False, indent=2)

known_words = load_json_set(known_path)
unknown_words = load_json_set(unknown_path)
seen_sentences = load_json_set(seen_path)

okt = Okt()

# ✅ Start menu
def start_menu():
    clear_output()
    print("📚 Welcome to your Korean Wikipedia reading app!")
    btn_pick_articles = widgets.Button(description="📂 Select Wikipedia articles", button_style='info')
    btn_use_last = widgets.Button(description="🚀 Use last selected articles", button_style='success')
    btn_quit = widgets.Button(description="❌ Quit", button_style='danger')

    def on_pick(b):
        select_articles_interface(csv_file)
    def on_use_last(b):
        if articles_json.exists():
            with articles_json.open("r", encoding="utf-8") as f:
                selected_titles = json.load(f)
            extract_paragraphs(selected_titles)
        else:
            clear_output()
            print("⚠️ No previous articles found. Please select new ones.")
            select_articles_interface(csv_file)
    def on_quit(b):
        clear_output()
        print("👋 Goodbye!")

    btn_pick_articles.on_click(on_pick)
    btn_use_last.on_click(on_use_last)
    btn_quit.on_click(on_quit)

    display(widgets.VBox([
        widgets.HTML("<h3>What would you like to do?</h3>"),
        btn_pick_articles, btn_use_last, btn_quit
    ]))

# ✅ Select articles
def select_articles_interface(csv_file):
    df = pd.read_csv(csv_file)
    df['combined'] = df['title_ko'] + " — " + df['title_final']
    options = df['combined'].tolist()
    selector = widgets.SelectMultiple(options=options, rows=20, layout=widgets.Layout(width='100%'))
    save_button = widgets.Button(description="💾 Save selected", button_style='success')
    output = widgets.Output()

    def save_selected(b):
        selected_ko = [item.split(" — ")[0] for item in selector.value]
        with articles_json.open("w", encoding="utf-8") as f:
            json.dump(selected_ko, f, ensure_ascii=False, indent=2)
        with output:
            output.clear_output()
            print(f"✅ Saved {len(selected_ko)} articles to {articles_json.resolve()}")
        extract_paragraphs(selected_ko)

    save_button.on_click(save_selected)
    clear_output()
    display(widgets.VBox([selector, save_button, output]))

# ✅ Extract paragraphs from Wikipedia
def extract_paragraphs(selected_titles):
    wiki_kr = wikipediaapi.Wikipedia(language='ko', user_agent='Yannis-KoreanCorpus/1.0')
    article_paragraphs = {}
    for title in selected_titles:
        page = wiki_kr.page(title)
        if page.exists():
            paras = [p.strip() for p in page.text.split("\n") if p.strip()]
            if paras:
                article_paragraphs[title] = paras
    with paragraphs_json.open("w", encoding="utf-8") as f:
        json.dump(article_paragraphs, f, ensure_ascii=False, indent=2)
    print(f"✅ Extracted paragraphs saved to: {paragraphs_json.resolve()}")
    launch_top_menu()

# ✅ Learn words
def learn_words_from_articles():
    with open(paragraphs_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    all_text = "\n".join([para for paras in data.values() for para in paras])
    tokens = okt.morphs(all_text)
    token_freq = Counter([t for t in tokens if re.search(r"[가-힣]", t) and len(t) > 1])
    learn_list = [t for t, _ in token_freq.most_common() if t not in known_words and t not in unknown_words]
    run_word_review(learn_list)

def run_word_review(token_list):
    index, reviewed = 0, 0
    token_label = widgets.HTML()
    known_button = widgets.Button(description="✅ Known", button_style='success')
    unknown_button = widgets.Button(description="❌ Unknown", button_style='danger')
    quit_button = widgets.Button(description="🚪 Quit", button_style='warning')
    progress = widgets.Label()
    buttons = widgets.HBox([known_button, unknown_button, quit_button])
    display_box = widgets.VBox([token_label, buttons, progress])

    def update():
        if index < len(token_list):
            token_label.value = f"<h2>{token_list[index]}</h2>"
            progress.value = f"Token {index+1}/{len(token_list)}"
        else:
            finish()

    def finish():
        save_json_set(known_words, known_path)
        save_json_set(unknown_words, unknown_path)
        clear_output()
        print(f"✅ Word review done. {reviewed} tokens reviewed.")
        launch_top_menu()

    def on_known(b):
        nonlocal index, reviewed
        known_words.add(token_list[index])
        index += 1
        reviewed += 1
        update()

    def on_unknown(b):
        nonlocal index, reviewed
        unknown_words.add(token_list[index])
        index += 1
        reviewed += 1
        update()

    known_button.on_click(on_known)
    unknown_button.on_click(on_unknown)
    quit_button.on_click(lambda b: finish())
    clear_output()
    display(display_box)
    update()

# ✅ Top menu after paragraphs
def launch_top_menu():
    clear_output()
    btn_learn = widgets.Button(description="📚 Learn words first", button_style='success')
    btn_read = widgets.Button(description="📰 Read paragraphs by %", button_style='info')
    btn_quit = widgets.Button(description="🚪 Quit", button_style='danger')

    btn_learn.on_click(lambda b: learn_words_from_articles())
    btn_read.on_click(lambda b: select_coverage_bin())
    btn_quit.on_click(lambda b: (clear_output(), print("👋 Exited session.")))

    display(widgets.VBox([
        widgets.HTML("<h3>What would you like to do next?</h3>"),
        btn_learn, btn_read, btn_quit
    ]))

# ✅ Paragraph selection by % range
def select_coverage_bin():
    with open(paragraphs_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    paragraphs = [para.strip() for paras in data.values() for para in paras if para.strip()]
    df = pd.DataFrame(paragraphs, columns=["korean"])
    df["coverage"] = df["korean"].apply(lambda text: korean_known_coverage(text))
    bins = [0, 0.1, 20, 30, 40, 50, 60, 70, 80, 90, 92.9, 97, 99.9, 100]
    labels = ["0%", "0.1%-20%", "20.1%-30%", "30.1%-40%", "40.1%-50%", "50.1%-60%",
              "60.1%-70%", "70.1%-80%", "80.1%-90%", "90.1%-92.9%", "93%-97%",
              "97.1%-99.9%", "100%"]
    df["coverage_bin"] = pd.cut(df["coverage"], bins=bins, labels=labels, include_lowest=True)
    dist = df["coverage_bin"].value_counts().sort_index()

    clear_output()
    print("📊 Paragraphs coverage distribution:")
    for label, count in dist.items():
        print(f"{label:>12}: {count}")

    buttons = []
    for label in labels:
        count = dist.get(label, 0)
        btn = widgets.Button(description=f"{label} ({count})", 
                             button_style='info' if count > 0 else '',
                             disabled=bool(count == 0))
        def make_onclick(l):
            return lambda b: launch_paragraph_reader_for_bin(df, l)
        btn.on_click(make_onclick(label))
        buttons.append(btn)
    rows = [widgets.HBox(buttons[i:i+3]) for i in range(0, len(buttons), 3)]
    quit_btn = widgets.Button(description="🚪 Quit", button_style='danger')
    quit_btn.on_click(lambda b: (clear_output(), print("👋 Exited session.")))
    display(widgets.VBox(rows + [quit_btn]))

# ✅ Paragraph reader
def launch_paragraph_reader_for_bin(df, selected_bin):
    eligible_df = df[(df["coverage_bin"] == selected_bin) & (~df["korean"].isin(seen_sentences))].reset_index(drop=True)
    if eligible_df.empty:
        clear_output()
        print(f"😕 No paragraphs in {selected_bin}.")
        return launch_top_menu()
    index = 0
    def review_block():
        nonlocal index
        clear_output()
        if index >= len(eligible_df):
            save_json_set(seen_sentences, seen_path)
            save_json_set(known_words, known_path)
            save_json_set(unknown_words, unknown_path)
            print(f"✅ Finished {selected_bin}.")
            return launch_top_menu()
        para = eligible_df.iloc[index]["korean"]
        tokens = okt.morphs(para)
        tokens = [t for t in tokens if re.search(r"[가-힣]", t) and len(t) > 1]
        word_status = {t: ('green' if t in known_words else 'red' if t in unknown_words else 'grey') for t in tokens}
        buttons = []
        for t in tokens:
            btn = widgets.Button(description=t,
                                 layout=widgets.Layout(width='auto', height='auto', padding='1px', margin='1px'),
                                 style={'button_color': color_for_status(word_status[t])})
            def make_onclick(word):
                def on_click(b):
                    new = next_status(word_status[word])
                    word_status[word] = new
                    b.style.button_color = color_for_status(new)
                return on_click
            btn.on_click(make_onclick(t))
            buttons.append(btn)
        rows = [widgets.HBox(buttons[i:i+8]) for i in range(0, len(buttons), 8)]
        mark_btn = widgets.Button(description="📌 Mark Seen & Next", button_style='success')
        skip_btn = widgets.Button(description="➡️ Next", button_style='info')
        quit_btn = widgets.Button(description="🚪 Quit", button_style='danger')
        def on_mark(b):
            seen_sentences.add(para)
            update_globals()
            next_para()
        def on_skip(b):
            update_globals()
            next_para()
        def update_globals():
            for w, s in word_status.items():
                if s == 'green':
                    known_words.add(w)
                    unknown_words.discard(w)
                elif s == 'red':
                    unknown_words.add(w)
                    known_words.discard(w)
        def next_para():
            nonlocal index
            index += 1
            review_block()
        mark_btn.on_click(on_mark)
        skip_btn.on_click(on_skip)
        quit_btn.on_click(lambda b: (clear_output(), print("👋 Exited session.")))
        display(widgets.VBox([widgets.HTML(f"<pre>{para}</pre>")] + rows + [widgets.HBox([mark_btn, skip_btn, quit_btn])]))
    review_block()

def korean_known_coverage(text):
    tokens = okt.morphs(str(text))
    tokens = [t for t in tokens if re.search(r"[가-힣]", t) and len(t) > 1]
    known = [t for t in tokens if t in known_words]
    return len(known) / len(tokens) * 100 if tokens else 0
def color_for_status(s): return {'green': 'lightgreen', 'red': 'lightcoral', 'grey': 'lightgrey'}[s]
def next_status(c): return {'grey': 'green', 'green': 'red', 'red': 'grey'}[c]

# ✅ Go!
start_menu()
# %%
