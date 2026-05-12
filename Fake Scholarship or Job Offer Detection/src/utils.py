# src/utils.py
import pandas as pd

def load_sample(n=50, path='src/data/sample_offers.csv'):
    df = pd.read_csv(path)
    return df.sample(min(n, len(df)), random_state=42)
