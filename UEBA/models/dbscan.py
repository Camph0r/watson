from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN


## Todos: Traing the model
def detect_anomalies_dbscan(df):
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(df[['cpu_percent', 'mem_percent', 'threads']])
    dbscan = DBSCAN(eps=1.5, min_samples=5)
    df['anomaly'] = dbscan.fit_predict(features_scaled)
    return df[df['anomaly'] == -1]
