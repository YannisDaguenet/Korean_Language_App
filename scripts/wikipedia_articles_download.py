# This code sets up a Korean WIkipedia API, loads a list of selected wikipedia article titles and extracts paragraphs from each article.
#   It fetches the full article text and splits the article into paragraphs by newline characters and filters out empty lines. 
#   By looping over each titles, it populates a dictionary, mapping paragraphs to their articles.
#   Finally, it saves the extracted paragraphs into a json file. 

# 📄 Extract paragraphs for selected articles from saved list
import wikipediaapi
import pandas as pd
import json
from tqdm import tqdm
from pathlib import Path

# 🌐 Set up Wikipedia API (Korean)
wiki_kr = wikipediaapi.Wikipedia(
    language='ko',
    user_agent='Yannis-KoreanCorpus/1.0 (contact: yannisdaguenet@gmail.com)'
)

# 📥 Load list of selected articles
JSON_DIR = Path("data/json")
input_file = JSON_DIR / "selected_articles.json"
output_file = JSON_DIR / "selected_wikipedia_paragraphs.json"

with open(input_file, "r", encoding="utf-8") as f:
    selected_titles = json.load(f)

# 🔍 Extract paragraphs
article_paragraphs = {}

def get_paragraphs(title):
    page = wiki_kr.page(title)
    if not page.exists():
        return []
    return [p.strip() for p in page.text.split("\n") if p.strip()]

for title in tqdm(selected_titles):
    paras = get_paragraphs(title)
    if paras:
        article_paragraphs[title] = paras

# 💾 Save extracted paragraphs
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(article_paragraphs, f, ensure_ascii=False, indent=2)

print(f"✅ Saved extracted paragraphs to: {output_file.resolve()}")
