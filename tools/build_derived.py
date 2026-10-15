"""Derive the extra data each advanced idiom needs: centroids, bivariate classes,
waffle allocation, and the driest planting window per state."""
import csv, json, collections

OUT = 'data'
R = lambda p: list(csv.DictReader(open(f'{OUT}/{p}')))

def w(name, fields, data):
    with open(f'{OUT}/{name}', 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=fields); wr.writeheader()
        for d in data: wr.writerow({k: ('' if d.get(k) is None else d[k]) for k in fields})
    print(f'  {name:28s} {len(data):4d} rows')

# ---------- 1. centroids: centroid of each state's LARGEST polygon ------------
# A naive centroid over all rings of a MultiPolygon can land in the sea (Sabah,
# Sarawak and Penang all have outlying islands), so we use the biggest ring only.
def ring_area_centroid(ring):
    a = cx = cy = 0.0
    for i in range(len(ring) - 1):
        x0, y0 = ring[i][0], ring[i][1]
        x1, y1 = ring[i+1][0], ring[i+1][1]
        cross = x0*y1 - x1*y0
        a += cross; cx += (x0+x1)*cross; cy += (y0+y1)*cross
    if a == 0: return 0.0, ring[0][0], ring[0][1]
    a *= 0.5
    return abs(a), cx/(6*a), cy/(6*a)

geo = json.load(open(f'{OUT}/source/dosm_state.geojson'))
cent = []
for f in geo['features']:
    best = (0, 0, 0)
    polys = f['geometry']['coordinates']
    if f['geometry']['type'] == 'Polygon': polys = [polys]
    for poly in polys:
        area, x, y = ring_area_centroid(poly[0])
        if area > best[0]: best = (area, x, y)
    cent.append({'state': f['properties']['state'], 'code': f['properties']['code_state'],
                 'lon': round(best[1], 4), 'lat': round(best[2], 4)})
w('state_centroids.csv', ['state','code','lon','lat'], sorted(cent, key=lambda r: r['code']))

CODE = {c['state']: c['code'] for c in cent}

# ---------- 2. bivariate classes: search interest x growing intensity ---------
summ = {r['state']: r for r in R('state_summary.csv') if r['year'] == '2024'}
summ14 = {r['state']: r for r in R('state_summary.csv') if r['year'] == '2014'}
tr = {r['state']: r for r in R('trends_state.csv')}

def tertile_breaks(vals):
    s = sorted(vals)
    n = len(s)
    return s[n//3], s[2*n//3]

states = [s for s in summ if s in tr]
grow_vals = [float(summ[s]['veg_area_ha_per_1000'] or 0) for s in states]
int_vals  = [float(tr[s]['berkebun'] or 0) for s in states]
gb1, gb2 = tertile_breaks(grow_vals)
ib1, ib2 = tertile_breaks(int_vals)

def cls(v, b1, b2): return 1 if v < b1 else (2 if v < b2 else 3)

# Stevens-style bivariate ramp: x = interest (terracotta), y = growing (green)
BI = {(1,1):'#E8E6DF',(2,1):'#E3C4AE',(3,1):'#D89A74',
      (1,2):'#A9C6A6',(2,2):'#A7A98A',(3,2):'#C08A62',
      (1,3):'#5E9460',(2,3):'#6E8C5A',(3,3):'#8A7A44'}

rows = []
for s in states:
    g = float(summ[s]['veg_area_ha_per_1000'] or 0); i = float(tr[s]['berkebun'] or 0)
    gc, ic = cls(g, gb1, gb2), cls(i, ib1, ib2)
    rows.append({'state': s, 'code': CODE[s],
                 'interest': i, 'grow_per_1000': round(g, 3),
                 'interest_class': ic, 'grow_class': gc,
                 'bi_class': f'{ic}-{gc}', 'bi_color': BI[(ic, gc)]})
w('bivariate_state.csv', ['state','code','interest','grow_per_1000','interest_class','grow_class','bi_class','bi_color'], rows)

leg = [{'interest_class': i, 'grow_class': g, 'bi_class': f'{i}-{g}', 'bi_color': BI[(i, g)]}
       for i in (1,2,3) for g in (1,2,3)]
w('bivariate_legend.csv', ['interest_class','grow_class','bi_class','bi_color'], leg)
print(f'   breaks: interest {ib1:.0f} / {ib2:.0f}   growing {gb1:.2f} / {gb2:.2f} ha per 1,000')

# ---------- 3. waffle: 100 squares = national vegetable area, 2024 -----------
tot = sum(float(summ[s]['veg_area_ha']) for s in summ)
shares = {s: float(summ[s]['veg_area_ha']) / tot * 100 for s in summ}
floors = {s: int(shares[s]) for s in shares}
rem = 100 - sum(floors.values())
for s in sorted(shares, key=lambda k: -(shares[k] - floors[k]))[:rem]:
    floors[s] += 1
order = sorted(floors, key=lambda s: -shares[s])
cells, i = [], 0
for s in order:
    for _ in range(floors[s]):
        cells.append({'index': i, 'row': i // 10, 'col': i % 10, 'state': s,
                      'share_pct': round(shares[s], 1), 'squares': floors[s]}); i += 1
w('waffle_vegetable_share.csv', ['index','row','col','state','share_pct','squares'], cells)
print('   waffle top:', ', '.join(f'{s} {floors[s]}' for s in order[:4]))

# ---------- 4. driest 3-month planting window per state ----------------------
REGION = {'Perlis':'North','Kedah':'North','Pulau Pinang':'North','Perak':'North',
          'Selangor':'Central','W.P. Kuala Lumpur':'Central','W.P. Putrajaya':'Central',
          'Negeri Sembilan':'Central','Melaka':'South','Johor':'South',
          'Pahang':'East Coast','Terengganu':'East Coast','Kelantan':'East Coast',
          'Sabah':'Borneo','Sarawak':'Borneo','W.P. Labuan':'Borneo'}
cl = R('climate_states.csv')
by = collections.defaultdict(dict)
for r in cl: by[r['state']][int(r['month'])] = float(r['rain_mm_month'])
MN = ['January','February','March','April','May','June','July','August','September','October','November','December']
pw = []
for s, d in by.items():
    best = min(range(1, 13), key=lambda m: sum(d[((m-1+k) % 12)+1] for k in range(3)))
    months = [((best-1+k) % 12)+1 for k in range(3)]
    pw.append({'state': s, 'code': CODE[s], 'region': REGION[s],
               'start_month': best, 'end_month': months[-1],
               'window_label': f'{MN[months[0]-1]}–{MN[months[-1]-1]}',
               'window_rain_mm': round(sum(d[m] for m in months), 0),
               'driest_month': min(d, key=d.get),
               'driest_month_name': MN[min(d, key=d.get)-1],
               'wettest_month': max(d, key=d.get),
               'wettest_month_name': MN[max(d, key=d.get)-1],
               'annual_rain_mm': round(sum(d.values()), 0)})
w('planting_window.csv', ['state','code','region','start_month','end_month','window_label',
                          'window_rain_mm','driest_month','driest_month_name',
                          'wettest_month','wettest_month_name','annual_rain_mm'],
  sorted(pw, key=lambda r: (r['region'], r['state'])))

# ---------- 5. state change 2014 -> 2024 (dumbbell + spike map) --------------
chg = []
for s in states:
    a14 = float(summ14[s]['veg_area_ha']); a24 = float(summ[s]['veg_area_ha'])
    if a14 == 0 and a24 == 0:
        continue                      # W.P. Kuala Lumpur reports no commercial crop area
    pct = (a24/a14 - 1) * 100 if a14 else None
    c = next(x for x in cent if x['state'] == s)
    chg.append({'state': s, 'code': CODE[s], 'lon': c['lon'], 'lat': c['lat'],
                'area_2014': a14, 'area_2024': a24,
                'pct_change': round(pct, 1) if pct is not None else None,
                'direction': 'Increase' if pct and pct > 0 else 'Decrease'})
# Spike length: degrees of latitude, capped so Kelantan's +156% stays on the map.
SPIKE_MAX_DEG = 2.6
mx = max(abs(r['pct_change']) for r in chg)
for r in chg:
    r['lat_end'] = round(r['lat'] + SPIKE_MAX_DEG * r['pct_change'] / mx, 4)
    # Put each label just beyond the free end of its spike: above an upward spike,
    # below a downward one, so labels never sit on top of the line they describe.
    r['label_lat'] = round(r['lat_end'] + (0.30 if r['pct_change'] > 0 else -0.42), 4)
w('state_change.csv', ['state','code','lon','lat','lat_end','label_lat','area_2014','area_2024','pct_change','direction'],
  sorted(chg, key=lambda r: -r['pct_change']))

# ---------- 6. waffle grouped to top 6 states + "Other states" ---------------
cells2 = []
top = [s for s in order[:6]]
for c in csv.DictReader(open(f'{OUT}/waffle_vegetable_share.csv')):
    c['group'] = c['state'] if c['state'] in top else 'Other states'
    cells2.append(c)
w('waffle_vegetable_share.csv', ['index','row','col','state','group','share_pct','squares'], cells2)

# ---------- 7. polar coordinates for the custom radial seasonality chart -----
import math
seas = R('seasonality.csv')
R_IN, R_OUT = 42.0, 132.0          # pixel radii
LO, HI = 60.0, 150.0               # index range the radii map to
def radius(v): return R_IN + (max(LO, min(HI, v)) - LO) / (HI - LO) * (R_OUT - R_IN)

polar = []
for series, field, label in [('malaysia', 'malaysia_index', 'Malaysia'),
                             ('world', 'world_index', 'Worldwide')]:
    pts = []
    for r in seas:
        m = int(r['month']); v = float(r[field])
        ang = (m - 1) / 12 * 2 * math.pi            # January at the top, clockwise
        rad = radius(v)
        pts.append({'series': series, 'series_label': label, 'month': m,
                    'month_name': r['month_name'], 'value': v,
                    'x': round(rad * math.sin(ang), 2), 'y': round(rad * math.cos(ang), 2)})
    pts.append({**pts[0], 'month': 13})             # close the loop
    polar += pts
w('seasonality_polar.csv', ['series','series_label','month','month_name','value','x','y'], polar)

rings = []
for v in (75, 100, 125, 150):
    for k in range(73):
        ang = k / 72 * 2 * math.pi
        rings.append({'ring': v, 'k': k,
                      'x': round(radius(v)*math.sin(ang), 2), 'y': round(radius(v)*math.cos(ang), 2)})
w('seasonality_rings.csv', ['ring','k','x','y'], rings)

spokes = []
for r in seas:
    m = int(r['month']); ang = (m-1)/12*2*math.pi
    spokes.append({'month': m, 'month_name': r['month_name'],
                   'x0': 0, 'y0': 0,
                   'x': round(R_OUT*math.sin(ang), 2), 'y': round(R_OUT*math.cos(ang), 2),
                   'lx': round((R_OUT+16)*math.sin(ang), 2), 'ly': round((R_OUT+16)*math.cos(ang), 2),
                   'rainfall_mm': float(r['rainfall_mm'])})
w('seasonality_spokes.csv', ['month','month_name','x0','y0','x','y','lx','ly','rainfall_mm'], spokes)
