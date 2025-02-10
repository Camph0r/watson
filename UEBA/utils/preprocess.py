from utils.logger import log_anomaly

# this is a test script to simulate the process using stats
def detect_unusual_processes(df, baseline, hostname):
    result =  df[~df['name'].isin(baseline.index)]
    for _, row in result.iterrows():
        log_anomaly("Unusual Process", hostname, "warning", row.to_dict())
    

def detect_high_resource_usage(df, hostname):
    z_scores = (df[['cpu_percent', 'mem_percent', 'threads']] - df[['cpu_percent', 'mem_percent', 'threads']].mean()) / df[['cpu_percent', 'mem_percent', 'threads']].std()
    result = df[(z_scores > 2).any(axis=1)]
    for _, row in result.iterrows():
        log_anomaly("High Resource Usage", hostname, "warning", row.to_dict())
    

def detect_long_running_processes(df, hostname):
    runtimes = (df['created'].max() - df['created']).dt.total_seconds()
    result=  df[runtimes > runtimes.mean() + 2 * runtimes.std()]
    for _, row in result.iterrows():
        log_anomaly("Long Running Process", hostname, "warning", row.to_dict())

    

def detect_anomalous_start_times(df, hostname):
    start_times = df.groupby('name')['created'].apply(lambda x: x.dt.hour.value_counts().idxmax())
    result=  df[df.apply(lambda row: row['created'].hour != start_times.get(row['name'], row['created'].hour), axis=1)]
    for _, row in result.iterrows():
        log_anomaly("Anomalous Start Time", hostname, "warning", row.to_dict())

    

def process_anomaly_detection(df, hostname):
    baseline = df.groupby('name').agg({
        'cpu_percent': ['mean', 'std'],
        'mem_percent': ['mean', 'std'],
        'threads': ['mean', 'std'],
        'created': ['min', 'max']
    })
    detect_unusual_processes(df, baseline, hostname)
    detect_high_resource_usage(df, hostname)
    detect_long_running_processes(df, hostname)
    detect_anomalous_start_times(df, hostname)


    


    