import numpy as np
import pandas as pd

data = {
    'DB': ['MySQL','Postgres','SQLite'],
    'T_mig': [102.8, 118.5, 78.3],
    'T_q': [1.62, 1.55, 1.68],
    'eta_s': [84.2, 80.3, 95.3],
    'C_r': [99.4, 99.9, 98.8]
}
df = pd.DataFrame(data)
for col in ['T_mig','T_q','eta_s','C_r']:
    mn, mx = df[col].min(), df[col].max()
    df['n_'+col] = (df[col] - mn) / (mx - mn) if mx!=mn else 1.0

# compute MPI = (n_Cr * n_eta_s) / (n_T_mig * n_T_q)
df['MPI'] = (df['n_C_r'] * df['n_eta_s']) / (df['n_T_mig'] * df['n_T_q'])
print(df[['DB','MPI']].sort_values('MPI', ascending=False))