# src/train.py
import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import numpy as np

from preprocess import make_vectorizer

# change DATA_PATH to generated dataset
DATA_PATH = "src/data/generated_dataset.csv"
VEC_PATH = "src/model/vectorizer_v2.joblib"
MODEL_PATH = "src/model/model_v2.joblib"

def load_data(path=DATA_PATH):
    df = pd.read_csv(path, encoding="utf-8")
    df = df.dropna(subset=["text", "label"])
    return df

def prepare_labels(df: pd.DataFrame):
    return df["label"].astype(str).str.lower().map(lambda x: 1 if x == "fake" else 0)

def main():
    print("Loading data...")
    df = load_data()
    X_text = df["text"].astype(str).tolist()
    y = prepare_labels(df)

    print("Splitting...")
    X_train_text, X_test_text, y_train, y_test = train_test_split(
        X_text, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Fitting TF-IDF vectorizer on train text (no leakage)...")
    vec = make_vectorizer(X_train_text, max_features=5000)

    X_train = vec.transform(X_train_text)
    X_test = vec.transform(X_test_text)

    print("Evaluating multiple models...")
    models = {
        "LogisticRegression": LogisticRegression(max_iter=1200, class_weight="balanced", solver="liblinear"),
        "RandomForest": RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
        "MLP": MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
    }

    best_model = None
    best_acc = 0
    best_name = ""

    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        print(f"{name} Accuracy: {acc:.4f}")
        if acc > best_acc:
            best_acc = acc
            best_model = model
            best_name = name

    print(f"\nBest Model: {best_name} with Accuracy: {best_acc:.4f}")
    
    best_preds = best_model.predict(X_test)
    print("\nBest Model Classification Report:\n", classification_report(y_test, best_preds, zero_division=0))

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(best_model, MODEL_PATH)
    joblib.dump(vec, VEC_PATH)

    print("\nSaved best model ->", MODEL_PATH)
    print("Saved vectorizer ->", VEC_PATH)

if __name__ == "__main__":
    main()
