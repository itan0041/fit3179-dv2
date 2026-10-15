// Render every spec to SVG with Vega in Node, resolving data files from disk,
// so each chart can be inspected without a browser.
import fs from 'fs';
import path from 'path';
import * as vl from 'vega-lite';
import * as vega from 'vega';

const ROOT = process.cwd();
const files = fs.readdirSync('specs').filter(f => f.endsWith('.json')).sort();

const loader = vega.loader({ baseURL: ROOT + '/', mode: 'file' });

for (const f of files) {
  const spec = JSON.parse(fs.readFileSync(`specs/${f}`, 'utf8'));
  const theme = JSON.parse(fs.readFileSync('qa/theme.json', 'utf8'));
  try {
    const out = vl.compile(spec, { config: theme });
    const view = new vega.View(vega.parse(out.spec), { loader, renderer: 'none' });
    await view.runAsync();
    const svg = await view.toSVG();
    const name = f.replace(/\.json$/, '.svg');
    fs.writeFileSync(path.join('qa', name), svg);
    console.log(`ok    ${name}  ${(svg.length / 1024).toFixed(0)} KB`);
    view.finalize();
  } catch (e) {
    console.log(`FAIL  ${f}\n        ${e.message}`);
  }
}
