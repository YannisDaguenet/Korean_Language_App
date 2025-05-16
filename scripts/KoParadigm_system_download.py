
# This code takes the system created by Kyubyong Park (박규병) in 
# 2020 and downloads it locally.
#  @article{park2020KoParadigm,
#   author = {Park, Kyubyong },
#   title={KoParadigm: A Korean Conjugation Paradigm Generator},
#   journal={arXiv preprint arXiv:2004.13221},
#   year={2020}}
# %%

import pandas as pd
import os
from pathlib import Path
from jamo import h2j, j2hcj
from koparadigm import __file__ as kp_file

# Step 1: Locate koparadigm.xlsx inside the installed module
xlsx_path = Path(kp_file).resolve().parent / "koparadigm.xlsx"

# Step 2: Load the sheets
verbs_df = pd.read_excel(xlsx_path, sheet_name='Verbs')
endings_df = pd.read_excel(xlsx_path, sheet_name='Endings')
template_df = pd.read_excel(xlsx_path, sheet_name='Template', header=None)

# Step 3: Add first_jamo column to verbs_df
def extract_first_jamo(word):
    if not word or not isinstance(word, str):
        return None
    try:
        jamos = j2hcj(h2j(word[0]))
        return jamos[0] if jamos else None
    except:
        return None

verbs_df["first_jamo"] = verbs_df["Verb"].apply(extract_first_jamo)

# Step 4: Define output folder relative to this script
project_root = Path(__file__).resolve().parent.parent
output_dir = project_root / "data" / "vocab" / "koparadigm_vocab"
output_dir.mkdir(parents=True, exist_ok=True)

# Step 5: Save CSVs
verbs_df.to_csv(output_dir / "koparadigm_verbs_df_jamo.csv", index=False, encoding='utf-8-sig')
endings_df.to_csv(output_dir / "koparadigm_endings.csv", index=False, encoding='utf-8-sig')
template_df.to_csv(output_dir / "koparadigm_template.csv", index=False, header=False, encoding='utf-8-sig')

# ✅ Summary
print("✅ KoParadigm data exported to:", output_dir)
print("🔤 Columns in verbs_df:", verbs_df.columns.tolist())

# %%
