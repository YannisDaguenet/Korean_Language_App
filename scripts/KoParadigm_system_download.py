
# This code takes the system created by Kyubyong Park (박규병) in 
# 2020 and downloads it locally.
#  @article{park2020KoParadigm,
#   author = {Park, Kyubyong },
#   title={KoParadigm: A Korean Conjugation Paradigm Generator},
#   journal={arXiv preprint arXiv:2004.13221},
#   year={2020}}
# %% 
# koparadigm basic
from koparadigm import Paradigm, prettify

p = Paradigm()

# Important: only the stem (e.g., 곱다 → 곱)
verb = "곱"

paradigms = p.conjugate(verb)

# See raw structure
print(paradigms)

# Nicely formatted output
prettify(paradigms)
# %% 
# read the matrix
import pandas as pd
from koparadigm import __file__ as kp_file
import os

# Get path to koparadigm.xlsx
base_dir = os.path.dirname(kp_file)
xlsx_path = os.path.join(base_dir, 'koparadigm.xlsx')

# Load the three sheets
verbs_df = pd.read_excel(xlsx_path, sheet_name='Verbs')
endings_df = pd.read_excel(xlsx_path, sheet_name='Endings')
template_df = pd.read_excel(xlsx_path, sheet_name='Template', header=None)

print("✅ Loaded:")
print(f"- {len(verbs_df)} verbs")
print(f"- {len(endings_df)} endings")
print(f"- {template_df.shape[0]} x {template_df.shape[1]} rule matrix")

# Preview first 5 entries
print("\n📌 Sample verbs:")
print(verbs_df.head())

print("\n📌 Sample endings:")
print(endings_df.head())

print("\n📌 Sample rule matrix:")
print(template_df.iloc[:5, :5])

# %% 
# extract csvs

import pandas as pd
from koparadigm import __file__ as kp_file
import os

# Step 1: Locate the xlsx file
base_dir = os.path.dirname(kp_file)
xlsx_path = os.path.join(base_dir, 'koparadigm.xlsx')

# Step 2: Load each sheet
verbs_df = pd.read_excel(xlsx_path, sheet_name='Verbs')
endings_df = pd.read_excel(xlsx_path, sheet_name='Endings')
template_df = pd.read_excel(xlsx_path, sheet_name='Template', header=None)

# Step 3: Save to CSV
verbs_df.to_csv("koparadigm_verbs.csv", index=False, encoding='utf-8-sig')
endings_df.to_csv("koparadigm_endings.csv", index=False, encoding='utf-8-sig')
template_df.to_csv("koparadigm_template.csv", index=False, header=False, encoding='utf-8-sig')

print("✅ All files saved:")
print("- koparadigm_verbs.csv")
print("- koparadigm_endings.csv")
print("- koparadigm_template.csv")

# %%
import pandas as pd
import os
from koparadigm import __file__ as kp_file

# Step 1: Locate koparadigm.xlsx
base_dir = os.path.dirname(kp_file)
xlsx_path = os.path.join(base_dir, 'koparadigm.xlsx')

# Step 2: Load each sheet
verbs_df = pd.read_excel(xlsx_path, sheet_name='Verbs')
endings_df = pd.read_excel(xlsx_path, sheet_name='Endings')
template_df = pd.read_excel(xlsx_path, sheet_name='Template', header=None)

# Step 3: Define target folder path
output_folder = r"C:\Users\Nerros\Documents\Korean_Language_App\data\vocab\koparadigm_vocab"
os.makedirs(output_folder, exist_ok=True)

# Step 4: Save all 3 files
verbs_df.to_csv(os.path.join(output_folder, "koparadigm_verbs.csv"), index=False, encoding='utf-8-sig')
endings_df.to_csv(os.path.join(output_folder, "koparadigm_endings.csv"), index=False, encoding='utf-8-sig')
template_df.to_csv(os.path.join(output_folder, "koparadigm_template.csv"), index=False, header=False, encoding='utf-8-sig')

print("✅ Files saved to:", output_folder)

# %%
import koparadigm
print(dir(koparadigm))
# %%
import koparadigm

help(koparadigm.prettify)
help(koparadigm.koparadigm)
help(koparadigm.Paradigm)

# %%
import pandas as pd
import os
from jamo import h2j, j2hcj

# Load your CSV file
verbs_path = r"C:\Users\Nerros\Documents\Korean_Language_App\data\vocab\koparadigm_vocab\koparadigm_verbs.csv"
verbs_df = pd.read_csv(verbs_path)

# Confirm columns
print("🔍 Columns:", verbs_df.columns.tolist())

# Function to extract choseong (initial consonant) from the first syllable
def extract_first_jamo(word):
    if not word or not isinstance(word, str):
        return None
    try:
        first_syllable = word[0]
        jamos = j2hcj(h2j(first_syllable))
        return jamos[0] if jamos else None
    except:
        return None

# Apply to 'Verb' column
verbs_df["first_jamo"] = verbs_df["Verb"].apply(extract_first_jamo)

# Save to new file
output_folder = r"C:\Users\Nerros\Documents\Korean_Language_App\data\vocab\koparadigm_vocab"
output_path = os.path.join(output_folder, "koparadigm_verbs_df_jamo.csv")
verbs_df.to_csv(output_path, index=False, encoding='utf-8-sig')

print("✅ Saved verbs with `first_jamo` to:", output_path)

# %%

import pandas as pd

# ✅ Paths to KoParadigm files
verbs_path = r"C:\Users\Nerros\Documents\Korean_Language_App\data\vocab\koparadigm_vocab\koparadigm_verbs_df_jamo.csv"
endings_path = r"C:\Users\Nerros\Documents\Korean_Language_App\data\vocab\koparadigm_vocab\koparadigm_endings.csv"

# ✅ Load verbs (assumed format: [lemma, class_id])
verbs_df = pd.read_csv(verbs_path, header=None, names=["Num", "Verb", "Class ID", "Jamo"])
print("✅ verbs_df loaded:", verbs_df.shape)

# ✅ Load endings (assumed format: [ending, class_id])
endings_df = pd.read_csv(endings_path, header=None, names=["Num", "ending", "class_id"])
print("✅ endings_df loaded:", endings_df.shape)

print("verbs_df columns : ", verbs_df.columns.tolist())
print("verbs_df headers :", verbs_df.head(10))

print(verbs_df[verbs_df["Verb"] == "하"])
# %%
