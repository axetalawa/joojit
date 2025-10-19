# affect.py
import os
from collections import defaultdict
import langid

# ---------------------------
# Global lexicon cache
# ---------------------------
LEXICONS = {}

# Base directory for dictionaries
BASE_DIR = os.path.join(os.path.dirname(__file__), "dictionaries")

# ---------------------------
# Load lexicon dynamically
# ---------------------------
def load_lexicon(lang="en"):
    """
    Load NRC lexicon for the given language.
    If unavailable, fallback to English.
    """
    filename = f"emotion_lexicon_{lang}.txt"
    path = os.path.join(BASE_DIR, filename)

    lexicon = defaultdict(dict)
    if not os.path.exists(path):
        if lang != "en":
            print(f"⚠️ No lexicon found for '{lang}'. Falling back to English.")
            return load_lexicon("en")
        else:
            print(f"⚠️ English lexicon not found at {path}. Affect metrics disabled.")
            return lexicon

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 3:
                word, emotion, value = parts
                lexicon[word.lower()][emotion] = int(value)

    print(f"✅ Loaded lexicon for '{lang}' ({len(lexicon)} words).")
    return lexicon


# ---------------------------
# Detect language
# ---------------------------
def detect_language(text):
    """
    Detect language of a text using langid.
    Returns language code (e.g. 'en', 'pt', 'es').
    """
    try:
        lang, prob = langid.classify(text)
        if prob < 0.75:
            # If confidence is low, default to English
            return "en"
        return lang
    except Exception:
        return "en"


# ---------------------------
# Compute affect
# ---------------------------
def compute_affect(text, lang=None):
    """
    Compute normalized emotion scores for the given text.
    Automatically detects language if not provided.
    """
    if not text.strip():
        return {}

    if lang is None:
        lang = detect_language(text)

    if lang not in LEXICONS:
        LEXICONS[lang] = load_lexicon(lang)

    lexicon = LEXICONS.get(lang, {})
    words = text.lower().split()
    scores = defaultdict(int)
    count = 0

    for w in words:
        if w in lexicon:
            for emo, val in lexicon[w].items():
                scores[emo] += val
            count += 1

    if count > 0:
        for emo in scores:
            scores[emo] /= count

    return dict(scores)
