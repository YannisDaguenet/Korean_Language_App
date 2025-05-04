# This code loads pre-extracted wikipedia paragraphs, initializes a Korean tokenizer and runs it via loop through all paragraphs, 
#   in order to extract all morphemes and store their frequencies into a dataframe sorted from most to least frequent and saves it into a json.

import json
from pathlib import Path
from konlpy.tag import Okt
from collections import Counter
import pandas as pd

# ✅ Load the Wikipedia paragraph dataset
DATA_DIR = Path("data/json")  # adjust if needed
input_file = DATA_DIR / "selected_wikipedia_paragraphs.json"
output_file = Path("data/vocab/korean_token_frequency.csv")

with open(input_file, "r", encoding="utf-8") as f:
    article_data = json.load(f)

# ✅ Initialize tokenizer
okt = Okt()

# 🧵 Tokenize all paragraphs and count frequencies
all_tokens = []
for paras in article_data.values():
    for para in paras:
        tokens = okt.morphs(para.strip())
        all_tokens.extend(tokens)

# 📊 Count frequency of each token
token_freq = Counter(all_tokens)

# 📄 Convert to DataFrame and sort by frequency
df_tokens = pd.DataFrame(token_freq.items(), columns=["token", "frequency"])
df_tokens = df_tokens.sort_values(by="frequency", ascending=False).reset_index(drop=True)

# 🧠 Preview
print("📊 Top 20 most frequent tokens:")
print(df_tokens.head(20))

# 💾 Save as CSV
output_file.parent.mkdir(parents=True, exist_ok=True)
df_tokens.to_csv(output_file, index=False, encoding="utf-8")
print(f"✅ Token frequency saved to: {output_file.resolve()}")
