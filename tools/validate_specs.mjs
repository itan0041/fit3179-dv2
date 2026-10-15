// Compile every spec with the real Vega-Lite compiler and build the Vega dataflow,
// so syntax and encoding errors surface here rather than silently in the browser.
import fs from 'fs';
import * as vl from 'vega-lite';
import * as vega from 'vega';

const files = fs.readdirSync('specs').filter(f => f.endsWith('.json')).sort();
let bad = 0;
for (const f of files) {
  const spec = JSON.parse(fs.readFileSync(`specs/${f}`, 'utf8'));
  const logger = vega.logger(vega.Warn);
  const msgs = [];
  logger.warn = (...a) => msgs.push('WARN  ' + a.join(' '));
  logger.error = (...a) => msgs.push('ERROR ' + a.join(' '));
  try {
    const out = vl.compile(spec, {logger});
    new vega.View(vega.parse(out.spec), {renderer: 'none'});
    const errs = msgs.filter(m => m.startsWith('ERROR'));
    if (errs.length) bad++;
    console.log(`${errs.length ? 'FAIL' : 'ok  '}  ${f}`);
    msgs.slice(0, 6).forEach(m => console.log('        ' + m));
  } catch (e) {
    bad++;
    console.log(`FAIL  ${f}\n        ${e.message}`);
  }
}
console.log(bad ? `\n${bad} spec(s) failed to compile.` : '\nAll specs compiled cleanly.');
