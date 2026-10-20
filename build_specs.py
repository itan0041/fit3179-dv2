"""Write one human-readable Vega-Lite v6 spec per idiom into specs/.

Colour semantics are fixed across the whole page, because reusing a colour for a
different attribute between charts was a specific criticism of the previous
assignment:
    green      = growing / land / production
    terracotta = attention (search interest)
    blue       = rainfall / water
"""
import json, os

S = 'specs'
os.makedirs(S, exist_ok=True)
V6 = 'https://vega.github.io/schema/vega-lite/v6.json'

PAPER, INK, INK_SOFT, RULE = '#FAF7F0', '#1C2B22', '#5E6E64', '#DCD5C7'
INK_FAINT = '#8A9890'
GROW   = ['#EDF3E8', '#CFE2C4', '#A6CB98', '#78AE6B', '#4C8D48', '#2D6C35', '#1A4A27']
ATTN   = ['#FBEFE8', '#F2D2BE', '#E6AD8C', '#D88960', '#C2603C', '#9E4528', '#763017']
RAIN   = ['#F0F5F8', '#D2E2EC', '#A9C8DE', '#7CA9CC', '#5089B7', '#2F6A9A', '#1C4B72']
# Farmland lost needs a hue of its own. Terracotta already means search interest on six
# figures, so using it for a decrease gave one colour two meanings - the exact criticism
# made of Data Visualisation 1. Purple is the diverging partner to green in ColorBrewer's
# PRGn scheme, which is designed to stay legible for red-green colour blindness.
LOSS   = ['#F4EEF6', '#E2D3E7', '#C8AED2', '#AC85BA', '#8E5DA2', '#73418A', '#5A2E6E']
ATTN_1, GROW_1, RAIN_1, LOSS_1 = '#C2603C', '#4C8D48', '#2F6A9A', '#73418A'
# Figure 4 sets two growing measures against each other. Terracotta would read as
# search interest there, so the harvest line takes an amber of its own.
HARVEST, HARVEST_DEEP = '#B07D16', '#8A6210'

CROP_COLORS = {
    'Vegetables': '#4C8D48', 'Fruits': '#D98A28', 'Herbs': '#7E9E3A',
    'Spices': '#B5541F', 'Cash crops': '#8C6D3F', 'Paddy (rice)': '#C9A227',
    'Coconut': '#6B8E6E', 'Industrial crops': '#6E6A60', 'Flowers': '#B5567E',
}
CROP_DOMAIN = list(CROP_COLORS); CROP_RANGE = list(CROP_COLORS.values())

W_FULL, W_HALF, W_MAP = 1060, 505, 1060
MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def write(name, spec):
    spec = {'$schema': V6, **spec}
    with open(f'{S}/{name}', 'w') as f:
        json.dump(spec, f, indent=2)
        f.write('\n')
    print(f'  {name:36s} {os.path.getsize(f"{S}/{name}"):6d} B')

def csv(path, parse=None):
    d = {'url': f'data/{path}'}
    if parse: d['format'] = {'type': 'csv', 'parse': parse}
    return d

TOPO = {'url': 'data/malaysia_states.topo.json',
        'format': {'type': 'topojson', 'feature': 'states'}}
PROJ = {'type': 'mercator'}        # Malaysia sits within 8 degrees of the equator,
                                   # where Mercator's area distortion is negligible.
print('writing specs:')

# ───────────────────────── 01 search interest over time ────────────────────
# A plain multi-line chart, on ONE shared 0-100 scale. An earlier ridgeline scaled
# every row to its own peak, which hid a five-fold difference in volume and drew
# the fair criticism that it implied a comparison it did not support. Readers also
# found the double encoding (raw band plus smoothed line) hard to parse. One line
# per term on one axis is honest about relative volume and needs no explaining.
SEARCH_TERMS = ['hidroponik (hydroponics)', 'gardening',
                'berkebun (to garden)', 'kebun sayur (vegetable garden)']
SEARCH_COLORS = ['#B0502E', '#C2603C', '#D08C62', '#E0B18F']

write('01_search_interest.json', {
  'description': 'Multi-line chart: monthly Google Trends search interest in Malaysia for four '
                 'gardening terms, January 2014 to September 2026, all on one 0-100 scale so the '
                 'terms can be compared directly. Lines are a five-month centred average, which '
                 'shows the trend through month-to-month noise.',
  'data': csv('trends_my_monthly.csv', {'date': 'date', 'value': 'number'}),
  'transform': [
    {'window': [{'op': 'mean', 'field': 'value', 'as': 'smooth'}],
     'frame': [-2, 2], 'groupby': ['keyword'], 'sort': [{'field': 'date'}]}],
  'width': 925, 'height': 384,
  # autosize already grows the frame to hold the overflowing end labels, so a
  # right padding on top of it is pure dead space inside the panel.
  'padding': {'left': 5, 'top': 5, 'bottom': 5, 'right': 8},
  'encoding': {
    'x': {'field': 'date', 'type': 'temporal', 'title': None,
          'axis': {'format': '%Y', 'tickCount': 'year', 'grid': False,
                   'domainColor': RULE, 'tickColor': RULE, 'labelColor': INK_SOFT,
                   'labelFontSize': 11.5}},
    'y': {'field': 'smooth', 'type': 'quantitative',
          'title': 'Search interest (100 = busiest month of any term)',
          'scale': {'domain': [0, 75]},
          'axis': {'grid': True, 'gridColor': RULE, 'gridDash': [2, 3], 'domain': False,
                   'ticks': False, 'labelColor': INK_SOFT, 'titleColor': INK_SOFT}},
    'color': {'field': 'keyword_label', 'type': 'nominal', 'legend': None,
              'scale': {'domain': SEARCH_TERMS, 'range': SEARCH_COLORS}}},
  'layer': [
    {'mark': {'type': 'line', 'strokeWidth': 2.6, 'interpolate': 'monotone'},
     'encoding': {
       'opacity': {'condition': {'param': 'hover', 'value': 1, 'empty': True}, 'value': 0.2},
       'tooltip': [
         {'field': 'keyword_label', 'type': 'nominal', 'title': 'Search term'},
         {'field': 'date', 'type': 'temporal', 'title': 'Month', 'format': '%B %Y'},
         {'field': 'value', 'type': 'quantitative', 'title': 'Interest that month'},
         {'field': 'smooth', 'type': 'quantitative', 'title': 'Five-month average', 'format': '.1f'}]}},
    # The hover selection sits on one layer only; at the top level of a layered spec
    # it is instantiated per layer and collides with itself.
    # A zero-size point has no hit area, so pointerover never fires on it. The target
    # is given a real radius, held invisible, and matched by nearest so the reader can
    # hover anywhere near a line rather than landing exactly on a month.
    {'params': [{'name': 'hover', 'select': {'type': 'point', 'fields': ['keyword_label'],
                                             'on': 'pointerover', 'clear': 'pointerout',
                                             'nearest': True}}],
     'mark': {'type': 'point', 'filled': True, 'size': 120, 'opacity': 0},
     # The invisible target sits above the line and absorbs the pointer, so the
     # tooltip must live here too: on the line alone it almost never fires.
     'encoding': {
       'tooltip': [
         {'field': 'keyword_label', 'type': 'nominal', 'title': 'Search term'},
         {'field': 'date', 'type': 'temporal', 'title': 'Month', 'format': '%B %Y'},
         {'field': 'value', 'type': 'quantitative', 'title': 'Interest that month'},
         {'field': 'smooth', 'type': 'quantitative', 'title': 'Five-month average', 'format': '.1f'}]}},
    # berkebun and kebun sayur end within a few index points of each other, so the
    # lower label is nudged clear of the upper one.
    {'transform': [{'filter': 'datum.date >= toDate("2026-09-01")'},
                   {'calculate': "datum.keyword === 'kebun sayur' ? datum.smooth - 4.5 : "
                                 "(datum.keyword === 'berkebun' ? datum.smooth + 2.5 : datum.smooth)",
                    'as': 'label_y'},
                   # The glosses are given in the caption, so the end label carries
                   # the search term alone and the chart keeps the width instead.
                   {'calculate': "split(datum.keyword_label, ' (')[0]", 'as': 'label_short'}],
     'mark': {'type': 'text', 'align': 'left', 'dx': 10, 'fontSize': 12.5, 'fontWeight': 600},
     'encoding': {'y': {'field': 'label_y', 'type': 'quantitative'},
                  'text': {'field': 'label_short', 'type': 'nominal'}}},
    {'data': {'values': [{'date': '2020-03-18'}]},
     'transform': [],
     'mark': {'type': 'rule', 'strokeDash': [5, 4], 'strokeWidth': 1.4, 'opacity': 0.55},
     # y is nulled out: the layer inherits the top-level y field, the inline row has
     # no such field, and the rule silently drew nothing for want of a y value.
     'encoding': {'x': {'field': 'date', 'type': 'temporal'}, 'y': None,
                  'color': {'value': INK}}},
    {'data': {'values': [{'date': '2020-04-15', 'y': 73,
                          'label': 'Movement Control Order, March 2020'}]},
     'transform': [],
     'mark': {'type': 'text', 'align': 'left', 'dx': 6, 'baseline': 'top',
              'fontSize': 11.5, 'fontStyle': 'italic'},
     'encoding': {'x': {'field': 'date', 'type': 'temporal'},
                  'y': {'field': 'y', 'type': 'quantitative'},
                  'text': {'field': 'label', 'type': 'nominal'},
                  'color': {'value': INK_SOFT}}}],
  'config': {'view': {'stroke': None}}})

# ───────────────────────── 02 slope graph ───────────────────────────────────
write('02_category_slope.json', {
  'description': 'Slope graph: planted area of each crop category in 2024 relative to 2014 (2014 = 100).',
  'data': csv('crops_category_malaysia.csv',
              {'year': 'number', 'area_index_2014': 'number', 'prod_index_2014': 'number',
               'label_area': 'number', 'label_prod': 'number'}),
  'params': [{'name': 'measure', 'value': 'Planted area',
              'bind': {'input': 'radio', 'options': ['Planted area', 'Production'],
                       'name': 'Compare by  '}},
             ],
  'transform': [
    {'filter': 'datum.year == 2014 || datum.year == 2024'},
    {'calculate': "measure === 'Planted area' ? datum.area_index_2014 : datum.prod_index_2014",
     'as': 'value'},
    {'calculate': "measure === 'Planted area' ? datum.label_area : datum.label_prod",
     'as': 'label_y'},
    {'filter': 'isValid(datum.value)'}],
  'width': 1006, 'height': 505,
  'padding': {'left': 5, 'top': 5, 'bottom': 5, 'right': 8},
  'encoding': {
    'x': {'field': 'year', 'type': 'quantitative', 'title': None,
          'scale': {'domain': [2013.5, 2026.9], 'nice': False},
          'axis': {'values': [2014, 2024], 'format': 'd', 'labelAngle': 0,
                   'labelFontSize': 13, 'labelColor': INK,
                   'domain': False, 'ticks': False, 'grid': False, 'labelPadding': 8}},
    'y': {'field': 'value', 'type': 'quantitative',
          'title': 'Index (2014 = 100)',
          'scale': {'zero': False},
          'axis': {'grid': True, 'gridColor': RULE, 'gridDash': [2, 3],
                   'domain': False, 'ticks': False, 'labelColor': INK_SOFT, 'titleColor': INK_SOFT}},
    'color': {'field': 'crop_label', 'type': 'nominal', 'legend': None,
              'scale': {'domain': CROP_DOMAIN, 'range': CROP_RANGE}},
    'detail': {'field': 'crop_label', 'type': 'nominal'}},
  'layer': [
    {'mark': {'type': 'line', 'strokeWidth': 2.4},
     'encoding': {'opacity': {'condition': {'param': 'hover', 'value': 1, 'empty': True},
                              'value': 0.18},
                  'strokeWidth': {'condition': {'param': 'hover', 'value': 4, 'empty': False},
                                  'value': 2.4}}},
    # The hover selection lives on this one layer: declared at the top level of a
    # layered spec it is instantiated per layer and collides with itself.
    {'params': [{'name': 'hover', 'select': {'type': 'point', 'fields': ['crop_label'],
                                            'on': 'pointerover', 'clear': 'pointerout',
                                            'nearest': True}}],
     'mark': {'type': 'point', 'filled': True, 'size': 70},
     'encoding': {'tooltip': [
        {'field': 'crop_label', 'type': 'nominal', 'title': 'Category'},
        {'field': 'year', 'type': 'quantitative', 'title': 'Year', 'format': 'd'},
        {'field': 'value', 'type': 'quantitative',
         'title': 'Index (2014 = 100)', 'format': '.1f'}]}},
    {'transform': [{'filter': 'datum.year == 2024'}],
     'mark': {'type': 'text', 'align': 'left', 'dx': 10, 'fontSize': 12, 'fontWeight': 500},
     'encoding': {
       'y': {'field': 'label_y', 'type': 'quantitative'},
       'text': {'field': 'crop_label', 'type': 'nominal'}}}],
  'config': {'view': {'stroke': None}}})

# ───────────────────────── 03 bump chart ────────────────────────────────────
write('03_category_bump.json', {
  'description': 'Bump chart: each crop category ranked 1-9 by how much its planted area '
                 'had grown relative to 2014. Rank 1 = fastest growing that year.',
  'data': csv('crops_category_malaysia.csv', {'year': 'number', 'area_index_2014': 'number'}),
  'transform': [
    {'filter': 'datum.year > 2014'},
    {'window': [{'op': 'rank', 'as': 'growth_rank'}],
     'sort': [{'field': 'area_index_2014', 'order': 'descending'}],
     'groupby': ['year']}],
  'width': 993, 'height': 505,
  'padding': {'left': 5, 'top': 5, 'bottom': 5, 'right': 8},
  'encoding': {
    'x': {'field': 'year', 'type': 'ordinal', 'title': None,
          'axis': {'labelAngle': 0, 'labelColor': INK_SOFT, 'grid': False,
                   'domain': False, 'ticks': False, 'labelFontSize': 11,
                   'values': [2015, 2017, 2019, 2021, 2024]}},
    'y': {'field': 'growth_rank', 'type': 'quantitative',
          'scale': {'domain': [0.5, 9.5], 'reverse': True},
          'title': None,
          'axis': {'values': [1,2,3,4,5,6,7,8,9], 'grid': False, 'domain': False,
                   'ticks': False, 'labelColor': INK_SOFT, 'titleColor': INK_SOFT}},
    'color': {'field': 'crop_label', 'type': 'nominal', 'legend': None,
              'scale': {'domain': CROP_DOMAIN, 'range': CROP_RANGE}},
    'detail': {'field': 'crop_label', 'type': 'nominal'},
    'tooltip': [
      {'field': 'crop_label', 'type': 'nominal', 'title': 'Category'},
      {'field': 'year', 'type': 'ordinal', 'title': 'Year'},
      {'field': 'growth_rank', 'type': 'quantitative', 'title': 'Growth rank'},
      {'field': 'area_index_2014', 'type': 'quantitative', 'title': 'Area (2014 = 100)', 'format': '.1f'}]},
  'layer': [
    {'mark': {'type': 'line', 'strokeWidth': 2.6, 'interpolate': 'monotone'},
     'encoding': {'opacity': {'condition': {'param': 'hover', 'value': 1, 'empty': True},
                              'value': 0.15},
                  'strokeWidth': {'condition': {'param': 'hover', 'value': 4.5, 'empty': False},
                                  'value': 2.6}}},
    # Hovering one category lifts its path; the param sits on a single layer.
    {'params': [{'name': 'hover', 'select': {'type': 'point', 'fields': ['crop_label'],
                                            'on': 'pointerover', 'clear': 'pointerout',
                                            'nearest': True}}],
     'mark': {'type': 'point', 'filled': True, 'size': 60},
     'encoding': {'opacity': {'condition': {'param': 'hover', 'value': 1, 'empty': True},
                              'value': 0.15}}},
    {'transform': [{'filter': 'datum.year == 2024'}],
     'mark': {'type': 'text', 'align': 'left', 'dx': 10, 'fontSize': 11.5, 'fontWeight': 500},
     'encoding': {'text': {'field': 'crop_label', 'type': 'nominal'}}}],
  'config': {'view': {'stroke': None}}})

# ───────────────────────── 04 land against output ──────────────────────────
# Was a connected scatterplot. The loop shape read as a puzzle to non-technical
# readers and, worse, it buried the actual finding: planted area has recovered past
# its 2014 level while production has not. Two indexed lines with the gap between
# them tinted show that in one glance.
write('04_land_vs_output.json', {
  'description': 'Two lines: Malaysia\u2019s vegetable planted area and vegetable production, '
                 'each indexed so its 2014 value equals 100, so the two can be compared on one '
                 'scale. The tinted band is the gap between them \u2014 output per hectare.',
  'data': csv('crops_category_malaysia.csv',
              {'year': 'number', 'area_index_2014': 'number', 'prod_index_2014': 'number',
               'planted_area_ha': 'number', 'production_tonnes': 'number'}),
  'transform': [{'filter': "datum.crop_type == 'vegetables'"}],
  'width': 886, 'height': 404,
  'padding': {'left': 5, 'top': 5, 'bottom': 5, 'right': 8},
  'encoding': {
    'x': {'field': 'year', 'type': 'quantitative', 'title': None,
          'scale': {'domain': [2014, 2024], 'nice': False},
          'axis': {'format': 'd', 'tickCount': 11, 'grid': False, 'domain': False,
                   'ticks': False, 'labelColor': INK_SOFT, 'labelFontSize': 11.5}}},
  'layer': [
    # the gap between land and output, as a tinted band
    {'mark': {'type': 'area', 'color': GROW[2], 'opacity': 0.35, 'interpolate': 'monotone'},
     'encoding': {
       'y': {'field': 'area_index_2014', 'type': 'quantitative',
             'title': 'Index (2014 = 100)', 'scale': {'domain': [66, 110]},
             'axis': {'grid': True, 'gridColor': RULE, 'gridDash': [2, 3], 'domain': False,
                      'ticks': False, 'labelColor': INK_SOFT, 'titleColor': INK_SOFT}},
       'y2': {'field': 'prod_index_2014'}}},
    # One horizontal reference line at the 2014 = 100 level. It has to blank the
    # inherited x encoding and be filtered to a single row: without both, the layer
    # takes the top-level x field and draws a VERTICAL rule at every year, each one
    # running from the top of the plot down to 100.
    {'transform': [{'filter': 'datum.year == 2014'}],
     'mark': {'type': 'rule', 'color': INK_SOFT, 'strokeDash': [3, 3], 'opacity': 0.5},
     'encoding': {'x': None, 'y': {'datum': 100}}},
    {'mark': {'type': 'line', 'strokeWidth': 2.8, 'color': GROW[6], 'interpolate': 'monotone',
              'point': {'filled': True, 'size': 55, 'color': GROW[6]}},
     'encoding': {
       'y': {'field': 'area_index_2014', 'type': 'quantitative'},
       'tooltip': [
         {'field': 'year', 'type': 'quantitative', 'title': 'Year', 'format': 'd'},
         {'field': 'planted_area_ha', 'type': 'quantitative', 'title': 'Planted area (hectares)', 'format': ',.0f'},
         {'field': 'area_index_2014', 'type': 'quantitative', 'title': 'Area index (2014 = 100)', 'format': '.1f'}]}},
    {'mark': {'type': 'line', 'strokeWidth': 2.8, 'color': HARVEST, 'interpolate': 'monotone',
              'point': {'filled': True, 'size': 55, 'color': HARVEST}},
     'encoding': {
       'y': {'field': 'prod_index_2014', 'type': 'quantitative'},
       'tooltip': [
         {'field': 'year', 'type': 'quantitative', 'title': 'Year', 'format': 'd'},
         {'field': 'production_tonnes', 'type': 'quantitative', 'title': 'Production (tonnes)', 'format': ',.0f'},
         {'field': 'prod_index_2014', 'type': 'quantitative', 'title': 'Production index (2014 = 100)', 'format': '.1f'}]}},
    {'transform': [{'filter': 'datum.year == 2024'}],
     'mark': {'type': 'text', 'align': 'left', 'dx': 12, 'fontSize': 12.5, 'fontWeight': 600,
              'color': GROW[6]},
     'encoding': {'y': {'field': 'area_index_2014', 'type': 'quantitative'},
                  'text': {'value': 'Land planted'}}},
    {'transform': [{'filter': 'datum.year == 2024'}],
     'mark': {'type': 'text', 'align': 'left', 'dx': 12, 'fontSize': 12.5, 'fontWeight': 600,
              'color': HARVEST_DEEP},
     'encoding': {'y': {'field': 'prod_index_2014', 'type': 'quantitative'},
                  'text': {'value': 'Tonnes harvested'}}},
    {'transform': [{'filter': 'datum.year == 2024'}],
     'mark': {'type': 'text', 'align': 'left', 'dx': 12, 'dy': 16, 'fontSize': 11.5,
              'fontStyle': 'italic', 'color': INK_SOFT},
     'encoding': {'y': {'field': 'prod_index_2014', 'type': 'quantitative'},
                  'text': {'value': 'still below 2014'}}}],
  'config': {'view': {'stroke': None}}})

# ═══════════════════════ MAPS ═══════════════════════════════════════════════
# Malaysia straddles the South China Sea, so a single fitted frame wastes roughly
# half its canvas on open water and shrinks the peninsular states past legibility.
# Every map below is therefore drawn as two separately fitted panels - Peninsular
# Malaysia and Malaysian Borneo - sharing one colour and size scale.

PEN = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 16]
BOR = [12, 13, 15]

# Both panels are pinned to the SAME Mercator scale rather than being auto-fitted
# independently, so a hectare in Sarawak covers the same number of pixels as a
# hectare in Perak and the two panels remain visually comparable.
# Enlarged by 1.09 over the first draft so the two panels fill the 1072px that a
# full-width figure actually offers. Scale, panel widths and height move together,
# so a hectare still covers the same pixels in both panels.
MAP_SCALE = 3777
PEN_W, BOR_W = 357, 669
MAP_H = 465
SPIKE_H = 562

# The translate is written out in pixels rather than left to Vega's width/2 signal:
# inside an hconcat that signal resolves against the wrong view and clips the map.
def pen_proj(h=MAP_H, ty=None):
    return {'type': 'mercator', 'scale': MAP_SCALE, 'center': [102.1, 3.95],
            'translate': [PEN_W / 2, h / 2 if ty is None else ty]}

def bor_proj(h=MAP_H, ty=None):
    return {'type': 'mercator', 'scale': MAP_SCALE, 'center': [114.4, 4.12],
            'translate': [BOR_W / 2, h / 2 if ty is None else ty]}

PEN_PROJ, BOR_PROJ = pen_proj(), bor_proj()

def region_filter(field, codes):
    return {'filter': f'indexof({codes}, datum.{field}) >= 0'}

def shared():
    return {'resolve': {'scale': {'color': 'shared', 'size': 'shared'}},
            'spacing': 26,
            'config': {'view': {'stroke': None}}}

SUM_DATA = csv('state_summary.csv',
               {'year': 'number', 'veg_area_ha_per_1000': 'number', 'code': 'number',
                'veg_area_ha': 'number', 'population': 'number', 'veg_prod_tonnes': 'number',
                'veg_kg_per_person': 'number'})

# Charts with state names down the y axis indent their plotting area by the width of
# those labels, and a bottom legend starts at that indent rather than at the panel edge.
# Measured in a browser, that put legends on three different vertical lines down the
# page - the sight-line fault Data Visualisation 1 was marked down for. These four pull
# their legend back to the panel edge, so every legend on the page starts on the same
# line as the figure's caption above it. The offsets are the measured axis widths.
def left_legend(dx, y, **kw):
    return {'orient': 'none', 'legendX': -dx, 'legendY': y, 'direction': 'horizontal',
            'titleAnchor': 'start', 'titleColor': INK, 'labelColor': INK_SOFT,
            'titleFontSize': 11.5, **kw}

BOTTOM_LEGEND = {'orient': 'bottom', 'direction': 'horizontal', 'titleLimit': 1000,
                 'labelLimit': 220, 'titleColor': INK, 'labelColor': INK_SOFT,
                 'titleFontSize': 11.5, 'titleAnchor': 'start'}

# Annotations drawn ON the figures. Data Visualisation 1 was marked down for carrying
# too few of these ("can add more informative annotations in diagrams"), and the waffle
# chart was named specifically, so every figure that can carry a label now does.
NOTE = {'type': 'text', 'fontSize': 11, 'fontWeight': 600, 'lineBreak': '|'}

# The federal territories are published as "W.P. Kuala Lumpur" and the like. W.P. is
# Wilayah Persekutuan, and an unexpanded short form in the visualisation is the exact
# thing Data Visualisation 1 was marked down for. Each is shown by its plain name,
# which is unambiguous to a Malaysian reader, on axes and in tooltips alike.
STATE_LABEL = "replace(datum.label, 'W.P. ', '')"
DROP_WP = {'calculate': "replace(datum.state, 'W.P. ', '')", 'as': 'state_name'}

def note_layer(values, color=INK, **mark):
    """A free-standing text layer. It carries its own data and an empty transform so
    that nothing is inherited from the enclosing spec - a layer with inline data still
    picks up the parent's encoding and transform, and silently renders nothing when a
    field it is handed does not exist in its own rows."""
    return {'data': {'values': values}, 'transform': [],
            'mark': {**NOTE, 'color': color, **mark},
            'encoding': {'longitude': {'field': 'lon', 'type': 'quantitative'},
                         'latitude': {'field': 'lat', 'type': 'quantitative'},
                         'text': {'field': 'label', 'type': 'nominal'}}}

# ───────────────────────── 05 choropleth map ────────────────────────────────
# The two states the section's prose names are labelled on the map itself, so the
# comparison can be made without going to the tooltip or back to the paragraph.
CHORO_NOTES_PEN = [note_layer(
    [{'lon': 102.5416, 'lat': 3.7335, 'label': 'Pahang|16.5'}],
    color='#FAF7F0', fontSize=11.5),
  note_layer(
    [{'lon': 100.95, 'lat': 2.92, 'label': 'Selangor 0.31'}],
    color=INK_SOFT, align='right')]

def choropleth_panel(codes, width, title, legend, proj, notes=()):
    notes = list(notes)
    return {
      'width': width, 'height': MAP_H, 'title': {'text': title, 'fontSize': 13, 'dy': -6},
      'projection': proj,
      'layer': [
        {'data': TOPO,
         'transform': [
           {'lookup': 'properties.code',
            'from': {'data': SUM_DATA, 'key': 'code',
                     'fields': ['state', 'year', 'veg_area_ha', 'veg_area_ha_per_1000', 'population']}},
           {'filter': 'datum.year == 2024'},
           region_filter('properties.code', codes)],
         'mark': {'type': 'geoshape', 'stroke': PAPER, 'strokeWidth': 1.1},
         'encoding': {
           'color': {'field': 'veg_area_ha_per_1000', 'type': 'quantitative',
                     'title': 'Hectares of vegetable land per 1,000 residents',
                     'scale': {'type': 'threshold', 'domain': [0.5, 2, 5, 10], 'range': GROW[1:6]},
                     'legend': {**BOTTOM_LEGEND, 'symbolType': 'square', 'symbolSize': 170} if legend else None},
           'tooltip': [
             {'field': 'state', 'type': 'nominal', 'title': 'State'},
             {'field': 'veg_area_ha', 'type': 'quantitative', 'title': 'Vegetable land (hectares)', 'format': ',.0f'},
             {'field': 'population', 'type': 'quantitative', 'title': 'Population', 'format': ',.0f'},
             {'field': 'veg_area_ha_per_1000', 'type': 'quantitative',
              'title': 'Hectares per 1,000 people', 'format': '.2f'}]}}] + notes}

write('05_map_choropleth.json', {
  'description': 'Choropleth map: hectares of vegetable land per 1,000 residents by state, 2024. '
                 'Drawn as two separately fitted panels so the peninsular states stay legible.',
  'hconcat': [choropleth_panel(PEN, PEN_W, 'Peninsular Malaysia', True, PEN_PROJ, CHORO_NOTES_PEN),
              choropleth_panel(BOR, BOR_W, 'Sabah, Sarawak and Labuan', False, BOR_PROJ)],
  **shared()})

# ───────────────────────── 06 proportional symbol map ───────────────────────
# Each label is centred on its state's longitude and sits just clear of the circle
# drawn there, so it reads as belonging to that circle rather than to a neighbour.
SYMB_NOTES_PEN = [note_layer(
    [{'lon': 102.5416, 'lat': 3.20, 'label': 'Pahang|599,700 tonnes'},
     {'lon': 103.3854, 'lat': 1.52, 'label': 'Johor|243,400 tonnes'}],
    color=INK, fontSize=11, baseline='top')]

def symbol_panel(codes, width, title, legend, proj, notes=()):
    notes = list(notes)
    return {
      'width': width, 'height': MAP_H, 'title': {'text': title, 'fontSize': 13, 'dy': -6},
      'projection': proj,
      'layer': [
        {'data': TOPO,
         'transform': [region_filter('properties.code', codes)],
         'mark': {'type': 'geoshape', 'fill': '#EAE6DC', 'stroke': PAPER, 'strokeWidth': 1.1}},
        {'data': csv('state_centroids.csv', {'lon': 'number', 'lat': 'number', 'code': 'number'}),
         'transform': [
           {'lookup': 'code', 'from': {'data': SUM_DATA, 'key': 'code',
                                       'fields': ['year', 'veg_prod_tonnes', 'veg_kg_per_person']}},
           {'filter': 'datum.year == 2024'},
           {'filter': 'datum.veg_prod_tonnes > 0'},
           region_filter('code', codes)],
         'mark': {'type': 'circle', 'opacity': 0.84, 'stroke': '#1A4A27', 'strokeWidth': 1.1,
                  'color': GROW[4]},
         'encoding': {
           'longitude': {'field': 'lon', 'type': 'quantitative'},
           'latitude': {'field': 'lat', 'type': 'quantitative'},
           'size': {'field': 'veg_prod_tonnes', 'type': 'quantitative',
                    'title': 'Vegetable production in 2024 (tonnes)',
                    # The size channel is the mark's AREA in square pixels, so area is
                    # proportional to tonnes only when the scale is linear and anchored
                    # at zero. A sqrt scale here made area proportional to the square
                    # root of tonnes: Pahang grows 2.5 times Johor's crop but its circle
                    # covered only 1.6 times the area, which is not what the figure note
                    # claims and not what a proportional symbol map means. The floor of
                    # 8 square pixels is 0.3 per cent of the largest circle, so it keeps
                    # Perlis and Labuan visible without disturbing the proportion.
                    'scale': {'type': 'linear', 'domainMin': 0, 'range': [8, 3000]},
                    'legend': {**BOTTOM_LEGEND, 'format': ',.0f',
                               'values': [50000, 200000, 400000, 600000],
                               'symbolFillColor': GROW[4],
                               'symbolStrokeColor': '#1A4A27'} if legend else None},
           'tooltip': [
             {'field': 'state', 'type': 'nominal', 'title': 'State'},
             {'field': 'veg_prod_tonnes', 'type': 'quantitative', 'title': 'Production (tonnes)', 'format': ',.0f'},
             {'field': 'veg_kg_per_person', 'type': 'quantitative', 'title': 'Kilograms per resident', 'format': ',.1f'}]}}] + notes}

write('06_map_symbol.json', {
  'description': 'Proportional symbol map: vegetable production in tonnes by state, 2024. '
                 'Circle area is proportional to tonnage.',
  'hconcat': [symbol_panel(PEN, PEN_W, 'Peninsular Malaysia', True, PEN_PROJ, SYMB_NOTES_PEN),
              symbol_panel(BOR, BOR_W, 'Sabah, Sarawak and Labuan', False, BOR_PROJ)],
  **shared()})

# ───────────────────────── 07 bivariate choropleth ──────────────────────────
# The three corners of the key, named where they actually fall on the map. Without
# these the reader has to hold the nine-square key in memory while scanning.
BIV_NOTES_PEN = [note_layer(
    [{'lon': 100.05, 'lat': 6.48, 'label': 'Perlis and Kedah|search hard, grow little'}],
    color='#8A4A22', fontSize=10.5, align='left'),
  note_layer(
    [{'lon': 102.60, 'lat': 3.62, 'label': 'Pahang|grows most'}],
    color='#FAF7F0', fontSize=10.5),
  note_layer(
    [{'lon': 101.18, 'lat': 2.86, 'label': 'Selangor|low on both'}],
    color=INK_SOFT, fontSize=10.5, align='right')]

def bivariate_panel(codes, width, title, proj, notes=()):
    notes = list(notes)
    return {
      'width': width, 'height': MAP_H, 'title': {'text': title, 'fontSize': 13, 'dy': -6},
      'projection': proj,
      'layer': [
        {'data': TOPO,
         'transform': [
           {'lookup': 'properties.code',
            'from': {'data': csv('bivariate_state.csv',
                                 {'code': 'number', 'interest': 'number', 'grow_per_1000': 'number'}),
                     'key': 'code',
                     'fields': ['state', 'interest', 'grow_per_1000', 'bi_class', 'bi_color']}},
           region_filter('properties.code', codes)],
         'mark': {'type': 'geoshape', 'stroke': PAPER, 'strokeWidth': 1.1},
         'encoding': {
           'color': {'field': 'bi_color', 'type': 'nominal', 'scale': None, 'legend': None},
           'tooltip': [
             {'field': 'state', 'type': 'nominal', 'title': 'State'},
             {'field': 'interest', 'type': 'quantitative', 'title': 'Search interest (0-100)'},
             {'field': 'grow_per_1000', 'type': 'quantitative',
              'title': 'Hectares per 1,000 people', 'format': '.2f'}]}}] + notes}

write('07_map_bivariate.json', {
  'description': 'Bivariate choropleth map: search interest in gardening against vegetable land '
                 'per 1,000 residents. Each state takes a colour from a three-by-three key; the '
                 'colours are pre-computed in the bi_color column.',
  'hconcat': [bivariate_panel(PEN, PEN_W, 'Peninsular Malaysia', PEN_PROJ, BIV_NOTES_PEN),
              bivariate_panel(BOR, BOR_W, 'Sabah, Sarawak and Labuan', BOR_PROJ)],
  **shared()})

write('07b_bivariate_legend.json', {
  'description': 'Three-by-three colour key for the bivariate choropleth map.',
  'data': csv('bivariate_legend.csv', {'interest_class': 'number', 'grow_class': 'number'}),
  'width': 112, 'height': 112,
  'mark': {'type': 'rect', 'stroke': PAPER, 'strokeWidth': 1.5},
  'encoding': {
    'x': {'field': 'interest_class', 'type': 'ordinal',
          'title': 'Searches \u2192',
          'axis': {'labels': False, 'ticks': False, 'domain': False,
                   'titleFontSize': 10.5, 'titleColor': INK_SOFT, 'titlePadding': 6}},
    'y': {'field': 'grow_class', 'type': 'ordinal', 'sort': 'descending',
          'title': 'Vegetable land \u2192',
          'axis': {'labels': False, 'ticks': False, 'domain': False,
                   'titleFontSize': 10.5, 'titleColor': INK_SOFT, 'titlePadding': 6}},
    'color': {'field': 'bi_color', 'type': 'nominal', 'scale': None, 'legend': None}},
  'config': {'view': {'stroke': None}}})

# ───────────────────────── 08 spike map ─────────────────────────────────────
CHG_DATA = csv('state_change.csv',
               {'lon': 'number', 'lat': 'number', 'lat_end': 'number',
                'pct_change': 'number', 'code': 'number',
                'area_2014': 'number', 'area_2024': 'number'})

def spike_panel(codes, width, title, legend, proj):
    return {
      'width': width, 'height': SPIKE_H, 'title': {'text': title, 'fontSize': 13, 'dy': -6},
      'projection': proj,
      'layer': [
        {'data': TOPO,
         'transform': [region_filter('properties.code', codes)],
         'mark': {'type': 'geoshape', 'fill': '#EAE6DC', 'stroke': PAPER, 'strokeWidth': 1}},
        {'data': CHG_DATA,
         'transform': [region_filter('code', codes)],
         'mark': {'type': 'rule', 'strokeWidth': 3, 'opacity': 0.92, 'strokeCap': 'round'},
         'encoding': {
           'longitude': {'field': 'lon', 'type': 'quantitative'},
           'latitude': {'field': 'lat', 'type': 'quantitative'},
           'longitude2': {'field': 'lon'},
           'latitude2': {'field': 'lat_end'},
           'color': {'field': 'direction', 'type': 'nominal',
                     'title': 'Change in vegetable land, 2014 to 2024',
                     'scale': {'domain': ['Increase', 'Decrease'], 'range': [GROW[5], LOSS[5]]},
                     'legend': BOTTOM_LEGEND if legend else None},
           'tooltip': [
             {'field': 'state', 'type': 'nominal', 'title': 'State'},
             {'field': 'area_2014', 'type': 'quantitative', 'title': 'Vegetable land 2014 (hectares)', 'format': ',.0f'},
             {'field': 'area_2024', 'type': 'quantitative', 'title': 'Vegetable land 2024 (hectares)', 'format': ',.0f'},
             {'field': 'pct_change', 'type': 'quantitative', 'title': 'Change (per cent)', 'format': '+.1f'}]}},
        {'data': CHG_DATA,
         'transform': [region_filter('code', codes)],
         'mark': {'type': 'circle', 'size': 22, 'color': INK, 'opacity': 0.6},
         'encoding': {'longitude': {'field': 'lon', 'type': 'quantitative'},
                      'latitude': {'field': 'lat', 'type': 'quantitative'}}},
        {'data': CHG_DATA,
         'transform': [region_filter('code', codes),
                       {'filter': 'abs(datum.pct_change) >= 25'}],
         'mark': {'type': 'text', 'fontSize': 10.5, 'fontWeight': 600, 'align': 'center'},
         'encoding': {'longitude': {'field': 'lon', 'type': 'quantitative'},
                      'latitude': {'field': 'label_lat', 'type': 'quantitative'},
                      'text': {'field': 'pct_change', 'type': 'quantitative', 'format': '+.0f'},
                      'color': {'condition': {'test': "datum.direction === 'Increase'",
                                              'value': GROW[6]},
                                'value': LOSS[6]}}}]}

write('08_map_spike.json', {
  'description': 'Spike map: change in vegetable planted area between 2014 and 2024. Spike '
                 'length is proportional to the percentage change, rising for an increase and '
                 'falling for a decrease. Changes of 25 per cent or more are labelled.',
  'hconcat': [spike_panel(PEN, PEN_W, 'Peninsular Malaysia', True, pen_proj(SPIKE_H, 356)),
              spike_panel(BOR, BOR_W, 'Sabah, Sarawak and Labuan', False, bor_proj(SPIKE_H, 356))],
  **shared()})

# ───────────────────────── 09 dumbbell ──────────────────────────────────────
write('09_state_dumbbell.json', {
  'description': 'Dumbbell chart: vegetable planted area by state in 2014 and 2024, '
                 'with a connecting line showing the direction of travel.',
  'data': csv('state_change.csv',
              {'area_2014': 'number', 'area_2024': 'number', 'pct_change': 'number'}),
  'width': 384, 'height': 594,
  # The percentage change is printed at the end of every row. It was previously
  # reachable only by hovering, which leaves the chart silent in a screenshot and
  # on any device without a mouse.
  'transform': [
    DROP_WP,
    {'calculate': 'max(datum.area_2014, datum.area_2024)', 'as': 'row_end'},
    {'calculate': "format(datum.pct_change, '+.0f') + ' per cent'", 'as': 'chg_label'}],
  'encoding': {
    'y': {'field': 'state_name', 'type': 'nominal', 'title': None,
          'sort': {'field': 'area_2024', 'order': 'descending'},
          'axis': {'domain': False, 'ticks': False, 'labelFontSize': 11.5,
                   'labelColor': INK, 'grid': True, 'gridColor': RULE, 'gridDash': [1, 4]}},
    'x': {'field': 'area_2014', 'type': 'quantitative',
          'title': 'Vegetable planted area (hectares)',
          # Headroom on the right so the change labels are not clipped at the view edge.
          'scale': {'type': 'sqrt', 'domain': [0, 36000], 'nice': False},
          'axis': {'grid': False, 'domain': False, 'ticks': False, 'format': ',.0f',
                   'labelColor': INK_SOFT, 'titleColor': INK_SOFT,
                   'values': [0, 2000, 5000, 10000, 20000, 30000]}}},
  'layer': [
    {'mark': {'type': 'rule', 'strokeWidth': 2.2, 'opacity': 0.55},
     'encoding': {'x2': {'field': 'area_2024'},
                  'color': {'field': 'direction', 'type': 'nominal',
                            'scale': {'domain': ['Increase', 'Decrease'], 'range': [GROW[5], LOSS[5]]}}}},
    {'mark': {'type': 'point', 'filled': True, 'size': 95, 'color': '#B9BEB3',
              'stroke': PAPER, 'strokeWidth': 1.5},
     'encoding': {'tooltip': [
        {'field': 'state_name', 'type': 'nominal', 'title': 'State'},
        {'field': 'area_2014', 'type': 'quantitative', 'title': '2014 (hectares)', 'format': ',.0f'}]}},
    {'mark': {'type': 'point', 'filled': True, 'size': 130, 'stroke': PAPER, 'strokeWidth': 1.5},
     'encoding': {
       'x': {'field': 'area_2024', 'type': 'quantitative'},
       'color': {'field': 'direction', 'type': 'nominal',
                 'title': 'Pale dot = 2014, coloured dot = 2024',
                 'scale': {'domain': ['Increase', 'Decrease'], 'range': [GROW[5], LOSS[5]]},
                 'legend': left_legend(95, 622, titleLimit=400, titleColor=INK_SOFT)},
       'tooltip': [
         {'field': 'state_name', 'type': 'nominal', 'title': 'State'},
         {'field': 'area_2024', 'type': 'quantitative', 'title': '2024 (hectares)', 'format': ',.0f'},
         {'field': 'pct_change', 'type': 'quantitative', 'title': 'Change (per cent)', 'format': '+.1f'}]}},
    {'mark': {'type': 'text', 'align': 'left', 'dx': 10, 'fontSize': 10.5, 'fontWeight': 600},
     'encoding': {
       'x': {'field': 'row_end', 'type': 'quantitative'},
       'text': {'field': 'chg_label', 'type': 'nominal'},
       'color': {'field': 'direction', 'type': 'nominal', 'legend': None}}}],
  'config': {'view': {'stroke': None}}})

# ───────────────────────── 10 waffle ────────────────────────────────────────
WAFFLE_DOMAIN = ['Pahang', 'Johor', 'Kelantan', 'Sarawak', 'Perak', 'Sabah', 'Other states']
WAFFLE_RANGE  = ['#17401F', '#38763E', '#6BA45F', '#9CC78B', '#C6DEB8', '#E4EFDA', '#D6CEBC']
write('10_waffle_share.json', {
  'description': 'Waffle chart: each of the 100 squares is one per cent of Malaysia’s '
                 'vegetable planted area in 2024.',
  'data': csv('waffle_vegetable_share.csv',
              {'row': 'number', 'col': 'number', 'share_pct': 'number', 'squares': 'number'}),
  # The key runs along the bottom rather than down the right. On the right it was
  # seven rows tall against a ten-row grid, so the column's lower third was empty
  # and the grid had to shrink to make room for it. Underneath, the grid gets the
  # full width of its column back.
  'width': 482, 'height': 482,
  'layer': [
    {'mark': {'type': 'square', 'size': 1330, 'stroke': PAPER, 'strokeWidth': 3.4, 'cornerRadius': 2},
     'encoding': {
       'x': {'field': 'col', 'type': 'ordinal', 'axis': None},
       'y': {'field': 'row', 'type': 'ordinal', 'axis': None},
       'color': {'field': 'group', 'type': 'nominal', 'title': 'State',
                 'scale': {'domain': WAFFLE_DOMAIN, 'range': WAFFLE_RANGE},
                 'legend': {'orient': 'bottom', 'direction': 'horizontal', 'columns': 4,
                            'titleColor': INK, 'labelColor': INK_SOFT, 'titleOrient': 'top',
                            'symbolType': 'square', 'symbolSize': 150, 'labelFontSize': 11.5,
                            'columnPadding': 14, 'rowPadding': 5, 'offset': 10}},
       'tooltip': [
         {'field': 'state', 'type': 'nominal', 'title': 'State'},
         {'field': 'share_pct', 'type': 'quantitative', 'title': 'Share of national area (per cent)', 'format': '.1f'},
         {'field': 'squares', 'type': 'quantitative', 'title': 'Squares on this chart'}]}},
    # The marker of Data Visualisation 1 asked for an annotation on the waffle chart
    # by name. The two blocks worth naming are the largest and the residual.
    # White lettering was being cut to pieces by the paper-coloured gaps between the
    # squares. The four squares the label crosses are filled in behind it, so it runs
    # over one solid block of Pahang's own colour.
    {'data': {'values': [{'col': 0, 'row': 1}, {'col': 1, 'row': 1},
                         {'col': 2, 'row': 1}, {'col': 3, 'row': 1}]},
     'transform': [],
     'mark': {'type': 'rect', 'fill': WAFFLE_RANGE[0], 'stroke': None, 'cornerRadius': 2},
     'encoding': {'x': {'field': 'col', 'type': 'ordinal'},
                  'y': {'field': 'row', 'type': 'ordinal'}}},
    {'data': {'values': [{'col': 0, 'row': 1, 'label': 'Pahang: 36 squares'}]},
     'transform': [],
     'mark': {'type': 'text', 'align': 'left', 'dx': -18, 'fontSize': 13.5,
              'fontWeight': 700, 'color': '#FAF7F0'},
     'encoding': {'x': {'field': 'col', 'type': 'ordinal'},
                  'y': {'field': 'row', 'type': 'ordinal'},
                  'text': {'field': 'label', 'type': 'nominal'}}},
    {'data': {'values': [{'col': 0, 'row': 9, 'label': 'Every other state combined: 12'}]},
     'transform': [],
     'mark': {'type': 'text', 'align': 'left', 'dx': 0, 'fontSize': 11.5,
              'fontWeight': 600, 'color': INK},
     'encoding': {'x': {'field': 'col', 'type': 'ordinal'},
                  'y': {'field': 'row', 'type': 'ordinal'},
                  'text': {'field': 'label', 'type': 'nominal'}}}],
  'config': {'view': {'stroke': None}}})

# ───────────────────────── 11 rainfall heatmap ──────────────────────────────
# The row order is written out as a list rather than left to an aggregate sort.
# Inside a layered spec that sort has to resolve against every layer's data, and it
# silently falls back to alphabetical when one of them cannot supply the field - which
# is exactly what happened when the annotation layers were added.
def _rain_order():
    import csv as _csv, collections
    total = collections.defaultdict(float)
    with open('data/climate_states.csv', newline='', encoding='utf-8') as f:
        for row in _csv.DictReader(f):
            total[row['state']] += float(row['rain_mm_month'])
    return [st for st, _ in sorted(total.items(), key=lambda kv: -kv[1])]

RAIN_ORDER = _rain_order()
write('11_rain_heatmap.json', {
  'description': 'Heatmap: average monthly rainfall by state, from a 25-year NASA POWER climatology.',
  'data': csv('climate_states.csv', {'month': 'number', 'rain_mm_month': 'number'}),
  'transform': [DROP_WP],
  'width': 950, 'height': 450,
  'encoding': {
    'x': {'field': 'month_name', 'type': 'ordinal', 'title': None,
          'sort': MONTHS,
          'axis': {'labelAngle': 0, 'domain': False, 'ticks': False, 'orient': 'top',
                   'labelFontSize': 12, 'labelColor': INK, 'labelPadding': 6}},
    'y': {'field': 'state_name', 'type': 'nominal', 'title': None,
          'sort': [st.replace('W.P. ', '') for st in RAIN_ORDER],
          'axis': {'domain': False, 'ticks': False, 'labelFontSize': 11.5, 'labelColor': INK}},
    'color': {'field': 'rain_mm_month', 'type': 'quantitative',
              'title': 'Average rainfall (millimetres per month)',
              # Four breaks, not six: Vega-Lite discards gradientLength on a threshold
              # scale and draws a fixed banded key, so six labels landed a pixel apart.
              # The breaks are the quintiles of the 192 state-months, rounded, so the
              # five bands hold 19 / 22 / 18 / 21 / 19 per cent of the cells. The earlier
              # round numbers put 38 per cent of the chart in a single shade, which
              # flattened the very contrast the chart exists to show. The ramp is five
              # consecutive steps; it previously skipped one, so the step from the fourth
              # band to the fifth read as twice the size of the others. The palest step
              # of the scale is unused because it sits within a shade of the paper.
              'scale': {'type': 'threshold', 'domain': [155, 185, 215, 270],
                        'range': [RAIN[2], RAIN[3], RAIN[4], RAIN[5], RAIN[6]]},
              'legend': left_legend(95, 476, labelFontSize=11.5, labelOverlap=False,
                                    labelPadding=6, titlePadding=8)},
    'tooltip': [
      {'field': 'state_name', 'type': 'nominal', 'title': 'State'},
      {'field': 'city', 'type': 'nominal', 'title': 'Measured at'},
      {'field': 'month_name', 'type': 'nominal', 'title': 'Month'},
      {'field': 'rain_mm_month', 'type': 'quantitative', 'title': 'Rainfall (millimetres)', 'format': ',.0f'},
      {'field': 'tmax_c', 'type': 'quantitative', 'title': 'Average daily maximum (°C)', 'format': '.1f'}]},
  # Both annotations are drawn from the chart's own rows, filtered to a single cell, so
  # every field the shared scales sort on is still present on the annotation layer.
  'layer': [
    {'mark': {'type': 'rect', 'stroke': PAPER, 'strokeWidth': 1.5, 'cornerRadius': 1}},
    # A row is 28 pixels tall, so these sit at 9 point on a 10 point line: two larger
    # lines overran the cell and were clipped by the row below.
    # A two-line note anchors on its first line, so without the upward dy the pair
    # hangs below the cell's middle and the second line sits on the row boundary.
    {'transform': [{'filter': "datum.month == 11 && datum.state == 'Terengganu'"}],
     'mark': {'type': 'text', 'fontSize': 9, 'fontWeight': 700, 'baseline': 'middle',
              'lineBreak': '|', 'lineHeight': 10, 'dy': -5},
     'encoding': {'text': {'value': 'North-east|monsoon'}, 'color': {'value': '#FAF7F0'}}},
    {'transform': [{'filter': "datum.month == 2 && datum.state == 'Perlis'"}],
     'mark': {'type': 'text', 'fontSize': 9, 'fontWeight': 700, 'baseline': 'middle',
              'lineBreak': '|', 'lineHeight': 10, 'dy': -5},
     'encoding': {'text': {'value': 'Driest cell|on the chart'}, 'color': {'value': INK}}}],
  'config': {'view': {'stroke': None}}})

# ───────────────────────── 12 custom radial ─────────────────────────────────
AX = {'scale': {'domain': [-168, 168]}, 'axis': None}
write('12_seasonality_radial.json', {
  'description': 'Custom-built radial chart. Polar coordinates are pre-computed in Python '
                 '(data/seasonality_polar.csv) because Vega-Lite has no polar line mark. '
                 'January is at the top and the months run clockwise. Each series is scaled '
                 'so its own yearly average sits at the 100 ring.',
  'width': 478, 'height': 478,
  'layer': [
    {'data': csv('seasonality_rings.csv', {'x': 'number', 'y': 'number', 'ring': 'number', 'k': 'number'}),
     'mark': {'type': 'line', 'strokeWidth': 0.8, 'color': RULE},
     'encoding': {'x': {'field': 'x', 'type': 'quantitative', **AX},
                  'y': {'field': 'y', 'type': 'quantitative', **AX},
                  'detail': {'field': 'ring', 'type': 'nominal'},
                  'order': {'field': 'k', 'type': 'quantitative'}}},
    {'data': csv('seasonality_spokes.csv', {'x': 'number', 'y': 'number', 'x0': 'number', 'y0': 'number'}),
     'mark': {'type': 'rule', 'strokeWidth': 0.7, 'color': RULE},
     'encoding': {'x': {'field': 'x0', 'type': 'quantitative', **AX},
                  'y': {'field': 'y0', 'type': 'quantitative', **AX},
                  'x2': {'field': 'x'}, 'y2': {'field': 'y'}}},
    {'data': csv('seasonality_spokes.csv', {'lx': 'number', 'ly': 'number'}),
     'mark': {'type': 'text', 'fontSize': 11.5, 'color': INK_SOFT},
     'encoding': {'x': {'field': 'lx', 'type': 'quantitative', **AX},
                  'y': {'field': 'ly', 'type': 'quantitative', **AX},
                  'text': {'field': 'month_name', 'type': 'nominal'}}},
    {'data': {'values': [{'ring': 75, 'x': 0, 'y': 57.0, 'label': '75'}, {'ring': 100, 'x': 0, 'y': 82.0, 'label': '100  (yearly average)'}, {'ring': 125, 'x': 0, 'y': 107.0, 'label': '125'}, {'ring': 150, 'x': 0, 'y': 132.0, 'label': '150'}]},
     'mark': {'type': 'text', 'fontSize': 9.5, 'color': INK_FAINT, 'align': 'left',
              'baseline': 'middle', 'dx': 5},
     'encoding': {'x': {'field': 'x', 'type': 'quantitative', **AX},
                  'y': {'field': 'y', 'type': 'quantitative', **AX},
                  'text': {'field': 'label', 'type': 'nominal'}}},
    {'data': csv('seasonality_polar.csv', {'x': 'number', 'y': 'number', 'month': 'number', 'value': 'number'}),
     'mark': {'type': 'line', 'strokeWidth': 2.6, 'interpolate': 'cardinal', 'opacity': 0.95},
     'encoding': {'x': {'field': 'x', 'type': 'quantitative', **AX},
                  'y': {'field': 'y', 'type': 'quantitative', **AX},
                  'order': {'field': 'month', 'type': 'quantitative'},
                  'color': {'field': 'series_label', 'type': 'nominal', 'title': None,
                            'scale': {'domain': ['Malaysia', 'Worldwide'], 'range': [ATTN_1, '#8C9AA3']},
                            # Every other legend on the page sits at the bottom, left-aligned
                            # to the panel edge. A hand-placed one here broke that sight line.
                            'legend': {'orient': 'bottom', 'direction': 'horizontal',
                                       'title': None, 'titleAnchor': 'start',
                                       'labelColor': INK, 'labelFontSize': 12}}}},
    {'data': csv('seasonality_polar.csv', {'x': 'number', 'y': 'number', 'month': 'number', 'value': 'number'}),
     'transform': [{'filter': 'datum.month <= 12'}],
     'mark': {'type': 'point', 'filled': True, 'size': 70, 'stroke': PAPER, 'strokeWidth': 1.5},
     'encoding': {'x': {'field': 'x', 'type': 'quantitative', **AX},
                  'y': {'field': 'y', 'type': 'quantitative', **AX},
                  'color': {'field': 'series_label', 'type': 'nominal',
                            'scale': {'domain': ['Malaysia', 'Worldwide'], 'range': [ATTN_1, '#8C9AA3']}},
                  'tooltip': [
                    {'field': 'series_label', 'type': 'nominal', 'title': 'Series'},
                    {'field': 'month_name', 'type': 'nominal', 'title': 'Month'},
                    {'field': 'value', 'type': 'quantitative',
                     'title': 'Seasonal index (yearly average = 100)', 'format': '.1f'}]}}],
  'config': {'view': {'stroke': None}}})

# ───────────────────────── 13 planting window ───────────────────────────────
write('13_planting_window.json', {
  'description': 'Interval chart: the three consecutive months with the least rainfall in each '
                 'state, from the NASA POWER climatology. Bars span that drier window.',
  'data': csv('planting_window.csv',
              {'start_month': 'number', 'end_month': 'number',
               'window_rain_mm': 'number', 'annual_rain_mm': 'number'}),
  'transform': [DROP_WP, {'calculate': 'datum.end_month + 1', 'as': 'end_edge'}],
  'width': W_FULL - 110, 'height': 384,
  'encoding': {
    'y': {'field': 'state_name', 'type': 'nominal', 'title': None,
          'sort': {'field': 'start_month'},
          'axis': {'domain': False, 'ticks': False, 'labelFontSize': 11.5, 'labelColor': INK}},
    'x': {'field': 'start_month', 'type': 'quantitative',
          'title': None,
          'scale': {'domain': [1, 13], 'nice': False},
          'axis': {'values': [1,2,3,4,5,6,7,8,9,10,11,12],
                   'labelExpr': "['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][datum.value-1]",
                   'labelAngle': 0, 'orient': 'top', 'grid': True, 'gridColor': RULE,
                   'gridDash': [2, 3], 'domain': False, 'ticks': False,
                   'labelColor': INK, 'labelFontSize': 12, 'labelPadding': 6}},
    'x2': {'field': 'end_edge'},
    'color': {'field': 'window_rain_mm', 'type': 'quantitative',
              'title': 'Rainfall across the window (millimetres)',
              'scale': {'range': [RAIN[1], RAIN[6]]},
              'legend': left_legend(95, 410, gradientLength=220)},
    'tooltip': [
      {'field': 'state_name', 'type': 'nominal', 'title': 'State'},
      {'field': 'region', 'type': 'nominal', 'title': 'Region'},
      {'field': 'window_label', 'type': 'nominal', 'title': 'Driest three months'},
      {'field': 'window_rain_mm', 'type': 'quantitative', 'title': 'Rain in that window (millimetres)', 'format': ',.0f'},
      {'field': 'wettest_month_name', 'type': 'nominal', 'title': 'Wettest month'},
      {'field': 'annual_rain_mm', 'type': 'quantitative', 'title': 'Annual rainfall (millimetres)', 'format': ',.0f'}]},
  'layer': [
    {'mark': {'type': 'bar', 'cornerRadius': 3, 'height': 20}},
    # The rainfall across each window, printed at the end of its bar. The colour
    # already carries it, but a reader comparing two states needs the number.
    {'mark': {'type': 'text', 'align': 'left', 'dx': 9, 'fontSize': 10.5,
              'fontWeight': 600, 'color': INK_SOFT},
     'encoding': {'x': {'field': 'end_edge', 'type': 'quantitative'}, 'x2': None,
                  'color': {'value': INK_SOFT},
                  'text': {'field': 'window_rain_mm', 'type': 'quantitative', 'format': ',.0f'}}}],
  'config': {'view': {'stroke': None}}})

# ───────────────────────── 14 rainfall against interest ────────────────────
# Two y scales, not three: an independent resolve gives every sibling layer its own
# scale, so the line, its points and its annotation are nested in one child layer.
# Both series carry a datum colour on the SAME scale so one shared legend names them —
# without it the only clue to which mark is which is the colour of the axis titles.
SERIES = ['Rainfall (left axis)', 'Search interest (right axis)']
SERIES_SCALE = {'domain': SERIES, 'range': [RAIN[2], ATTN_1]}
RIGHT_Y = {'field': 'malaysia_index', 'type': 'quantitative',
           'scale': {'zero': False, 'nice': True}}

write('14_rain_vs_interest.json', {
  'description': 'Dual-axis layered chart: average monthly rainfall across all sixteen states '
                 '(bars, left axis) against Malaysia\u2019s seasonal index of gardening search '
                 'interest (line, right axis). December is both the wettest month of the year '
                 'and the quietest month for searching.',
  'data': csv('seasonality.csv',
              {'month': 'number', 'malaysia_index': 'number', 'rainfall_mm': 'number'}),
  'width': 380, 'height': 408,
  'encoding': {
    'x': {'field': 'month_name', 'type': 'ordinal', 'sort': MONTHS, 'title': None,
          'axis': {'labelAngle': 0, 'domain': False, 'ticks': False, 'grid': False,
                   'labelColor': INK, 'labelFontSize': 11.5}},
    'color': {'datum': SERIES[0], 'type': 'nominal', 'title': None,
              'scale': SERIES_SCALE,
              'legend': left_legend(50, 440, direction='vertical', labelColor=INK,
                                    labelFontSize=11.5, labelLimit=320,
                                    symbolType='square', symbolSize=150, rowPadding=2)}},
  'layer': [
    {'mark': {'type': 'bar', 'cornerRadiusTopLeft': 3, 'cornerRadiusTopRight': 3, 'size': 20},
     'encoding': {
       'y': {'field': 'rainfall_mm', 'type': 'quantitative',
             'title': 'Average rainfall (millimetres)',
             'axis': {'grid': True, 'gridColor': RULE, 'gridDash': [2, 3], 'domain': False,
                      'ticks': False, 'titleColor': RAIN_1, 'labelColor': INK_SOFT}},
       'tooltip': [
         {'field': 'month_name', 'type': 'nominal', 'title': 'Month'},
         {'field': 'rainfall_mm', 'type': 'quantitative', 'title': 'Rainfall (millimetres)', 'format': ',.0f'},
         {'field': 'malaysia_index', 'type': 'quantitative',
          'title': 'Search interest (yearly average = 100)', 'format': '.1f'}]}},
    {'layer': [
       {'mark': {'type': 'line', 'strokeWidth': 2.8, 'interpolate': 'monotone',
                 'point': {'filled': True, 'size': 70, 'color': ATTN_1,
                           'stroke': PAPER, 'strokeWidth': 1.5}},
        'encoding': {
          'color': {'datum': SERIES[1], 'type': 'nominal', 'scale': SERIES_SCALE},
          'y': {**RIGHT_Y, 'title': 'Search interest (yearly average = 100)',
                'axis': {'grid': False, 'domain': False, 'ticks': False,
                         'titleColor': ATTN_1, 'labelColor': INK_SOFT}},
          'tooltip': [
            {'field': 'month_name', 'type': 'nominal', 'title': 'Month'},
            {'field': 'malaysia_index', 'type': 'quantitative',
             'title': 'Search interest (yearly average = 100)', 'format': '.1f'}]}},
       {'transform': [{'filter': "datum.month_name == 'Dec'"}],
        'mark': {'type': 'text', 'align': 'right', 'dx': -12, 'dy': -14, 'fontSize': 11.5,
                 'fontStyle': 'italic', 'color': ATTN[5]},
        'encoding': {'y': RIGHT_Y, 'color': {'value': ATTN[5]},
                     'text': {'value': 'wettest month, quietest searches'}}}]}],
  'resolve': {'scale': {'y': 'independent'}},
  'config': {'view': {'stroke': None}}})
