"""Build tidy, chart-ready data files for the FIT3179 gardening visualisation.

Two data traps are handled explicitly here:
  1. `flower` production is NOT metric tonnes (Malaysia 2014 = 4.99e8), despite the
     portal's generic field description. It is a stem/stalk count. We therefore keep
     flower PLANTED AREA (hectares, reliable) and set flower production to null.
  2. `coconut` is a SUBSET of `industrial_crops` (DOSM methodology lists coconut under
     industrial fats). Summing all nine categories double-counts. We define a
     non-overlapping "edible garden" grouping and never sum all categories.
"""
import csv, json, os, collections

UP = 'data/source'
OUT = 'data'
os.makedirs(OUT, exist_ok=True)

# ---- state code lookup from DOSM's official boundary file -------------------
geo = json.load(open(f'{OUT}/source/dosm_state.geojson'))
CODE = {f['properties']['state']: f['properties']['code_state'] for f in geo['features']}

EDIBLE = ['vegetables', 'fruits', 'herbs', 'spices', 'cash_crops']   # non-overlapping
NO_TONNES = {'flower'}

LABEL = {
    'vegetables': 'Vegetables', 'fruits': 'Fruits', 'herbs': 'Herbs',
    'spices': 'Spices', 'cash_crops': 'Cash crops', 'flower': 'Flowers',
    'paddy': 'Paddy (rice)', 'coconut': 'Coconut', 'industrial_crops': 'Industrial crops',
}

# ---- 1. crops ---------------------------------------------------------------
rows = []
with open(f'{UP}/fit3179_crops_state.csv', newline='') as f:
    for r in csv.DictReader(f):
        yr = int(r['date'][:4])
        ct = r['crop_type']
        area = float(r['planted_area']) if r['planted_area'] else None
        prod = float(r['production']) if r['production'] else None
        if ct in NO_TONNES:
            prod = None
        rows.append({
            'state': r['state'],
            'code': CODE.get(r['state'], ''),
            'year': yr,
            'crop_type': ct,
            'crop_label': LABEL.get(ct, ct),
            'planted_area_ha': area,
            'production_tonnes': prod,
        })

def w(name, fields, data):
    with open(f'{OUT}/{name}', 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=fields)
        wr.writeheader()
        for d in data:
            wr.writerow({k: ('' if d.get(k) is None else d.get(k)) for k in fields})
    print(f'  {name:36s} {len(data):5d} rows  {os.path.getsize(f"{OUT}/{name}"):7d} B')

print('writing:')
w('crops_state.csv', ['state','code','year','crop_type','crop_label','planted_area_ha','production_tonnes'], rows)

# ---- 2. national category trend, indexed to 2014 ----------------------------
nat = {(r['crop_type'], r['year']): r for r in rows if r['state'] == 'Malaysia'}
cats = sorted({c for c, _ in nat})
years = sorted({y for _, y in nat})
cat_rows = []
for c in cats:
    base_a = nat[(c, 2014)]['planted_area_ha']
    base_p = nat[(c, 2014)]['production_tonnes']
    for y in years:
        r = nat[(c, y)]
        cat_rows.append({
            'year': y, 'crop_type': c, 'crop_label': LABEL.get(c, c),
            'planted_area_ha': r['planted_area_ha'],
            'production_tonnes': r['production_tonnes'],
            'area_index_2014': round(100 * r['planted_area_ha'] / base_a, 2) if base_a else None,
            'prod_index_2014': round(100 * r['production_tonnes'] / base_p, 2) if (base_p and r['production_tonnes'] is not None) else None,
            'is_edible_garden': 'yes' if c in EDIBLE else 'no',
        })
# Several categories finish 2024 within a point of each other, so their end-of-line
# labels overlap. Nudge each label just far enough apart to be readable, keeping the
# order intact. The dot still sits on the true value; only the text moves.
def dodge_labels(points, chart_px=400, label_px=15):
    """points: [(key, value)]. Returns {key: label position}."""
    vals = [v for _, v in points]
    if not vals:
        return {}
    span = max(vals) - min(vals)
    gap = span * label_px / chart_px if span else 0
    out, prev = {}, None
    for k, v in sorted(points, key=lambda kv: -kv[1]):
        y = v if prev is None else min(v, prev - gap)
        out[k], prev = y, y
    return out

end = [r for r in cat_rows if r['year'] == 2024]
for field, label_field in [('area_index_2014', 'label_area'), ('prod_index_2014', 'label_prod')]:
    pos = dodge_labels([(r['crop_type'], r[field]) for r in end if r[field] is not None])
    for r in cat_rows:
        r[label_field] = round(pos[r['crop_type']], 3) if (r['year'] == 2024 and r['crop_type'] in pos) else None

w('crops_category_malaysia.csv',
  ['year','crop_type','crop_label','planted_area_ha','production_tonnes','area_index_2014','prod_index_2014','label_area','label_prod','is_edible_garden'],
  cat_rows)

# ---- 3. population ----------------------------------------------------------
pop = {}
# Filtered copy of DOSM's published population_state.csv: the full file is 12.5 MB
# of age/sex/ethnicity breakdowns and only the overall totals are needed here.
with open(f'{UP}/population_state_overall.csv', newline='') as f:
    for r in csv.DictReader(f):
        if r['sex']=='both' and r['age']=='overall' and r['ethnicity']=='overall':
            pop[(r['state'], int(r['date'][:4]))] = float(r['population']) * 1000.0
print('  population keys:', len(pop), '| years', min(y for _,y in pop), '-', max(y for _,y in pop))

# ---- 4. per-state summary ---------------------------------------------------
by = collections.defaultdict(dict)
for r in rows:
    by[(r['state'], r['year'])][r['crop_type']] = r
summ = []
for (st, yr), d in sorted(by.items()):
    if st == 'Malaysia':
        continue
    veg_a = d['vegetables']['planted_area_ha']
    veg_p = d['vegetables']['production_tonnes']
    ed_a = sum((d[c]['planted_area_ha'] or 0) for c in EDIBLE)
    ed_p = sum((d[c]['production_tonnes'] or 0) for c in EDIBLE)
    p = pop.get((st, yr))
    summ.append({
        'state': st, 'code': CODE.get(st, ''), 'year': yr,
        'veg_area_ha': veg_a, 'veg_prod_tonnes': veg_p,
        'edible_area_ha': round(ed_a, 1), 'edible_prod_tonnes': round(ed_p, 1),
        'population': int(p) if p else None,
        'veg_area_ha_per_1000': round(veg_a / p * 1000, 3) if p else None,
        'veg_kg_per_person': round(veg_p * 1000 / p, 1) if p else None,
    })
w('state_summary.csv',
  ['state','code','year','veg_area_ha','veg_prod_tonnes','edible_area_ha','edible_prod_tonnes','population','veg_area_ha_per_1000','veg_kg_per_person'],
  summ)

# ---- 5. climate -------------------------------------------------------------
cl = []
with open(f'{UP}/fit3179_climate_states.csv', newline='') as f:
    for r in csv.DictReader(f):
        days = [31,28,31,30,31,30,31,31,30,31,30,31][int(r['month'])-1]
        cl.append({
            'state': r['state'], 'code': CODE.get(r['state'], ''),
            'city': r['city'], 'month': int(r['month']),
            'month_name': r['month_name'].title(),
            'rain_mm_day': float(r['rain_mm_day']),
            'rain_mm_month': round(float(r['rain_mm_day']) * days, 1),
            'temp_c': float(r['temp_c']), 'tmax_c': float(r['tmax_c']),
            'solar_mj_m2_day': float(r['solar_kwh_m2_day']),   # source unit is MJ/m2/day
        })
w('climate_states.csv',
  ['state','code','city','month','month_name','rain_mm_day','rain_mm_month','temp_c','tmax_c','solar_mj_m2_day'], cl)

# ---- 6. trends --------------------------------------------------------------
# Google Trends returns en-GB month labels ("Jan 2014" ... "Sept 2026"). Normalise to
# ISO YYYY-MM-01 so Vega-Lite parses them as dates rather than guessing at "Sept".
MONTHS = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,
          'Jul':7,'Aug':8,'Sep':9,'Sept':9,'Oct':10,'Nov':11,'Dec':12}

def iso(label):
    mon, yr = label.split()
    m = MONTHS[mon]
    return f'{yr}-{m:02d}-01', m, int(yr)

KW_LABEL = {'berkebun': 'berkebun (to garden)', 'gardening': 'gardening',
            'hidroponik': 'hidroponik (hydroponics)', 'kebun sayur': 'kebun sayur (vegetable garden)'}

tr = json.load(open(f'{UP}/fit3179_trends.json'))
kw = tr['my_timeseries']['keywords']
my = []
for d in tr['my_timeseries']['data']:
    if d['partial']:
        continue
    date, m, y = iso(d['t'])
    for i, k in enumerate(kw):
        my.append({'date': date, 'year': y, 'month': m,
                   'keyword': k, 'keyword_label': KW_LABEL.get(k, k), 'value': d['v'][i]})
w('trends_my_monthly.csv', ['date','year','month','keyword','keyword_label','value'], my)

wd = []
for d in tr['world_timeseries']['data']:
    if d['partial']:
        continue
    date, m, y = iso(d['t'])
    wd.append({'date': date, 'year': y, 'month': m, 'value': d['v']})
w('trends_world_monthly.csv', ['date','year','month','value'], wd)

# Seasonal shape: average index by calendar month, rescaled so each series averages 100.
def season(rows, key='value'):
    acc = collections.defaultdict(list)
    for r in rows:
        acc[r['month']].append(float(r[key]))
    avg = {m: sum(v)/len(v) for m, v in acc.items()}
    grand = sum(avg.values())/len(avg)
    return {m: round(100*v/grand, 1) for m, v in avg.items()}

MN = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
s_my = season([r for r in my if r['keyword'] == 'berkebun'])
s_wd = season(wd)
rain_acc = collections.defaultdict(list)
for r in cl:
    rain_acc[r['month']].append(r['rain_mm_month'])
rain_avg = {m: sum(v)/len(v) for m, v in rain_acc.items()}
rain_grand = sum(rain_avg.values())/len(rain_avg)

w('seasonality.csv', ['month','month_name','malaysia_index','world_index','rainfall_index','rainfall_mm'],
  [{'month': m, 'month_name': MN[m-1],
    'malaysia_index': s_my[m], 'world_index': s_wd[m],
    'rainfall_index': round(100*rain_avg[m]/rain_grand, 1),
    'rainfall_mm': round(rain_avg[m], 1)} for m in range(1, 13)])

gb = {g['code']: g for g in tr['my_geo_berkebun']}
gh = {g['code']: g for g in tr['my_geo_hidroponik']}
geo_rows = []
for c in sorted(set(gb) | set(gh)):
    code = int(c.split('-')[1])
    name = next((s for s, v in CODE.items() if v == code), gb.get(c, gh.get(c))['name'])
    geo_rows.append({'state': name, 'code': code,
                     'berkebun': gb[c]['v'] if c in gb else None,
                     'hidroponik': gh[c]['v'] if c in gh else None})
w('trends_state.csv', ['state','code','berkebun','hidroponik'], geo_rows)
