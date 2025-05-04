# This script sets up the local folder structure for the Korean language learning app, ensuring that
#   `data/json` and `data/vocab` directories exist. It moves key vocabulary and tracking files 
#   (e.g., word frequency CSV, known/unknown words JSONs) into their appropriate folders if they are 
#   found in the working directory. It then optionally loads these files to verify data integrity.
#   Finally, it compares the known words with the frequency dataset to calculate the learner’s 
#   vocabulary coverage and prints the percentage of known tokens among all tokens in the dataset.

# ✅ Setup script for VSCode environment (no Colab-specific code)

import os
import shutil
import json
import pandas as pd

# ✅ Create project folders if needed
data_dir = "data"
vocab_dir = os.path.join(data_dir, "vocab")
json_dir = os.path.join(data_dir, "json")
os.makedirs(vocab_dir, exist_ok=True)
os.makedirs(json_dir, exist_ok=True)

# ✅ Define expected files
word_freq_file = "korean_token_frequency.csv"
json_files = [
    "known_words_tokenized.json",
    "unknown_words.json",
    "seen_sentences.json"
]

# ✅ Move vocabulary files (if downloaded into current dir)
if os.path.exists(word_freq_file):
    shutil.move(word_freq_file, os.path.join(vocab_dir, word_freq_file))
    print(f"✅ Moved {word_freq_file} to {vocab_dir}")

# ✅ Move JSON tracking files (if found in working directory)
for jf in json_files:
    if os.path.exists(jf):
        shutil.move(jf, os.path.join(json_dir, jf))
        print(f"✅ Moved {jf} to {json_dir}")

# ✅ Optionally confirm data load
try:
    with open(os.path.join(json_dir, "known_words_tokenized.json"), "r", encoding="utf-8") as f:
        known = json.load(f)
    print(f"📚 Known words loaded: {len(known)} tokens")
except Exception as e:
    print(f"⚠️ Could not load known_words_tokenized.json: {e}")

try:
    test_df = pd.read_csv(os.path.join(vocab_dir, word_freq_file))
    print(f"📊 Word frequency dataset contains {len(test_df)} entries")
except Exception as e:
    print(f"⚠️ Could not load {word_freq_file}: {e}")

# ✅ Analyze known word coverage in frequency dataset
if 'known' in locals() and 'test_df' in locals():
    freq_tokens = set(test_df['token'])
    known_tokens = set(known)

    known_in_freq = freq_tokens & known_tokens
    coverage_count = len(known_in_freq)
    total_count = len(freq_tokens)
    coverage_pct = (coverage_count / total_count) * 100 if total_count > 0 else 0

    print(f"🧠 You know {coverage_count} / {total_count} words in the frequency list.")
    print(f"📈 Coverage: {coverage_pct:.2f}%")