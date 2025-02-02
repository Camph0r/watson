from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import pickle

def train_dbscan(df):
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(df[['cpu_percent', 'mem_percent', 'threads']])
    dbscan = DBSCAN(eps=1.5, min_samples=5)
    dbscan.fit(features_scaled)
    return dbscan

def save_dbscan_model(model, user):
    model_path = f"saved/{user}/dbscan.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)

def load_dbscan_model(user):
    model_path = f"saved/{user}/dbscan.pkl"
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model

def detect_anomalies_dbscan(df, model):
  
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(df[['cpu_percent', 'mem_percent', 'threads']])
    df['anomaly'] = model.fit_predict(features_scaled)
    return df[df['anomaly'] == -1]
