# This code takes the system created by Kyubyong Park (박규병) in 
# 2020 and makes it function for our specific needs locally.
#  @article{park2020KoParadigm,
#   author = {Park, Kyubyong },
#   title={KoParadigm: A Korean Conjugation Paradigm Generator},
#   journal={arXiv preprint arXiv:2004.13221},
#   year={2020}}
# What it does is threefold : 
#   1. It parses template_df into a usable dictionary: rules[verb_class][ending_class] = rule_tuple
#   2. It maps example endings (like 어요, 았다, etc.) to grammatical labels (e.g., Present/Honorific)
#   3. It builds a reverse matcher to:
#       Identify which paradigm (verb stem) a conjugated word likely belongs to
#       Retrieve all conjugations
#       Filter them by mood/tense/style


# %% 
# Parsing the rules of conjugation
import pandas as pd
template_path = r"C:\Users\Nerros\Documents\Korean_Language_App\data\vocab\koparadigm_vocab\koparadigm_template.csv"
template_df = pd.read_csv(template_path, header=None)
print("✅ template_df was correctly loaded:", template_df.shape)

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
            if pd.isna(cell) or str(cell).strip() in {"", "(,,)", "NaN"}:
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

rules_dict = parse_template_with_logs(template_df)

verbs_path = r"C:\Users\Nerros\Documents\Korean_Language_App\data\vocab\koparadigm_vocab\koparadigm_verbs.csv"
verbs_df = pd.read_csv(verbs_path, header=None, names=["Num", "Verb", "Class"])
verbs_df = pd.read_csv(verbs_path, header=0, names=["Num", "Verb", "Class"])
verbs_df = verbs_df[verbs_df["Class"] != "Class"]  # Remove accidental header rows
verbs_df["Class"] = verbs_df["Class"].astype(int)
print("✅ verbs_df cleaned and loaded:", verbs_df.shape)

# ✅ Load endings_df safely
endings_path = r"C:\Users\Nerros\Documents\Korean_Language_App\data\vocab\koparadigm_vocab\koparadigm_endings.csv"
endings_df = pd.read_csv(endings_path, header=0, names=["Num", "Ending", "Class"])
endings_df = endings_df[endings_df["Class"] != "Class"]  # Remove accidental header rows
endings_df["Class"] = endings_df["Class"].astype(int)
print("✅ endings_df cleaned and loaded:", endings_df.shape)


def get_all_forms(stem, verbs_df, endings_df, rules_dict, save_to_csv=False, csv_path=None):

    """
    Generate all conjugated forms for a given Korean stem using KoParadigm logic.
    Optionally save the output to CSV.
    """
    import re
    import pandas as pd

    def decompose(word):
        return list(word)  # Naive: no jamo split, just character-level for now

    def compose(chars):
        return ''.join(chars)

    results = []

    print(f"\n🔍 Looking up stem: '{stem}'")

    # Step 1: Get verb class
    matching_verb = verbs_df[verbs_df["Verb"] == stem]
    if matching_verb.empty:
        print(f"❌ Stem '{stem}' not found in verbs list.")
        return []

    verb_class = int(matching_verb.iloc[0]["Class"])
    print(f"📚 Found Verb Class: {verb_class}")

    # Step 2: Check if verb class has rules
    if verb_class not in rules_dict:
        print(f"⚠️ No rules found for Verb Class {verb_class}.")
        return []

    # Step 3: Apply rules to generate forms
    for _, row in endings_df.iterrows():
        ending = row["Ending"]
        ending_class = int(row["Class"])

        if ending_class not in rules_dict[verb_class]:
            continue

        rule = rules_dict[verb_class][ending_class]
        stop_idx, postfix, start_idx = rule

        print(f"🔧 Applying rule {rule} for ending '{ending}' (class {ending_class})")

        try:
            verb_jamos = decompose(stem)
            ending_jamos = decompose(ending)

            modified_stem = verb_jamos if stop_idx is None else verb_jamos[:stop_idx]
            modified_stem += list(postfix) if postfix else []

            modified_ending = ending_jamos if start_idx is None else ending_jamos[start_idx:]

            full_form = compose(modified_stem + modified_ending)

            results.append({
                "base_stem": stem,
                "verb_class": verb_class,
                "ending": ending,
                "ending_class": ending_class,
                "rule": rule,
                "form": full_form
            })

            print(f"✅ Created form: {full_form}")

        except Exception as e:
            print(f"⚠️ Error processing rule {rule} for {stem} + {ending}: {e}")
            continue

    if save_to_csv:
        if not csv_path:
            csv_path = f"{stem}_conjugations.csv"
        df = pd.DataFrame(results)
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"\n📁 Saved {len(results)} forms to: {csv_path}")

    return results

forms = get_all_forms("곱", verbs_df, endings_df, rules_dict, save_to_csv=True)

# Print first 10 results
for form in forms[:10]:
    print(f"{form['form']}  ←  {form['base_stem']} + {form['ending']} via {form['rule']}")

print("🔎 Rules available for Verb Class 17:")
print(rules_dict.get(17, "❌ No entry found"))

# %%
# koparadigm_full_export

import pandas as pd
from koparadigm import Paradigm

# 1. Load verb stems from your local CSV
verb_path = r"C:\Users\Nerros\Documents\Korean_Language_App\data\vocab\koparadigm_vocab\koparadigm_verbs.csv"
verbs_df = pd.read_csv(verb_path, header=0, names=["Num", "Verb", "Class"])
verbs_df = verbs_df[verbs_df["Class"] != "Class"]
verbs_df["Class"] = verbs_df["Class"].astype(int)
verb_stems = verbs_df["Verb"].unique().tolist()

print(f"✅ Loaded {len(verb_stems)} unique verb stems")

# 2. Load KoParadigm generator
p = Paradigm()

# 3. Flatten helper
def flatten_koparadigm_output(stem, conjugated):
    result = []
    for category, pairs in conjugated:
        for ending, form in pairs:
            result.append({
                "stem": stem,
                "category": category,
                "ending": ending,
                "form": form
            })
    return result

# 4. Process all stems
all_conjugations = []

for idx, stem in enumerate(verb_stems):
    try:
        print(f"[{idx+1}/{len(verb_stems)}] 🔁 Conjugating '{stem}'...")
        conjugated = p.conjugate(stem)
        flattened = flatten_koparadigm_output(stem, conjugated)
        all_conjugations.extend(flattened)
    except Exception as e:
        print(f"❌ Error for '{stem}': {e}")

# 5. Save to CSV
parquet_path = r"C:\Users\Nerros\Documents\Korean_Language_App\data\vocab\koparadigm_vocab\koparadigm_conjugations.parquet"
df = pd.DataFrame(all_conjugations)
df.to_parquet(parquet_path, index=False)
print(f"\n📦 Saved to Parquet: {parquet_path}")
# %%
# Load Parquet when needed
parquet_path = r"C:\Users\Nerros\Documents\Korean_Language_App\data\vocab\koparadigm_vocab\koparadigm_conjugations.parquet"
df = pd.read_parquet(parquet_path)

# Example: Find the stem of a conjugated form
def find_stem(word):
    result = df[df["form"] == word]
    if not result.empty:
        return result.iloc[0]["stem"]
    else:
        return None

print(find_stem("갔어요"))  # Output: 가
