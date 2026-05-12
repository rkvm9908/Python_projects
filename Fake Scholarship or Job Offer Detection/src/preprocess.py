# src/preprocess.py
import re
import string
import joblib
import os
from typing import List, Dict, Any
from datetime import datetime

# small stopword set (fast, no NLTK dependency)
STOPWORDS_SET = {
    'the','is','am','are','was','were','be','been','to','and','or','in','on','for','at',
    'of','a','an','this','that','with','by','as','it','from','your','you','we','our','please','dear'
}

# -------------------------
# basic text cleaning
# -------------------------
def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.strip()
    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"\d+", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text

# -------------------------
# tokenizer (unigram + bigram) for TF-IDF
# -------------------------
def custom_tokenizer(text: str) -> List[str]:
    cleaned = clean_text(text)
    tokens = cleaned.split()
    filtered = [t for t in tokens if t not in STOPWORDS_SET and len(t) > 1]
    out = filtered.copy()
    for i in range(len(filtered) - 1):
        out.append(filtered[i] + " " + filtered[i+1])
    return out

# -------------------------
# vectorizer creation (fit on train corpus)
# -------------------------
def make_vectorizer(corpus: list, max_features: int = 5000):
    """
    Fits a TfidfVectorizer using the custom_tokenizer.
    Use higher max_features when using larger generated dataset.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    vec = TfidfVectorizer(analyzer=custom_tokenizer, max_features=max_features)
    vec.fit(corpus)
    return vec

# -------------------------
# small engineered metadata extractor
# -------------------------
def extract_metadata_features(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given a data row/dict (from generated dataset), extract simple numeric/categorical features.
    These are optional and not currently used by the baseline model, but useful to extend models later.
    Expected keys in row: 'text','contact_email','has_link','amount','created_at'
    """
    txt = row.get("text", "") or ""
    email = row.get("contact_email", "") or ""
    amount = row.get("amount", "")
    has_link = int(row.get("has_link", 0) or 0)

    # numeric features
    tokens = clean_text(txt).split()
    num_tokens = len(tokens)
    uppercase_ratio = sum(1 for c in txt if c.isupper()) / max(1, len(txt))

    # simple contact domain feature
    domain = ""
    if "@" in email:
        domain = email.split("@")[-1].lower()
    is_generic_email = int(domain in ("gmail.com", "yahoo.com", "hotmail.com", "outlook.com"))

    has_amount = 1 if amount not in (None, "", 0) else 0

    # recency: days since created_at (if present)
    recency_days = None
    created_at = row.get("created_at", "")
    try:
        dt = datetime.fromisoformat(created_at)
        recency_days = (datetime.now() - dt).days
    except Exception:
        recency_days = -1  # unknown

    return {
        "num_tokens": num_tokens,
        "uppercase_ratio": uppercase_ratio,
        "is_generic_email": is_generic_email,
        "has_link": has_link,
        "has_amount": has_amount,
        "recency_days": recency_days
    }

# -------------------------
# save / load helpers
# -------------------------
def save_vectorizer(vec, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(vec, path)

def load_vectorizer(path: str):
    return joblib.load(path)
