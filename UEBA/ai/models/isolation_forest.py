from sklearn.ensemble import IsolationForest
import os
import pickle

def train_iforest(df):
    features = df[["cpu_usage", "disk_usage", "memory_usage", "swap", "packetsSent", "packetsRecv"]]  # But swap data is not quite useful
    model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    model.fit(features)
    return model

def save_iforest_model(model, user):
    model_path = f"saved/{user}/iforest.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)

def load_iforest_model(user):
    model_path = f"saved/{user}/iforest.pkl"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No model found for user: {user}")
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model


def detect_anomalies_iforest(df, model):
    if df.empty:
        return df

    features = df[["cpu_usage", "disk_usage", "memory_usage", "swap", "packetsSent", "packetsRecv"]]
    df["anomaly"] = model.predict(features)
    return df
