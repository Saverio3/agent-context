"""Does sewage tell you next week's hospital admissions? (space-time nowcast pilot)

Data: CDC NWSS wastewater viral activity per site (atcp-73re) and NHSN weekly hospital
admissions per state (ua7e-t2fy). Pathogens: COVID, flu A, RSV.

Per state-week: population-weighted mean of log(site_wval). Target: log(admissions+1) h weeks
ahead (h = 1, 2). Models, fitted on weeks before 2025-07-01, tested on the weeks after:
  A  persistence: next week = this week
  B  admissions history (this week, last week, growth)          - ridge
  C  B + own-state wastewater (level, change)
  D  C + neighbouring states' wastewater (4 nearest state centres) - the space-time part
Score: mean absolute error in log terms (≈ % error), and share of weeks where the model
called the direction (up/down) right.
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV

ABBR = {'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA', 'Colorado': 'CO',
        'Connecticut': 'CT', 'Delaware': 'DE', 'District of Columbia': 'DC', 'Florida': 'FL', 'Georgia': 'GA',
        'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
        'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA',
        'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT',
        'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM',
        'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
        'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
        'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
        'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'}
# approximate state centres (lat, lon)
C = {'AL': (32.8, -86.8), 'AK': (64, -150), 'AZ': (34.2, -111.7), 'AR': (34.9, -92.4), 'CA': (37.2, -119.5),
     'CO': (39, -105.5), 'CT': (41.6, -72.7), 'DE': (39, -75.5), 'DC': (38.9, -77), 'FL': (28.6, -82.4),
     'GA': (32.7, -83.4), 'HI': (20.8, -156.3), 'ID': (44.4, -114.6), 'IL': (40, -89.2), 'IN': (39.9, -86.3),
     'IA': (42.1, -93.5), 'KS': (38.5, -98.4), 'KY': (37.5, -85.3), 'LA': (31, -92), 'ME': (45.4, -69.2),
     'MD': (39, -76.8), 'MA': (42.3, -71.8), 'MI': (44.3, -85.4), 'MN': (46.3, -94.3), 'MS': (32.7, -89.7),
     'MO': (38.4, -92.5), 'MT': (47, -109.6), 'NE': (41.5, -99.8), 'NV': (39.3, -116.6), 'NH': (43.7, -71.6),
     'NJ': (40.2, -74.7), 'NM': (34.4, -106.1), 'NY': (42.9, -75.5), 'NC': (35.6, -79.4), 'ND': (47.5, -100.5),
     'OH': (40.3, -82.8), 'OK': (35.6, -97.5), 'OR': (43.9, -120.6), 'PA': (40.9, -77.8), 'RI': (41.7, -71.5),
     'SC': (33.9, -80.9), 'SD': (44.4, -100.2), 'TN': (35.9, -86.4), 'TX': (31.5, -99.3), 'UT': (39.3, -111.7),
     'VT': (44.1, -72.7), 'VA': (37.5, -78.9), 'WA': (47.4, -120.5), 'WV': (38.6, -80.6), 'WI': (44.6, -89.9),
     'WY': (43, -107.5)}
NEAR = {}
for s, (a, b) in C.items():
    d = sorted((np.hypot(a - a2, (b - b2) * np.cos(np.radians(a))), s2) for s2, (a2, b2) in C.items() if s2 != s)
    NEAR[s] = [x for _, x in d[:4]]
PATH = {'SARS-CoV-2': 'totalconfc19newadm', 'Influenza A virus': 'totalconfflunewadm', 'RSV': 'totalconfrsvnewadm'}
NAME = {'SARS-CoV-2': 'COVID', 'Influenza A virus': 'Flu A', 'RSV': 'RSV'}
SPLIT = pd.Timestamp('2025-07-01')

w = pd.read_csv('data/medical/wastewater_levels.csv',
                usecols=['state_territory', 'population_served', 'site_wval', 'week_end', 'pathogen_target'])
w = w[w.state_territory.isin(ABBR) & (w.site_wval > 0)].copy()
w['st'] = w.state_territory.map(ABBR)
w['week'] = pd.to_datetime(w.week_end)
w['lw'] = np.log(w.site_wval)
w['pop'] = w.population_served.fillna(w.population_served.median()).clip(lower=1000)
w['x'] = w.lw * w['pop']
ww = w.groupby(['pathogen_target', 'st', 'week']).agg(x=('x', 'sum'), p=('pop', 'sum'), n=('lw', 'size')).reset_index()
ww['ww'] = ww.x / ww.p

h = pd.read_csv('data/medical/hospital_weekly.csv',
                usecols=['weekendingdate', 'jurisdiction', *PATH.values()])
h['week'] = pd.to_datetime(h.weekendingdate)
h = h[h.jurisdiction.isin(C)].rename(columns={'jurisdiction': 'st'})


def build(path, col):
    a = ww[ww.pathogen_target == path].pivot(index='week', columns='st', values='ww')
    a = a.asfreq('7D') if a.index.is_monotonic_increasing else a
    y = h.pivot_table(index='week', columns='st', values=col)
    y = np.log1p(y.clip(lower=0))
    # week_end dates may differ by weekday: snap both to Saturday
    a.index = a.index + pd.to_timedelta((5 - a.index.weekday) % 7, 'D')
    y.index = y.index + pd.to_timedelta((5 - y.index.weekday) % 7, 'D')
    a = a.groupby(level=0).mean(); y = y.groupby(level=0).mean()
    idx = pd.date_range(max(a.index.min(), y.index.min()), min(a.index.max(), y.index.max()), freq='7D')
    a = a.reindex(idx); y = y.reindex(idx)
    nb = pd.DataFrame({s: a[[n for n in NEAR[s] if n in a]].mean(axis=1) for s in a.columns})
    rows = []
    for s in sorted(set(a.columns) & set(y.columns)):
        d = pd.DataFrame({'y0': y[s], 'y1': y[s].shift(1), 'w0': a[s], 'w1': a[s].shift(1),
                          'n0': nb[s], 'n1': nb[s].shift(1)})
        d['g'] = d.y0 - d.y1; d['wg'] = d.w0 - d.w1; d['ng'] = d.n0 - d.n1
        for hh in (1, 2):
            d[f't{hh}'] = y[s].shift(-hh)
        d['st'] = s
        rows.append(d)
    return pd.concat(rows).rename_axis('week').reset_index()


FEATS = {'B': ['y0', 'y1', 'g'], 'C': ['y0', 'y1', 'g', 'w0', 'w1', 'wg'],
         'D': ['y0', 'y1', 'g', 'w0', 'w1', 'wg', 'n0', 'n1', 'ng']}
out = ["# Wastewater → hospital admissions (space-time nowcast)", "",
       f"Train: weeks before {SPLIT.date()} · test: weeks after (out-of-sample). Error = mean absolute error of "
       "log(admissions+1), roughly the typical % miss. Direction = share of state-weeks where the model called "
       "rise vs fall correctly (persistence can't call direction, so it's blank).", "",
       "| Disease | Weeks ahead | Test state-weeks | A: same as this week | B: + admission trend | C: + own sewage | "
       "D: + neighbours' sewage | Gain D vs B | Direction B → D |", "|---|---|---|---|---|---|---|---|---|"]
lead = ["", "## Does sewage move first?", "",
        "Correlation between this week's change in sewage and the change in admissions k weeks later "
        "(all states, all weeks). Peak at k > 0 means sewage leads.", "",
        "| Disease | k=0 | k=1 | k=2 | k=3 |", "|---|---|---|---|---|"]
for path, col in PATH.items():
    d = build(path, col)
    lc = []
    for k in range(4):
        fut = d.groupby('st').y0.shift(-k) - d.groupby('st').y1.shift(-k)
        m = d.wg.notna() & fut.notna()
        lc.append(np.corrcoef(d.wg[m], fut[m])[0, 1])
    lead.append(f"| {NAME[path]} | " + " | ".join(f"{x:.2f}" for x in lc) + " |")
    for hh in (1, 2):
        t = f't{hh}'
        dd = d.dropna(subset=FEATS['D'] + [t])
        dd = dd[dd.y0 > 0]
        tr, te = dd[dd.week < SPLIT], dd[dd.week >= SPLIT]
        if len(te) < 50 or len(tr) < 200:
            out.append(f"| {NAME[path]} | {hh} | {len(te)} | not enough overlap | | | | | |"); continue
        err = {'A': np.mean(np.abs(te[t] - te.y0))}
        dirs = {}
        truth = np.sign(te[t] - te.y0)
        for k, f in FEATS.items():
            m = RidgeCV(alphas=np.logspace(-3, 3, 13)).fit(tr[f], tr[t] - tr.y0)
            p = te.y0 + m.predict(te[f])
            err[k] = np.mean(np.abs(te[t] - p))
            dirs[k] = np.mean(np.sign(p - te.y0)[truth != 0] == truth[truth != 0])
        out.append(f"| {NAME[path]} | {hh} | {len(te):,} | {err['A']:.3f} | {err['B']:.3f} | {err['C']:.3f} | "
                   f"{err['D']:.3f} | {1 - err['D'] / err['B']:+.1%} | {dirs['B']:.0%} → {dirs['D']:.0%} |")
    print(NAME[path], 'done')
open('results/medical/WASTEWATER.md', 'w').write("\n".join(out + lead) + "\n")
print("\n".join(out + lead))
