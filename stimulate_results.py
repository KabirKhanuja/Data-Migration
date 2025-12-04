"""
Returns dictionaries with
- migration_time 
- per query latencies for SELECT, INSERT, UPDATE, DELETE, JOIN
- storage usage : data, index, total
- consistency 
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, Any

DEFAULT_SEED = 42

BASELINES = {
    'Postgres': {
        'mig_time_center': 118.0,
        'query_center': {'SELECT': 0.84, 'INSERT': 1.55, 'UPDATE': 1.68, 'DELETE': 1.62, 'JOIN': 2.08},
        'data_mb': 270,
        'index_mb': 66,
        'consistency_center': 99.9
    },
    'MySQL': {
        'mig_time_center': 103.0,
        'query_center': {'SELECT': 0.91, 'INSERT': 1.42, 'UPDATE': 1.76, 'DELETE': 1.59, 'JOIN': 2.41},
        'data_mb': 256,
        'index_mb': 48,
        'consistency_center': 99.4
    },
    'SQLite': {
        'mig_time_center': 78.0,
        'query_center': {'SELECT': 1.32, 'INSERT': 1.12, 'UPDATE': 1.49, 'DELETE': 1.36, 'JOIN': 3.12},
        'data_mb': 242,
        'index_mb': 12,
        'consistency_center': 98.8
    }
}

def rnd_gauss(center, rel_std=0.08):
    return float(np.random.normal(loc=center, scale=abs(center)*rel_std))

def simulate_metrics(databases=('MySQL','Postgres','SQLite'),
                     seed: int = DEFAULT_SEED,
                     jitter: float = 0.12) -> Dict[str, Dict[str, Any]]:

    np.random.seed(seed)
    random.seed(seed)
    out = {}
    for db in databases:
        key = 'Postgres' if 'post' in db.lower() else db  
        if key not in BASELINES:
            key = db 
        b = BASELINES.get(key, BASELINES['MySQL'])
       
        mig = rnd_gauss(b['mig_time_center'], rel_std=jitter)
        mig = max(10.0, mig)  
        queries = {}
        for q, center in b['query_center'].items():
            variance = jitter * (1.5 if q == 'JOIN' else 1.0)
            val = rnd_gauss(center, rel_std=variance)
            queries[q] = max(0.1, round(val, 3))
        data_mb = max(10.0, rnd_gauss(b['data_mb'], rel_std=jitter))
        index_mb = max(0.0, rnd_gauss(b['index_mb'], rel_std=jitter*1.2))
        total_mb = round(data_mb + index_mb, 2)
        consistency = max(90.0, round(rnd_gauss(b['consistency_center'], rel_std=jitter/2), 3))
        out[db] = {
            'migration_time_s': round(mig, 3),
            'query_ms': queries,
            'storage_mb': {'data': round(data_mb,2), 'index': round(index_mb,2), 'total': total_mb},
            'consistency_pct': consistency
        }
    return out

def to_dataframe(sim_out: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    """Flatten simulated output into a table-friendly DataFrame."""
    rows = []
    for db, v in sim_out.items():
        row = {
            'db': db,
            'migration_time_s': v['migration_time_s'],
            'consistency_pct': v['consistency_pct'],
            'data_mb': v['storage_mb']['data'],
            'index_mb': v['storage_mb']['index'],
            'total_mb': v['storage_mb']['total']
        }
        for q, t in v['query_ms'].items():
            row[f'latency_{q.lower()}_ms'] = t
        rows.append(row)
    return pd.DataFrame(rows)

if __name__ == '__main__':
    sim = simulate_metrics(seed=1234, jitter=0.15)
    df = to_dataframe(sim)
    print(df.to_string(index=False))