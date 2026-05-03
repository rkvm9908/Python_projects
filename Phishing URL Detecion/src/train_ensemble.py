import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import glob
from joblib import dump
from tqdm import tqdm
from joblib import Parallel, delayed
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.utils import resample
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from xgboost import XGBClassifier
from extract_features import extract_features 

# --- 1. Setup and Load Data ---
print("\n" + "="*50)
print(f"{'PHISHING DETECTION SYSTEM TRAINING':^50}")
print("="*50)

os.makedirs("models", exist_ok=True)
os.makedirs("src/static/img", exist_ok=True)

all_csv_files = glob.glob(os.path.join('dataset', '*.csv'))
if not all_csv_files:
    print("FATAL ERROR: No CSV files found. Exiting.")
    exit()

df_list = []
for file_path in all_csv_files:
    df_chunk = pd.read_csv(file_path)
    df_list.append(df_chunk)
    print(f"[+] Loaded {os.path.basename(file_path)}: {len(df_chunk)} rows")

df = pd.concat(df_list, ignore_index=True).dropna(subset=['url'])
df['url'] = df['url'].astype(str)
df.columns = df.columns.str.lower().str.strip()
df = df.rename(columns={'url': 'URL', 'type': 'label'})
# Clean column names
df.columns = df.columns.str.strip().str.lower()

# Remove duplicate columns if any
df = df.loc[:, ~df.columns.duplicated()]

# Ensure label column exists
if 'type' in df.columns and 'label' not in df.columns:
    df = df.rename(columns={'type': 'label'})

print("Final Columns:", df.columns.tolist())

# Clean label values
df['label'] = df['label'].astype(str).str.strip().str.lower()
df['label'] = df['label'].replace({
    'legitimate': 'legit',
    'safe': 'legit',
    'phishing': 'phishing',
    'malicious': 'phishing',
    'bad': 'phishing'
})

# Label Mapping
df['label'] = df['label'].str.lower().replace({
    'legitimate': 'legit', 'safe': 'legit', 
    'phishing': 'phishing', 'malicious': 'phishing', 'bad': 'phishing' 
})
df['label_num'] = df['label'].apply(lambda x: 1 if x == 'phishing' else 0)

# --- 2. Parallel Feature Extraction with Progress Bar ---
print("\n[*] PHASE 1: EXTRACTING 45 FEATURES (PARALLEL)...")

def process_url(url):
    try:
        # extract_features returns a DataFrame row
        return extract_features(url).iloc[0].to_dict()
    except:
        return None

# Parallel processing for speed
url_list = df['url'].tolist()
extracted_data = Parallel(n_jobs=-1)(
    delayed(process_url)(u) for u in tqdm(url_list, desc="Processing URLs", unit="url")
)

# Filtering and Merging
extracted_data = [f for f in extracted_data if f is not None]
df_features = pd.DataFrame(extracted_data)
df = pd.concat([df.reset_index(drop=True), df_features.reset_index(drop=True)], axis=1)

print(f"\n[✓] Feature extraction complete. Total: {len(df)}")

# --- 3. Balancing Data ---
print("\n[*] PHASE 2: BALANCING CLASSES (UPSAMPLING)...")
ph_df = df[df["label"] == "phishing"]
lg_df = df[df["label"] == "legit"]

min_df, max_df = (ph_df, lg_df) if len(ph_df) < len(lg_df) else (lg_df, ph_df)

min_up = resample(min_df, replace=True, n_samples=len(max_df), random_state=42)
df_balanced = pd.concat([max_df, min_up]).sample(frac=1, random_state=42).reset_index(drop=True)

print(f"[✓] Balanced Dataset Size: {len(df_balanced)} (1:1 Ratio)")

# --- 4. Training Preparation ---
SELECTED_FEATURE_COLUMNS = [
    "URLLength", "HostnameLength", "PathLength", "QueryLength", "NoOfDigits", 
    "NoOfLetters", "NoOfDots", "NoOfHyphens", "NoOfUnderscore", "NoOfSlash", 
    "NoOfQuestionMark", "NoOfEqual", "NoOfAt", "NoOfAmpersand", "NoOfExclamation", 
    "NoOfHash", "NoOfPercent", "NoOfTilde", "NoOfComma", "NoOfPlus", "NoOfAsterisk", 
    "NoOfDollar", "NoOfSpace", "NoOfSubdomains", "NoOfSubDir", "IsDomainIP", 
    "IsHTTPS", "IsWWW", "IsShortened", "HasSensitiveWord", "HasPort", 
    "AbnormalDoubleSlash", "DigitRatio", "LetterRatio", "SymbolCount", "SymbolRatio", 
    "DomainDigitCount", "DomainDigitRatio", "IsSuspiciousTLD", "RedirectInURL", 
    "NoOfUppercase", "UppercaseRatio", "URLEntropy", "IsPunycode", "IsBrandSpoofed"  
]

X = df_balanced[SELECTED_FEATURE_COLUMNS]
y = df_balanced['label'] 

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

le = LabelEncoder()
y_train_enc = le.fit_transform(y_train)
y_test_enc = le.transform(y_test)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train) 
X_test_scaled = scaler.transform(X_test)

# --- 5. Training Ensemble Model ---
print("\n[*] PHASE 3: TRAINING ENSEMBLE MODEL (RF + XGB)...")
rf = RandomForestClassifier(n_estimators=350, max_depth=12, random_state=42, n_jobs=-1)
xgb = XGBClassifier(n_estimators=250, max_depth=6, learning_rate=0.1, n_jobs=-1, random_state=42)

ensemble = VotingClassifier(estimators=[("rf", rf), ("xgb", xgb)], voting="soft", n_jobs=-1)
ensemble.fit(X_train_scaled, y_train_enc)

# --- 6. Evaluation ---
print("\n" + "-"*30)
print(f"{'FINAL EVALUATION':^30}")
print("-" * 30)

scores = cross_val_score(ensemble, X_train_scaled, y_train_enc, cv=5, n_jobs=-1)
preds = ensemble.predict(X_test_scaled)
acc = accuracy_score(y_test_enc, preds)

print(f"Mean CV Accuracy: {scores.mean():.4f}")
print(f"Final Test Accuracy: {acc:.4f}")

print("\n[+] Confusion Matrix:")
print(confusion_matrix(y_test_enc, preds))

print("\n[+] Classification Report:")
print(classification_report(y_test_enc, preds, target_names=le.classes_))

# --- 7. Saving Artifacts ---
dump(ensemble, "models/ensemble_model.joblib", compress=3)
dump(scaler, "models/scaler.joblib")
dump(le, "models/label_encoder.joblib")

# Save Metrics for UI
with open("models/ensemble_metrics.json", "w") as f:
    json.dump({"accuracy": float(acc), "cv_mean": float(scores.mean())}, f)

print("\n" + "="*50)
print("SUCCESS: Model training complete. Files saved in 'models/'.")
print("="*50)