from sklearn.ensemble import IsolationForest
import pandas as pd

def train_isolation_forest(df):
    features = df[["cpu_usage", "disk_usage", "memory_usage", "swap"]]  # But swap data is not quite useful
    model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    model.fit(features)
    return model

def detect_anomalies(model, df):
    features = df[["cpu_usage", "disk_usage", "memory_usage", "swap"]]
    df["anomaly"] = model.predict(features)
    return df[df["anomaly"] == -1]
