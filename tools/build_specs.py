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
ATTN_1, GROW_1, RAIN_1 = '#C2603C', '#4C8D48', '#2F6A9A'

CROP_COLORS = {
    'Vegetables': '#4C8D48', 'Fruits': '#D98A28', 'Herbs': '#7E9E3A',
    'Spices': '#B5541F', 'Cash crops': '#8C6D3F', 'Paddy (rice)': '#C9A227',
    'Coconut': '#6B8E6E', 'Industrial crops': '#5C6F7A', 'Flowers': '#B5567E',
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

# ───────────────────────── 01 ridgeline ─────────────────────────────────────
# width/height belong to the CHILD spec of a facet; setting them on the facet
# itself leaves the child at its default size and pads the rest of the frame.
write('01_search_ridgeline.json', {
  'description': 'Ridgeline plot: monthly Google Trends search interest in Malaysia for four '
                 'gardening terms, January 2014 to September 2026. The pale band is the raw '
                 'monthly index and the solid line is a five-month centred average. All four '
                 'row is scaled to its own peak, so the shapes are comparable even though '
                 'the terms differ greatly in volume.',
  'data': csv('trends_my_monthly.csv', {'date': 'date', 'value': 'number'}),
  'transform': [
    {'window': [{'op': 'mean', 'field': 'value', 'as': 'smooth'}],
     'frame': [-2, 2], 'groupby': ['keyword'], 'sort': [{'field': 'date'}]}],
  'spacing': -62,
  'facet': {'row': {'field': 'keyword', 'type': 'nominal', 'title': None,
                    'sort': ['hidroponik', 'gardening', 'berkebun', 'kebun sayur'],
                    'header': {'labelAngle': 0, 'labelAlign': 'right', 'labelOrient': 'left',
                               'labelPadding': 10, 'labelLimit': 150, 'labelFontSize': 12.5,
                               'labelFontStyle': 'italic', 'labelColor': INK,
                               'labelBaseline': 'middle'}}},
  'spec': {
    'width': 820, 'height': 124,
    'layer': [
      {'mark': {'type': 'area', 'interpolate': 'monotone', 'fillOpacity': 0.72,
                'stroke': PAPER, 'strokeWidth': 1.2, 'line': False},
       'encoding': {
         'x': {'field': 'date', 'type': 'temporal', 'title': None,
               'axis': {'format': '%Y', 'tickCount': 'year', 'grid': False,
                        'domainColor': RULE, 'tickColor': RULE, 'labelColor': INK_SOFT}},
         'y': {'field': 'value', 'type': 'quantitative', 'scale': {'zero': True}, 'axis': None},
         'color': {'value': ATTN[2]}}},
      {'mark': {'type': 'line', 'interpolate': 'monotone', 'strokeWidth': 1.8},
       'encoding': {
         'x': {'field': 'date', 'type': 'temporal'},
         'y': {'field': 'smooth', 'type': 'quantitative', 'scale': {'zero': True}, 'axis': None},
         'color': {'value': ATTN[5]},
         'tooltip': [
           {'field': 'keyword_label', 'type': 'nominal', 'title': 'Search term'},
           {'field': 'date', 'type': 'temporal', 'title': 'Month', 'format': '%B %Y'},
           {'field': 'value', 'type': 'quantitative', 'title': 'Interest that month (0-100)'},
           {'field': 'smooth', 'type': 'quantitative', 'title': 'Five-month average', 'format': '.1f'}]}},
      {'data': {'values': [{'date': '2020-03-18'}]},
       'mark': {'type': 'rule', 'color': INK, 'strokeDash': [4, 3], 'strokeWidth': 1.1,
                'opacity': 0.75},
       'encoding': {'x': {'field': 'date', 'type': 'temporal'}}}]},
  'resolve': {'scale': {'y': 'independent', 'x': 'shared'}},
  'config': {'view': {'stroke': None}}})

# ───────────────────────── 02 slope graph ───────────────────────────────────
write('02_category_slope.json', {
  'description': 'Slope graph: planted area of each crop category in 2024 relative to 2014 (2014 = 100).',
  'data': csv('crops_category_malaysia.csv',
              {'year': 'number', 'area_index_2014': 'number', 'prod_index_2014': 'number',
               'label_area': 'number', 'label_prod': 'number'}),
  'params': [{'name': 'measure', 'value': 'Planted area',
              'bind': {'input': 'radio', 'options': ['Planted area', 'Production'],
                       'name': 'Compare by  '}}],
  'transform': [
    {'filter': 'datum.year == 2014 || datum.year == 2024'},
    {'calculate': "measure === 'Planted area' ? datum.area_index_2014 : datum.prod_index_2014",
     'as': 'value'},
    {'calculate': "measure === 'Planted area' ? datum.label_area : datum.label_prod",
     'as': 'label_y'},
    {'filter': 'isValid(datum.value)'}],
  'width': 300, 'height': 430,
  'padding': {'left': 5, 'top': 5, 'bottom': 5, 'right': 12},
  'encoding': {
    'x': {'field': 'year', 'type': 'ordinal', 'title': None,
          'axis': {'labelAngle': 0, 'labelFontSize': 13, 'labelColor': INK,
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
    {'mark': {'type': 'line', 'strokeWidth': 2.4, 'opacity': 0.9}},
    {'mark': {'type': 'point', 'filled': True, 'size': 70, 'opacity': 1},
     'encoding': {'tooltip': [
        {'field': 'crop_label', 'type': 'nominal', 'title': 'Category'},
        {'field': 'year', 'type': 'ordinal', 'title': 'Year'},
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
  'width': 318, 'height': 430,
  'padding': {'left': 5, 'top': 5, 'bottom': 5, 'right': 12},
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
    {'mark': {'type': 'line', 'strokeWidth': 2.6, 'interpolate': 'monotone', 'opacity': 0.85}},
    {'mark': {'type': 'point', 'filled': True, 'size': 60}},
    {'transform': [{'filter': 'datum.year == 2024'}],
     'mark': {'type': 'text', 'align': 'left', 'dx': 10, 'fontSize': 11.5, 'fontWeight': 500},
     'encoding': {'text': {'field': 'crop_label', 'type': 'nominal'}}}],
  'config': {'view': {'stroke': None}}})

# ───────────────────────── 04 connected scatter ─────────────────────────────
write('04_vegetable_connected_scatter.json', {
  'description': 'Connected scatterplot: Malaysia’s vegetable planted area against '
                 'vegetable production, one point per year, joined in time order.',
  'data': csv('crops_category_malaysia.csv',
              {'year': 'number', 'planted_area_ha': 'number', 'production_tonnes': 'number'}),
  'transform': [{'filter': "datum.crop_type == 'vegetables'"}],
  'width': 900, 'height': 380,
  'encoding': {
    'x': {'field': 'planted_area_ha', 'type': 'quantitative',
          'title': 'Planted area (hectares)',
          'scale': {'zero': False, 'nice': True},
          'axis': {'grid': True, 'gridColor': RULE, 'gridDash': [2, 3], 'domain': False,
                   'ticks': False, 'format': ',.0f', 'tickCount': 6,
                   'labelColor': INK_SOFT, 'titleColor': INK_SOFT}},
    'y': {'field': 'production_tonnes', 'type': 'quantitative',
          'title': 'Production (tonnes)',
          'scale': {'zero': False, 'nice': True},
          'axis': {'grid': True, 'gridColor': RULE, 'gridDash': [2, 3], 'domain': False,
                   'ticks': False, 'format': ',.0f', 'labelColor': INK_SOFT, 'titleColor': INK_SOFT}}},
  'layer': [
    {'mark': {'type': 'line', 'interpolate': 'linear', 'strokeWidth': 2,
              'color': GROW[4], 'opacity': 0.8},
     'encoding': {'order': {'field': 'year', 'type': 'quantitative'}}},
    {'mark': {'type': 'point', 'filled': True, 'size': 150, 'color': GROW[5],
              'stroke': PAPER, 'strokeWidth': 2},
     'encoding': {'tooltip': [
        {'field': 'year', 'type': 'quantitative', 'title': 'Year', 'format': 'd'},
        {'field': 'planted_area_ha', 'type': 'quantitative', 'title': 'Planted area (hectares)', 'format': ',.0f'},
        {'field': 'production_tonnes', 'type': 'quantitative', 'title': 'Production (tonnes)', 'format': ',.0f'}]}},
    # 2019 and 2020 sit almost on top of each other, and dy is a mark property rather
    # than an encoding channel, so the 2019 label gets its own layer below the dot.
    {'transform': [{'filter': 'datum.year != 2019'}],
     'mark': {'type': 'text', 'align': 'left', 'dx': 11, 'dy': -9, 'fontSize': 11.5,
              'fontWeight': 600, 'color': INK},
     'encoding': {'text': {'field': 'year', 'type': 'quantitative', 'format': 'd'}}},
    {'transform': [{'filter': 'datum.year == 2019'}],
     'mark': {'type': 'text', 'align': 'left', 'dx': 11, 'dy': 17, 'fontSize': 11.5,
              'fontWeight': 600, 'color': INK},
     'encoding': {'text': {'field': 'year', 'type': 'quantitative', 'format': 'd'}}},
    {'transform': [{'filter': 'datum.year == 2018'}],
     'mark': {'type': 'text', 'align': 'left', 'dx': 10, 'dy': 22, 'fontSize': 11.5,
              'fontStyle': 'italic', 'color': ATTN_1},
     'encoding': {'text': {'value': 'lowest point of the decade'}}},
    {'transform': [{'filter': 'datum.year == 2024'}],
     'mark': {'type': 'text', 'align': 'right', 'dx': -14, 'dy': 16, 'fontSize': 11.5,
              'fontStyle': 'italic', 'color': GROW[6]},
     'encoding': {'text': {'value': 'highest in eleven years'}}}],
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
MAP_SCALE = 3500
PEN_W, BOR_W = 330, 620
MAP_H = 430
SPIKE_H = 520

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

BOTTOM_LEGEND = {'orient': 'bottom', 'direction': 'horizontal', 'titleLimit': 1000,
                 'labelLimit': 220, 'titleColor': INK, 'labelColor': INK_SOFT,
                 'titleFontSize': 11.5, 'titleAnchor': 'start'}

# ───────────────────────── 05 choropleth map ────────────────────────────────
def choropleth_panel(codes, width, title, legend, proj):
    return {
      'width': width, 'height': MAP_H, 'title': {'text': title, 'fontSize': 13, 'dy': -6},
      'data': TOPO, 'projection': proj,
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
           'title': 'Hectares per 1,000 people', 'format': '.2f'}]}}

write('05_map_choropleth.json', {
  'description': 'Choropleth map: hectares of vegetable land per 1,000 residents by state, 2024. '
                 'Drawn as two separately fitted panels so the peninsular states stay legible.',
  'hconcat': [choropleth_panel(PEN, PEN_W, 'Peninsular Malaysia', True, PEN_PROJ),
              choropleth_panel(BOR, BOR_W, 'Sabah, Sarawak and Labuan', False, BOR_PROJ)],
  **shared()})

# ───────────────────────── 06 proportional symbol map ───────────────────────
def symbol_panel(codes, width, title, legend, proj):
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
                    'scale': {'type': 'sqrt', 'range': [30, 3000]},
                    'legend': {**BOTTOM_LEGEND, 'format': ',.0f',
                               'values': [50000, 200000, 400000, 600000],
                               'symbolFillColor': GROW[4],
                               'symbolStrokeColor': '#1A4A27'} if legend else None},
           'tooltip': [
             {'field': 'state', 'type': 'nominal', 'title': 'State'},
             {'field': 'veg_prod_tonnes', 'type': 'quantitative', 'title': 'Production (tonnes)', 'format': ',.0f'},
             {'field': 'veg_kg_per_person', 'type': 'quantitative', 'title': 'Kilograms per resident', 'format': ',.1f'}]}}]}

write('06_map_symbol.json', {
  'description': 'Proportional symbol map: vegetable production in tonnes by state, 2024. '
                 'Circle area is proportional to tonnage.',
  'hconcat': [symbol_panel(PEN, PEN_W, 'Peninsular Malaysia', True, PEN_PROJ),
              symbol_panel(BOR, BOR_W, 'Sabah, Sarawak and Labuan', False, BOR_PROJ)],
  **shared()})

# ───────────────────────── 07 bivariate choropleth ──────────────────────────
def bivariate_panel(codes, width, title, proj):
    return {
      'width': width, 'height': MAP_H, 'title': {'text': title, 'fontSize': 13, 'dy': -6},
      'data': TOPO, 'projection': proj,
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
           'title': 'Hectares per 1,000 people', 'format': '.2f'}]}}

write('07_map_bivariate.json', {
  'description': 'Bivariate choropleth map: search interest in gardening against vegetable land '
                 'per 1,000 residents. Each state takes a colour from a three-by-three key; the '
                 'colours are pre-computed in the bi_color column.',
  'hconcat': [bivariate_panel(PEN, PEN_W, 'Peninsular Malaysia', PEN_PROJ),
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
                     'scale': {'domain': ['Increase', 'Decrease'], 'range': [GROW[5], ATTN[4]]},
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
                                'value': ATTN[5]}}}]}

write('08_map_spike.json', {
  'description': 'Spike map: change in vegetable planted area between 2014 and 2024. Spike '
                 'length is proportional to the percentage change, rising for an increase and '
                 'falling for a decrease. Changes of 25 per cent or more are labelled.',
  'hconcat': [spike_panel(PEN, PEN_W, 'Peninsular Malaysia', True, pen_proj(SPIKE_H, 330)),
              spike_panel(BOR, BOR_W, 'Sabah, Sarawak and Labuan', False, bor_proj(SPIKE_H, 330))],
  **shared()})

# ───────────────────────── 09 dumbbell ──────────────────────────────────────
write('09_state_dumbbell.json', {
  'description': 'Dumbbell chart: vegetable planted area by state in 2014 and 2024, '
                 'with a connecting line showing the direction of travel.',
  'data': csv('state_change.csv',
              {'area_2014': 'number', 'area_2024': 'number', 'pct_change': 'number'}),
  'width': 330, 'height': 400,
  'encoding': {
    'y': {'field': 'state', 'type': 'nominal', 'title': None,
          'sort': {'field': 'area_2024', 'order': 'descending'},
          'axis': {'domain': False, 'ticks': False, 'labelFontSize': 11.5,
                   'labelColor': INK, 'grid': True, 'gridColor': RULE, 'gridDash': [1, 4]}},
    'x': {'field': 'area_2014', 'type': 'quantitative',
          'title': 'Vegetable planted area (hectares)',
          'scale': {'type': 'sqrt'},
          'axis': {'grid': False, 'domain': False, 'ticks': False, 'format': ',.0f',
                   'labelColor': INK_SOFT, 'titleColor': INK_SOFT,
                   'values': [0, 2000, 5000, 10000, 20000, 30000]}}},
  'layer': [
    {'mark': {'type': 'rule', 'strokeWidth': 2.2, 'opacity': 0.55},
     'encoding': {'x2': {'field': 'area_2024'},
                  'color': {'field': 'direction', 'type': 'nominal',
                            'scale': {'domain': ['Increase', 'Decrease'], 'range': [GROW[5], ATTN[4]]}}}},
    {'mark': {'type': 'point', 'filled': True, 'size': 95, 'color': '#B9BEB3',
              'stroke': PAPER, 'strokeWidth': 1.5},
     'encoding': {'tooltip': [
        {'field': 'state', 'type': 'nominal', 'title': 'State'},
        {'field': 'area_2014', 'type': 'quantitative', 'title': '2014 (hectares)', 'format': ',.0f'}]}},
    {'mark': {'type': 'point', 'filled': True, 'size': 130, 'stroke': PAPER, 'strokeWidth': 1.5},
     'encoding': {
       'x': {'field': 'area_2024', 'type': 'quantitative'},
       'color': {'field': 'direction', 'type': 'nominal',
                 'title': 'Direction, 2014 to 2024',
                 'scale': {'domain': ['Increase', 'Decrease'], 'range': [GROW[5], ATTN[4]]},
                 'legend': {'orient': 'bottom', 'direction': 'horizontal', 'titleLimit': 400,
                            'titleColor': INK_SOFT, 'labelColor': INK_SOFT}},
       'tooltip': [
         {'field': 'state', 'type': 'nominal', 'title': 'State'},
         {'field': 'area_2024', 'type': 'quantitative', 'title': '2024 (hectares)', 'format': ',.0f'},
         {'field': 'pct_change', 'type': 'quantitative', 'title': 'Change (per cent)', 'format': '+.1f'}]}}],
  'config': {'view': {'stroke': None}}})

# ───────────────────────── 10 waffle ────────────────────────────────────────
WAFFLE_DOMAIN = ['Pahang', 'Johor', 'Kelantan', 'Sarawak', 'Perak', 'Sabah', 'Other states']
WAFFLE_RANGE  = ['#17401F', '#38763E', '#6BA45F', '#9CC78B', '#C6DEB8', '#E4EFDA', '#D6CEBC']
write('10_waffle_share.json', {
  'description': 'Waffle chart: each of the 100 squares is one per cent of Malaysia’s '
                 'vegetable planted area in 2024.',
  'data': csv('waffle_vegetable_share.csv',
              {'row': 'number', 'col': 'number', 'share_pct': 'number', 'squares': 'number'}),
  'width': 330, 'height': 360,
  'mark': {'type': 'square', 'size': 640, 'stroke': PAPER, 'strokeWidth': 3, 'cornerRadius': 2},
  'encoding': {
    'x': {'field': 'col', 'type': 'ordinal', 'axis': None},
    'y': {'field': 'row', 'type': 'ordinal', 'axis': None},
    'color': {'field': 'group', 'type': 'nominal', 'title': 'State',
              'scale': {'domain': WAFFLE_DOMAIN, 'range': WAFFLE_RANGE},
              'legend': {'orient': 'right', 'titleColor': INK, 'labelColor': INK_SOFT,
                         'symbolType': 'square', 'symbolSize': 150, 'labelFontSize': 11.5}},
    'tooltip': [
      {'field': 'state', 'type': 'nominal', 'title': 'State'},
      {'field': 'share_pct', 'type': 'quantitative', 'title': 'Share of national area (per cent)', 'format': '.1f'},
      {'field': 'squares', 'type': 'quantitative', 'title': 'Squares on this chart'}]},
  'config': {'view': {'stroke': None}}})

# ───────────────────────── 11 rainfall heatmap ──────────────────────────────
write('11_rain_heatmap.json', {
  'description': 'Heatmap: average monthly rainfall by state, from a 25-year NASA POWER climatology.',
  'data': csv('climate_states.csv', {'month': 'number', 'rain_mm_month': 'number'}),
  'width': 895, 'height': 430,
  'mark': {'type': 'rect', 'stroke': PAPER, 'strokeWidth': 1.5, 'cornerRadius': 1},
  'encoding': {
    'x': {'field': 'month_name', 'type': 'ordinal', 'title': None,
          'sort': MONTHS,
          'axis': {'labelAngle': 0, 'domain': False, 'ticks': False, 'orient': 'top',
                   'labelFontSize': 12, 'labelColor': INK, 'labelPadding': 6}},
    'y': {'field': 'state', 'type': 'nominal', 'title': None,
          'sort': {'op': 'sum', 'field': 'rain_mm_month', 'order': 'descending'},
          'axis': {'domain': False, 'ticks': False, 'labelFontSize': 11.5, 'labelColor': INK}},
    'color': {'field': 'rain_mm_month', 'type': 'quantitative',
              'title': 'Average rainfall (millimetres per month)',
              'scale': {'type': 'threshold', 'domain': [100, 150, 200, 250, 300, 400], 'range': RAIN},
              'legend': {'orient': 'bottom', 'direction': 'horizontal', 'titleColor': INK,
                         'labelColor': INK_SOFT, 'symbolType': 'square', 'symbolSize': 170,
                         'titleFontSize': 11.5, 'columns': 7}},
    'tooltip': [
      {'field': 'state', 'type': 'nominal', 'title': 'State'},
      {'field': 'city', 'type': 'nominal', 'title': 'Measured at'},
      {'field': 'month_name', 'type': 'nominal', 'title': 'Month'},
      {'field': 'rain_mm_month', 'type': 'quantitative', 'title': 'Rainfall (millimetres)', 'format': ',.0f'},
      {'field': 'tmax_c', 'type': 'quantitative', 'title': 'Average daily maximum (°C)', 'format': '.1f'}]},
  'config': {'view': {'stroke': None}}})

# ───────────────────────── 12 custom radial ─────────────────────────────────
AX = {'scale': {'domain': [-168, 168]}, 'axis': None}
write('12_seasonality_radial.json', {
  'description': 'Custom-built radial chart. Polar coordinates are pre-computed in Python '
                 '(data/seasonality_polar.csv) because Vega-Lite has no polar line mark. '
                 'January is at the top and the months run clockwise. Each series is scaled '
                 'so its own yearly average sits at the 100 ring.',
  'width': 420, 'height': 420,
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
                            'legend': {'orient': 'none', 'legendX': 0, 'legendY': 392,
                                       'direction': 'horizontal', 'title': None,
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
  'transform': [{'calculate': 'datum.end_month + 1', 'as': 'end_edge'}],
  'width': W_FULL - 200, 'height': 420,
  'mark': {'type': 'bar', 'cornerRadius': 3, 'height': 17},
  'encoding': {
    'y': {'field': 'state', 'type': 'nominal', 'title': None,
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
              'legend': {'orient': 'bottom', 'direction': 'horizontal', 'gradientLength': 220,
                         'titleColor': INK, 'labelColor': INK_SOFT, 'titleFontSize': 11.5}},
    'tooltip': [
      {'field': 'state', 'type': 'nominal', 'title': 'State'},
      {'field': 'region', 'type': 'nominal', 'title': 'Region'},
      {'field': 'window_label', 'type': 'nominal', 'title': 'Driest three months'},
      {'field': 'window_rain_mm', 'type': 'quantitative', 'title': 'Rain in that window (millimetres)', 'format': ',.0f'},
      {'field': 'wettest_month_name', 'type': 'nominal', 'title': 'Wettest month'},
      {'field': 'annual_rain_mm', 'type': 'quantitative', 'title': 'Annual rainfall (millimetres)', 'format': ',.0f'}]},
  'config': {'view': {'stroke': None}}})

# ───────────────────────── 14 rainfall against interest ────────────────────
# Only TWO y scales are wanted here. An independent resolve gives every sibling
# layer its own scale, so the line, its points and its annotation are nested in a
# single child layer that shares one scale between them.
RIGHT_Y = {'field': 'malaysia_index', 'type': 'quantitative',
           'scale': {'zero': False, 'nice': True}}

write('14_rain_vs_interest.json', {
  'description': 'Dual-axis layered chart: average monthly rainfall across all sixteen states '
                 '(bars, left axis) against Malaysia\u2019s seasonal index of gardening search '
                 'interest (line, right axis). December is both the wettest month of the year '
                 'and the quietest month for searching.',
  'data': csv('seasonality.csv',
              {'month': 'number', 'malaysia_index': 'number', 'rainfall_mm': 'number'}),
  'width': 355, 'height': 360,
  'encoding': {
    'x': {'field': 'month_name', 'type': 'ordinal', 'sort': MONTHS, 'title': None,
          'axis': {'labelAngle': 0, 'domain': False, 'ticks': False, 'grid': False,
                   'labelColor': INK, 'labelFontSize': 11.5}}},
  'layer': [
    {'mark': {'type': 'bar', 'cornerRadiusTopLeft': 3, 'cornerRadiusTopRight': 3,
              'color': RAIN[2], 'size': 20},
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
       {'mark': {'type': 'line', 'color': ATTN_1, 'strokeWidth': 2.8, 'interpolate': 'monotone',
                 'point': {'filled': True, 'size': 70, 'color': ATTN_1,
                           'stroke': PAPER, 'strokeWidth': 1.5}},
        'encoding': {
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
        'encoding': {'y': RIGHT_Y,
                     'text': {'value': 'wettest month, quietest searches'}}}]}],
  'resolve': {'scale': {'y': 'independent'}},
  'config': {'view': {'stroke': None}}})
