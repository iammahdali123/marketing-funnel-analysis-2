# backend/analytics.py
from collections import OrderedDict
import pandas as pd
from datetime import datetime

def load_events_df(engine):
    df = pd.read_sql_table('events', con=engine)
    if df.empty:
        return df
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def compute_funnel(df, funnel_steps):
    df = df.sort_values(['user_id','timestamp'])
    users = df['user_id'].unique()
    step_counts = OrderedDict((step, 0) for step in funnel_steps)
    for uid in users:
        u = df[df['user_id'] == uid]
        for step in funnel_steps:
            if step in u['event'].values:
                step_counts[step] += 1
    steps = list(step_counts.keys())
    counts = list(step_counts.values())
    total = counts[0] if counts else 0
    conversion = [ (c/total) if total>0 else 0.0 for c in counts ]
    dropoffs = []
    for i in range(len(counts)-1):
        a,b = counts[i], counts[i+1]
        drop = (a-b)/a if a>0 else 0.0
        dropoffs.append({'from': steps[i], 'to': steps[i+1], 'count_from': a, 'count_to': b, 'drop_rate': drop})
    return {'steps': steps, 'counts': counts, 'conversion': conversion, 'dropoffs': dropoffs, 'total_users': int(total)}

def top_dropoff(dropoffs):
    if not dropoffs:
        return None
    return max(dropoffs, key=lambda r: r['drop_rate'])
