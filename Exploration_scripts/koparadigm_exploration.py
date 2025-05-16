# %%
import pandas as pd
import os
from jamo import h2j, j2hcj
from koparadigm import __file__ as kp_file

base_dir = os.path.dirname(kp_file)
xlsx_path = os.path.join(base_dir, 'koparadigm.xlsx')
verbs_df = pd.read_excel(xlsx_path, sheet_name='Verbs')
endings_df = pd.read_excel(xlsx_path, sheet_name='Endings')
template_df = pd.read_excel(xlsx_path, sheet_name = 'Template')

print("Successfully downloaded !")

template_df.head()

def parse_template_with_logs(template_df):
    rules = {}

    print("📌 Parsing conjugation template...")

    # Step 1: Extract header IDs
    ending_class_ids = template_df.iloc[0, 2:].astype(int).tolist()
    verb_class_ids = template_df.iloc[2:, 0].astype(int).tolist()

    print(f"📋 Found {len(verb_class_ids)} verb classes and {len(ending_class_ids)} ending classes.")

    for i, verb_class in enumerate(verb_class_ids):
        rules[verb_class] = {}
        for j, ending_class in enumerate(ending_class_ids):
            cell = template_df.iloc[i + 2, j + 2]

            # ✅ Allow (,,) to be parsed — don't skip it!
            if pd.isna(cell) or str(cell).strip() in {"", "NaN"}:
                continue

            print(f"🔍 Verb Class {verb_class}, Ending Class {ending_class}: Raw Cell = {cell}")

            try:
                # Clean and split
                clean = str(cell).strip().strip("()")
                parts = [p.strip() if p.strip() != 'None' else None for p in clean.split(",")]

                stop_idx = int(parts[0]) if parts[0] not in [None, ""] else None
                postfix = parts[1] if parts[1] not in [None, ""] else ""
                start_idx = int(parts[2]) if parts[2] not in [None, ""] else None

                rules[verb_class][ending_class] = (stop_idx, postfix, start_idx)

                print(f"✅ Parsed: (stop_idx={stop_idx}, postfix='{postfix}', start_idx={start_idx})")

            except Exception as e:
                print(f"⚠️ Failed to parse at Verb Class {verb_class}, Ending Class {ending_class}: {cell} — {e}")
                continue

    print("✅ Finished parsing template.")
    return rules

parse_template_with_logs(template_df)


# %%
import pandas as pd
import os
from jamo import h2j, j2hcj
from koparadigm import __file__ as kp_file

# Locate base KoParadigm data
base_dir = os.path.dirname(kp_file)
xlsx_path = os.path.join(base_dir, 'koparadigm.xlsx')

# Load original Excel sheets
verbs_df = pd.read_excel(xlsx_path, sheet_name='Verbs')
endings_df = pd.read_excel(xlsx_path, sheet_name='Endings')
template_df = pd.read_excel(xlsx_path, sheet_name='Template', header=None)

# Function to extract choseong (initial consonant) of the first syllable
def extract_first_jamo(word):
    if not word or not isinstance(word, str):
        return None
    try:
        first_syllable = word[0]
        jamos = j2hcj(h2j(first_syllable))
        return jamos[0] if jamos else None
    except:
        return None

# Apply to verbs_df
verbs_df["first_jamo"] = verbs_df["lemma"].apply(extract_first_jamo)

# Define output folder and save
output_folder = r"C:\Users\Nerros\Documents\Korean_Language_App\data\vocab\koparadigm_vocab"
os.makedirs(output_folder, exist_ok=True)

# Save all updated files
verbs_df.to_csv(os.path.join(output_folder, "koparadigm_verbs.csv"), index=False, encoding='utf-8-sig')
endings_df.to_csv(os.path.join(output_folder, "koparadigm_endings.csv"), index=False, encoding='utf-8-sig')
template_df.to_csv(os.path.join(output_folder, "koparadigm_template.csv"), index=False, header=False, encoding='utf-8-sig')

print("✅ Updated verbs_df with `first_jamo` saved to:", output_folder)

verbs_output_path = os.path.join(output_folder, "koparadigm_verbs_df_jamo.csv")
verbs_df.to_csv(verbs_output_path, index=False, encoding='utf-8-sig')

print("✅ Saved updated verbs with jamo to:", verbs_output_path)
