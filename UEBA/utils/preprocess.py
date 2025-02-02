def detect_unusual_processes(df, baseline):
    return df[~df['name'].isin(baseline.index)]
    

def detect_high_resource_usage(df):
    z_scores = (df[['cpu_percent', 'mem_percent', 'threads']] - df[['cpu_percent', 'mem_percent', 'threads']].mean()) / df[['cpu_percent', 'mem_percent', 'threads']].std()
    return df[(z_scores > 2).any(axis=1)]
    

def detect_long_running_processes(df):
    runtimes = (df['created'].max() - df['created']).dt.total_seconds()
    return df[runtimes > runtimes.mean() + 2 * runtimes.std()]
    

def detect_anomalous_start_times(df):
    start_times = df.groupby('name')['created'].apply(lambda x: x.dt.hour.value_counts().idxmax())
    return df[df.apply(lambda row: row['created'].hour != start_times.get(row['name'], row['created'].hour), axis=1)]
    

def process_anomaly_detection(df):
    baseline = df.groupby('name').agg({
        'cpu_percent': ['mean', 'std'],
        'mem_percent': ['mean', 'std'],
        'threads': ['mean', 'std'],
        'created': ['min', 'max']
    })
    unusual_processes = detect_unusual_processes(df, baseline)
    high_resource_usage = detect_high_resource_usage(df)
    long_running = detect_long_running_processes(df)
    anomalous_start_times = detect_anomalous_start_times(df)

    return {
        "unusual_processes": unusual_processes,
        "high_resource_usage": high_resource_usage,
        "long_running": long_running,
        "anomalous_start_times": anomalous_start_times
    }
    


    