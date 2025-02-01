import pandas as pd
## Need prepocessor for boht harwae and software metrics
def preprocess_data(df):
    baseline = df.groupby('name').agg({'cpu_percent': ['mean', 'std'], 'mem_percent': ['mean', 'std'], 'threads': ['mean', 'std'], 'created': ['min', 'max']})
    z_scores = (df[['cpu_percent', 'mem_percent', 'threads']] - df[['cpu_percent', 'mem_percent', 'threads']].mean()) / df[['cpu_percent', 'mem_percent', 'threads']].std()
    high_resource = df[(z_scores > 2).any(axis=1)]
    runtimes = (df['created'].max() - df['created']).dt.total_seconds()
    long_running = df[runtimes > runtimes.mean() + 2 * runtimes.std()]
    return high_resource, long_running