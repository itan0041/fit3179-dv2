/* Loads every Vega-Lite specification and embeds it in its figure.
   The shared theme lives here rather than inside each spec file, so the JSON in
   specs/ stays readable as a description of the idiom alone. */

(function () {
  'use strict';

  var PAPER = '#FAF7F0';
  var INK = '#1C2B22';
  var INK_SOFT = '#5E6E64';
  var RULE = '#DCD5C7';
  var BODY = "'InterVar', -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
  var DISPLAY = "'Fraunces', Georgia, serif";

  var THEME = {
    background: null,
    font: BODY,
    padding: 4,
    axis: {
      labelFont: BODY, labelFontSize: 11.5, labelColor: INK_SOFT,
      titleFont: BODY, titleFontSize: 12, titleColor: INK_SOFT,
      titleFontWeight: 500, titlePadding: 10,
      domainColor: RULE, tickColor: RULE, gridColor: RULE, gridOpacity: 0.9,
      labelPadding: 5
    },
    legend: {
      labelFont: BODY, labelFontSize: 11.5, labelColor: INK_SOFT,
      titleFont: BODY, titleFontSize: 11.5, titleColor: INK,
      titleFontWeight: 600, titlePadding: 8, rowPadding: 5, offset: 14,
      titleLimit: 600, labelLimit: 260, labelOverlap: false
    },
    title: { font: DISPLAY, fontSize: 17, color: INK, fontWeight: 600, anchor: 'start' },
    header: { labelFont: BODY, titleFont: BODY },
    view: { stroke: null, continuousWidth: 400, continuousHeight: 300 },
    range: { category: ['#2D6C35', '#C2603C', '#2F6A9A', '#C9A227', '#7E9E3A', '#B5567E'] },
    text: { font: BODY },
    mark: { font: BODY }
  };

  var CHARTS = [
    ['c01', 'specs/01_search_interest.json'],
    ['c02', 'specs/02_category_slope.json'],
    ['c03', 'specs/03_category_bump.json'],
    ['c04', 'specs/04_vegetable_connected_scatter.json'],
    ['c05', 'specs/05_map_choropleth.json'],
    ['c06', 'specs/06_map_symbol.json'],
    ['c07', 'specs/07_map_bivariate.json'],
    ['c07b', 'specs/07b_bivariate_legend.json'],
    ['c08', 'specs/08_map_spike.json'],
    ['c09', 'specs/09_state_dumbbell.json'],
    ['c10', 'specs/10_waffle_share.json'],
    ['c11', 'specs/11_rain_heatmap.json'],
    ['c12', 'specs/12_seasonality_radial.json'],
    ['c13', 'specs/13_planting_window.json'],
    ['c14', 'specs/14_rain_vs_interest.json']
  ];

  var OPTIONS = {
    actions: { export: true, source: true, compiled: false, editor: false },
    theme: undefined,
    config: THEME,
    renderer: 'svg',
    tooltip: { theme: 'light' }
  };

  window.__chartsReady = 0;
  window.__chartErrors = [];

  function embedOne(id, url) {
    var el = document.getElementById(id);
    if (!el) {
      window.__chartErrors.push(id + ': container missing');
      return Promise.resolve();
    }
    return vegaEmbed(el, url, OPTIONS)
      .then(function () { window.__chartsReady += 1; })
      .catch(function (err) {
        window.__chartErrors.push(id + ': ' + err.message);
        el.innerHTML = '<p style="color:#C2603C;font-size:13.5px">This chart could not be ' +
          'loaded. If you are opening the page from your file system, serve it over HTTP ' +
          'instead, because browsers block local data files.</p>';
        console.error('Failed to embed ' + url, err);
      });
  }

  function run() {
    Promise.all(CHARTS.map(function (c) { return embedOne(c[0], c[1]); }))
      .then(function () {
        window.__allCharts = true;
        console.log('Charts embedded: ' + window.__chartsReady + ' of ' + CHARTS.length);
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
