import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_anomalies(df):
    df = df.copy()

    numeric_df = df.select_dtypes(include=[np.number])

    if not numeric_df.empty:
        model = IsolationForest(contamination=0.2, random_state=42)
        df['iso_flag'] = model.fit_predict(numeric_df) == -1
    else:
        df['iso_flag'] = False

    df['label_flag'] = False

    for i, row in df.iterrows():
        text = str(row.get("text", "")).lower()
        label = str(row.get("label", "")).lower()

        if ("free" in text or "win" in text or "money" in text) and label == "safe":
            df.at[i, 'label_flag'] = True

    df['suspicious'] = df['iso_flag'] | df['label_flag']

    df['score'] = (
        df['iso_flag'].astype(int) +
        df['label_flag'].astype(int)
    ) / 2

    return df