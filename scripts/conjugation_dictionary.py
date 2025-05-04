# %%
# conjugation_dictionary.py

# This code creates a dictionary of conjugation for each verb lemma that is filled, mapping the lemma to all 
#   possible grammatical forms.
#   Each lemma is categorized (e.g., regular, ㄷ irregular, ㅂ irregular, etc.), and conjugation rules are 
#   applied accordingly.
#   For each verb, the output includes all major grammatical forms:
#       - Present Tense
#       - Past Tense
#       - Future Tense
#       - Continuous Tense
#       - Suppositional Tense
#       - Intentional Tense
#       - Imperative Mood
#       - Prohibitive Mood
#   Each form is generated in both:
#       - Plain (non-honorific)
#       - Honorific style (e.g., 가요 vs. 가세요)
#   The final dictionary maps each lemma to a nested structure, grouping each conjugation type under
#   'plain' and 'honorific' keys.

import unicodedata
from typing import Dict

# ✅ Irregular verb exceptions
D_IRREGULARS = {"걷다", "듣다"}
B_IRREGULARS = {"돕다", "덥다"}
R_IRREGULARS = {"다르다", "빠르다"}
EUIR_IRREGULARS = {"크다"}
HA_IRREGULARS = {"하다", "공부하다", "말하다", "전화하다"}

# ✅ Hangul character components
JONGSUNG_LIST = [
    "", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ",
    "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ",
    "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
]

# ✅ Utility functions

def has_batchim(syllable: str) -> bool:
    code = ord(syllable[-1])
    return (code - 0xAC00) % 28 != 0 if 0xAC00 <= code <= 0xD7A3 else False

def add_final_consonant(word: str, final_consonant: str) -> str:
    if not word:
        return word
    code = ord(word[-1])
    if not (0xAC00 <= code <= 0xD7A3):
        return word + final_consonant
    offset = code - 0xAC00
    ch_i = offset // (21 * 28)
    jv_i = (offset % (21 * 28)) // 28
    jf_i = JONGSUNG_LIST.index(final_consonant)
    new_code = 0xAC00 + (ch_i * 21 * 28) + (jv_i * 28) + jf_i
    return word[:-1] + chr(new_code)

def get_l_future_form(stem: str) -> str:
    return stem + "을 거예요" if has_batchim(stem[-1]) else add_final_consonant(stem, "ㄹ") + " 거예요"

def contract_past(lemma: str) -> str:
    root = lemma[:-1]
    if root.endswith("하"):
        return "했어요"
    return root + ("았어요" if root[-1] in "ㅏㅗ" else "었어요")

def get_present_form(stem: str) -> str:
    root = stem[:-1]
    if root.endswith("하"):
        return "해요"
    return root + ("아요" if root[-1] in "ㅏㅗ" else "어요")

def detect_category(lemma: str) -> str:
    if lemma in HA_IRREGULARS or lemma.endswith("하다"):
        return "하 irregular"
    elif lemma in D_IRREGULARS:
        return "ㄷ irregular"
    elif lemma in B_IRREGULARS:
        return "ㅂ irregular"
    elif lemma in R_IRREGULARS:
        return "르 irregular"
    elif lemma in EUIR_IRREGULARS:
        return "으 irregular"
    else:
        return "regular"

# ✅ Conjugation base

def conjugate_regular(stem: str) -> Dict[str, Dict[str, str]]:
    root = stem[:-1]
    vowel_harmony = root[-1] in "ㅏㅗ"
    return {
        "present": {"plain": get_present_form(stem), "honorific": root + "세요"},
        "past": {"plain": contract_past(stem), "honorific": root + "셨어요"},
        "future": {"plain": get_l_future_form(root), "honorific": root + "실 거예요"},
        "continuous": {"plain": root + "고 있어요", "honorific": root + "고 계세요"},
        "suppositional": {"plain": root + "겠어요", "honorific": root + "시겠어요"},
        "intentional": {"plain": add_final_consonant(root, "ㄹ") + "게요", "honorific": root + "실게요"},
        "imperative": {"plain": root + ("아라" if vowel_harmony else "어라"), "honorific": root + "세요"},
        "prohibitive": {"plain": root + "지 마세요", "honorific": root + "지 마세요"},
    }

# ✅ Irregular verb handlers

def conjugate_irregular_ha(stem: str) -> Dict[str, Dict[str, str]]:
    return {
        "present": {"plain": "해요", "honorific": "하세요"},
        "past": {"plain": "했어요", "honorific": "하셨어요"},
        "future": {"plain": "할 거예요", "honorific": "하실 거예요"},
        "continuous": {"plain": "하고 있어요", "honorific": "하고 계세요"},
        "suppositional": {"plain": "하겠어요", "honorific": "하시겠어요"},
        "intentional": {"plain": "할게요", "honorific": "하실게요"},
        "imperative": {"plain": "하라", "honorific": "하세요"},
        "prohibitive": {"plain": "하지 마세요", "honorific": "하지 마세요"},
    }

def conjugate_irregular_d(stem: str) -> Dict[str, Dict[str, str]]:
    return conjugate_regular(stem[:-2] + "들다")

def conjugate_irregular_b(stem: str) -> Dict[str, Dict[str, str]]:
    return conjugate_regular(stem[:-2] + "우다")

def conjugate_irregular_r(stem: str) -> Dict[str, Dict[str, str]]:
    return conjugate_regular(stem[:-2] + stem[-2] + "르다")

def conjugate_irregular_euir(stem: str) -> Dict[str, Dict[str, str]]:
    root = stem[:-1] if stem[-2] == "으" else stem[:-1]  # general 으-drop logic
    return conjugate_regular(root + "다")

# 📦 Main dispatcher

def conjugate_korean_verb(lemma: str) -> Dict[str, Dict[str, str]]:
    category = detect_category(lemma)
    if category == "regular":
        return conjugate_regular(lemma)
    elif category == "ㄷ irregular":
        return conjugate_irregular_d(lemma)
    elif category == "ㅂ irregular":
        return conjugate_irregular_b(lemma)
    elif category == "르 irregular":
        return conjugate_irregular_r(lemma)
    elif category == "으 irregular":
        return conjugate_irregular_euir(lemma)
    elif category == "하 irregular":
        return conjugate_irregular_ha(lemma)
    else:
        raise ValueError(f"Unknown category for {lemma}")

# 🧪 Test
if __name__ == "__main__":
    verbs = ["가다", "자다", "듣다", "덥다", "다르다", "크다", "공부하다"]
    from pprint import pprint
    for lemma in verbs:
        print(f"\n🔹 {lemma}")
        pprint(conjugate_korean_verb(lemma))


# %%
# This code creates a dictionary of conjugation for each verb lemma that is filled, mapping the lemma to all 
#   possible grammatical forms.
#   Each lemma is categorized (e.g., regular, ㄷ irregular, ㅂ irregular, etc.), and conjugation rules are 
#   applied accordingly.
#   For each verb, the output includes all major grammatical forms:
#       - Present Tense
#       - Past Tense
#       - Future Tense
#       - Continuous Tense
#       - Suppositional Tense
#       - Intentional Tense
#       - Imperative Mood
#       - Prohibitive Mood
#   Each form is generated in both:
#       - Plain (non-honorific)
#       - Honorific style (e.g., 가요 vs. 가세요)
#   The final dictionary maps each lemma to a nested structure, grouping each conjugation type under
#   'plain' and 'honorific' keys.

import unicodedata
from typing import Dict

# ✅ Irregular verb exceptions
D_IRREGULARS = {"걷다", "듣다"}
B_IRREGULARS = {"돕다", "덥다"}
R_IRREGULARS = {"다르다", "빠르다"}
EUIR_IRREGULARS = {"크다"}
HA_IRREGULARS = {"하다", "공부하다", "말하다", "전화하다"}

# ✅ Hangul character components
JONGSUNG_LIST = [
    "", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ",
    "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ",
    "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
]

# ✅ Utility functions

def has_batchim(syllable: str) -> bool:
    code = ord(syllable[-1])
    return (code - 0xAC00) % 28 != 0 if 0xAC00 <= code <= 0xD7A3 else False

def add_final_consonant(word: str, final_consonant: str) -> str:
    if not word:
        return word
    code = ord(word[-1])
    if not (0xAC00 <= code <= 0xD7A3):
        return word + final_consonant
    offset = code - 0xAC00
    ch_i = offset // (21 * 28)
    jv_i = (offset % (21 * 28)) // 28
    jf_i = JONGSUNG_LIST.index(final_consonant)
    new_code = 0xAC00 + (ch_i * 21 * 28) + (jv_i * 28) + jf_i
    return word[:-1] + chr(new_code)

def get_l_future_form(stem: str) -> str:
    return stem + "을 거예요" if has_batchim(stem[-1]) else add_final_consonant(stem, "ㄹ") + " 거예요"

def contract_past(lemma: str) -> str:
    root = lemma[:-1]
    if root.endswith("하"):
        return "했어요"
    if root.endswith("크"):
        return "컸어요"
    return root + ("았어요" if root[-1] in "ㅏㅗ" else "었어요")

def contract_present(root: str) -> str:
    if root.endswith("하"):
        return "해요"
    if root.endswith("크"):
        return "커요"
    return root + ("아요" if root[-1] in "ㅏㅗ" else "어요")

def detect_category(lemma: str) -> str:
    if lemma in HA_IRREGULARS or lemma.endswith("하다"):
        return "하 irregular"
    elif lemma in D_IRREGULARS:
        return "ㄷ irregular"
    elif lemma in B_IRREGULARS:
        return "ㅂ irregular"
    elif lemma in R_IRREGULARS:
        return "르 irregular"
    elif lemma in EUIR_IRREGULARS:
        return "으 irregular"
    else:
        return "regular"

# ✅ Conjugation base

def conjugate_regular(stem: str) -> Dict[str, Dict[str, str]]:
    root = stem[:-1]
    vowel_harmony = root[-1] in "ㅏㅗ"
    return {
        "present": {"plain": contract_present(root), "honorific": root + "세요"},
        "past": {"plain": contract_past(stem), "honorific": root + "셨어요"},
        "future": {"plain": get_l_future_form(root), "honorific": root + "실 거예요"},
        "continuous": {"plain": root + "고 있어요", "honorific": root + "고 계세요"},
        "suppositional": {"plain": root + "겠어요", "honorific": root + "시겠어요"},
        "intentional": {"plain": add_final_consonant(root, "ㄹ") + "게요", "honorific": root + "실게요"},
        "imperative": {"plain": root + ("아라" if vowel_harmony else "어라"), "honorific": root + "세요"},
        "prohibitive": {"plain": root + "지 마세요", "honorific": root + "지 마세요"},
    }

# ✅ Irregular verb handlers

def conjugate_irregular_ha(stem: str) -> Dict[str, Dict[str, str]]:
    return {
        "present": {"plain": "해요", "honorific": "하세요"},
        "past": {"plain": "했어요", "honorific": "하셨어요"},
        "future": {"plain": "할 거예요", "honorific": "하실 거예요"},
        "continuous": {"plain": "하고 있어요", "honorific": "하고 계세요"},
        "suppositional": {"plain": "하겠어요", "honorific": "하시겠어요"},
        "intentional": {"plain": "할게요", "honorific": "하실게요"},
        "imperative": {"plain": "하라", "honorific": "하세요"},
        "prohibitive": {"plain": "하지 마세요", "honorific": "하지 마세요"},
    }

def conjugate_irregular_d(stem: str) -> Dict[str, Dict[str, str]]:
    return conjugate_regular(stem[:-2] + "들다")

def conjugate_irregular_b(stem: str) -> Dict[str, Dict[str, str]]:
    return conjugate_regular(stem[:-2] + "우다")

def conjugate_irregular_r(stem: str) -> Dict[str, Dict[str, str]]:
    base = stem[:-2] + stem[-2] + "르"
    return conjugate_regular(base + "다")

def conjugate_irregular_euir(stem: str) -> Dict[str, Dict[str, str]]:
    return conjugate_regular(stem)

# 📦 Main dispatcher

def conjugate_korean_verb(lemma: str) -> Dict[str, Dict[str, str]]:
    category = detect_category(lemma)
    if category == "regular":
        return conjugate_regular(lemma)
    elif category == "ㄷ irregular":
        return conjugate_irregular_d(lemma)
    elif category == "ㅂ irregular":
        return conjugate_irregular_b(lemma)
    elif category == "르 irregular":
        return conjugate_irregular_r(lemma)
    elif category == "으 irregular":
        return conjugate_irregular_euir(lemma)
    elif category == "하 irregular":
        return conjugate_irregular_ha(lemma)
    else:
        raise ValueError(f"Unknown category for {lemma}")

# 🧪 Test
if __name__ == "__main__":
    verbs = ["가다", "자다", "듣다", "덥다", "다르다", "크다", "공부하다"]
    from pprint import pprint
    for lemma in verbs:
        print(f"\n🔹 {lemma}")
        pprint(conjugate_korean_verb(lemma))

# %%
