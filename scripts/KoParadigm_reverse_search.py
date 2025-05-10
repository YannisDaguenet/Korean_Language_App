# This code aims to find the lemma from any given verbs among the list in verbs_df. 
# 
#   This code does so using the rules of the system created by Kyubyong Park (박규병) in 
#   2020 and makes it function for our specific needs locally.
#   @article{park2020KoParadigm,
#   author = {Park, Kyubyong },
#   title={KoParadigm: A Korean Conjugation Paradigm Generator},
#   journal={arXiv preprint arXiv:2004.13221},
#   year={2020}}
# 
#   I do so in three steps : 
#       1 - I detect the ending class and first jammo of the verb I want to find the lemma from.
#       2 - I reduce the list of eligible verbs using the dictionary of verb class and the ending class
#       3 - I compute the rules in reverse and see whether it matches one of the reduced list.
#       4 - (optional) I compute the rules in the normal order given these reductions

# %%
# Step 1

from collections import defaultdict
import pandas as pd
import jamo
from jamo import h2j, j2hcj

# ✅ Paths to KoParadigm files
verbs_path = r"C:\Users\Nerros\Documents\Korean_Language_App\data\vocab\koparadigm_vocab\koparadigm_verbs_df_jamo.csv"
endings_path = r"C:\Users\Nerros\Documents\Korean_Language_App\data\vocab\koparadigm_vocab\koparadigm_endings.csv"

# ✅ Load verbs (assumed format: [lemma, class_id])
verbs_df = pd.read_csv(verbs_path, header=None, names=["Num", "Verbs", "Class", "Jamo"])
print("✅ verbs_df loaded:", verbs_df.shape)

# ✅ Load endings (assumed format: [ending, class_id])
endings_df = pd.read_csv(endings_path, header=None, names=["Num", "Ending", "Class"])
print("✅ endings_df loaded:", endings_df.shape)

# ✅ Sample conjugated words
conjugated_word_list = ["하면서"]

# ✅ Decompose Hangul syllable into (choseong, jungseong, jongseong)
def get_jamo(syllable):
    decomposed = j2hcj(h2j(syllable))
    if len(decomposed) == 2:
        return (decomposed[0], decomposed[1], None)
    elif len(decomposed) == 3:
        return tuple(decomposed)
    return (None, None, None)

# ✅ Step 1: Detect possible endings and stem clues
def detect_candidate_endings_first_jamo(conjugated_word, endings_df):
    candidates = []

    for _, row in endings_df.iterrows():
        ending = row["Ending"]
        class_id = row["Class"]

        if conjugated_word.endswith(ending):
            stem_candidate = conjugated_word[:-len(ending)]
            if not stem_candidate:
                continue

            last_syllable = stem_candidate[-1]
            choseong_last, jungseong_last, jongseong_last = get_jamo(last_syllable)

            # ✅ Get first syllable and decompose it
            first_syllable = stem_candidate[0]
            choseong_first, jungseong_first, jongseong_first = get_jamo(first_syllable)

            candidates.append({
                "word": conjugated_word,
                "ending": ending,
                "class_id": class_id,
                "stem_candidate": stem_candidate,
                "last_syllable": last_syllable,
                "last_jamo": (choseong_last, jungseong_last, jongseong_last),
                "first_syllable": first_syllable,
                "first_jamo": choseong_first,  # ✅ Add this line
            })

    return candidates
# ✅ Run Step 1 with updated function and show first jamo too
for word in conjugated_word_list:
    print(f"\n🔎 Analyzing: {word}")
    candidates = detect_candidate_endings_first_jamo(word, endings_df)
    for c in candidates:
        print(f"➡ Ending '{c['ending']}' (Class {c['class_id']}), Stem: '{c['stem_candidate']}', First jamo: '{c['first_jamo']}', Last jamo: {c['last_jamo']}")

import pandas as pd

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

            try:
                # Clean and split
                clean = str(cell).strip().strip("()")
                parts = [p.strip() if p.strip() != 'None' else None for p in clean.split(",")]

                stop_idx = int(parts[0]) if parts[0] not in [None, ""] else None
                postfix = parts[1] if parts[1] not in [None, ""] else ""
                start_idx = int(parts[2]) if parts[2] not in [None, ""] else None

                rules[verb_class][ending_class] = (stop_idx, postfix, start_idx)

            except Exception as e:
                continue

    print("✅ Finished parsing template.")
    return rules

template_path = r"C:\Users\Nerros\Documents\Korean_Language_App\data\vocab\koparadigm_vocab\koparadigm_template.csv"
template_df = pd.read_csv(template_path, header=None)
rules_dict = parse_template_with_logs(template_df)
def filter_candidate_verbs(step1_results, verbs_df, rules_dict):
    """
    Step 2: For each ending match (from step 1), find candidate lemmas:
        - The verb class must support the detected ending class
        - The lemma's initial jamo must match the detected first jamo
    Returns a list of matches with all the information needed for Step 3.
    """
    filtered = []

    for item in step1_results:
        ending_class = item["class_id"]
        first_jamo = item["first_jamo"]
        ending = item["ending"]
        word = item["word"]
        stem_candidate = item["stem_candidate"]

        print(f"\n🔎 STEP 2: Checking '{word}' (Ending '{ending}', Class {ending_class}, Stem '{stem_candidate}', First jamo '{first_jamo}')")

        compatible_found = False
        match_count = 0

        for verb_class, rule_map in rules_dict.items():
            if ending_class not in rule_map:
                continue

            rule = rule_map[ending_class]
            compatible_found = True

            matching_verbs = verbs_df[
                (verbs_df["Class"] == verb_class) &
                (verbs_df["Jamo"] == first_jamo)
            ]

            print(f"   ✅ Verb Class {verb_class} matches Ending Class {ending_class} with rule {rule} → {len(matching_verbs)} match(es)")

            for _, row in matching_verbs.iterrows():
                match_count += 1
                filtered.append({
                    "lemma": row["Verbs"],
                    "verb_class": verb_class,
                    "ending_class": ending_class,
                    "rule": rule,
                    "ending": ending,
                    "original_word": word,
                    "stem_candidate": stem_candidate,
                    "first_jamo": first_jamo,
                })
                print(f"      ➕ Matched lemma: {row['Verbs']}")

        if not compatible_found:
            print(f"   ❌ No verb classes compatible with ending class {ending_class}.")
        elif match_count == 0:
            print(f"   ⚠️ Verb classes exist, but no lemma with first jamo '{first_jamo}' matched.")

    print(f"\n✅ STEP 2 COMPLETE: Found {len(filtered)} total candidate(s) across all matches.\n")
    return filtered

# Load the updated file with first_jamo
verbs_df = pd.read_csv(r"C:\Users\Nerros\Documents\Korean_Language_App\data\vocab\koparadigm_vocab\koparadigm_verbs_df_jamo.csv")

# Step 1
step1_results = detect_candidate_endings_first_jamo("하면서", endings_df)

# Step 2
filtered_candidates = filter_candidate_verbs(step1_results, verbs_df, rules_dict)

# Preview result
for c in filtered_candidates[:5]:  # show first 5 matches
    print(f"➡ Lemma: {c['lemma']} | Rule: {c['rule']} | Ending: {c['ending']}")

# Debugging
for vc, endings in rules_dict.items():
    if 2 in endings:
        print(f"✅ Verb Class {vc} has a rule for Ending Class 2 → {endings[2]}")

filtered = verbs_df[
    (verbs_df["Class"] == vc) & (verbs_df["first_jamo"] == 'ㅎ')
]
print(filtered.head())

print(ord('ㅎ'))  # should be 54620

verbs_df["first_jamo"].apply(lambda x: ord(x) if isinstance(x, str) else x).value_counts()



# %%
