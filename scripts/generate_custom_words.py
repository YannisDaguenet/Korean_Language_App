# generate_starter_vocab_assets.py
# This script creates starter CSV files for Korean punctuation variants, numbers, and Korean-style years.
# Outputs are saved to the /data/generated directory.

from pathlib import Path
import pandas as pd

# ✅ Define output directory
DATA_DIR = Path("../data")
GENERATED_DIR = DATA_DIR / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

# ✅ 1. Korean topic markers (not saved, but displayed)
korean_topic_markers = [
    "은", "는",  # Basic topic markers
    "도",        # Also/as well
    "만",        # Only
    "까지",      # Until/even
    "조차",      # Even (negative nuance)
    "마저",      # Even (unexpected)
]

print("✅ Korean topic markers:", korean_topic_markers)

# ✅ 2. Generate punctuation variants CSV
punctuation = [".", ",", "!", "?", ":", ";", "\"", "'", "(", ")", "…", "-", "~", "—"]
punct_variants = [(p, f"{p}.") for p in punctuation]
flat_punct = [item for pair in punct_variants for item in pair]

df_punct = pd.DataFrame(flat_punct, columns=["form"])
punct_path = GENERATED_DIR / "punctuation_variants.csv"
df_punct.to_csv(punct_path, index=False, encoding="utf-8")
print(f"✅ Saved punctuation variants to {punct_path.resolve()}")

# ✅ 3. Generate number list and Korean-style years
numbers = list(range(0, 2026))
df_numbers = pd.DataFrame(numbers, columns=["number"])
numbers_path = GENERATED_DIR / "numbers_0_to_2025.csv"
df_numbers.to_csv(numbers_path, index=False, encoding="utf-8")
print(f"✅ Saved numbers 0–2025 to {numbers_path.resolve()}")

years_korean = [f"{n}년" for n in numbers]
df_years = pd.DataFrame(years_korean, columns=["year"])
years_path = GENERATED_DIR / "korean_years_0_to_2025.csv"
df_years.to_csv(years_path, index=False, encoding="utf-8")
print(f"✅ Saved Korean-style years to {years_path.resolve()}")
