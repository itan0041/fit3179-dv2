// Build a compact TopoJSON of Malaysia's 16 states from DOSM's official boundary file.
import fs from 'fs';
import {topology} from 'topojson-server';
import {presimplify, simplify, quantile} from 'topojson-simplify';

const gj = JSON.parse(fs.readFileSync('data/source/dosm_state.geojson','utf8'));
gj.features.forEach(f => { f.properties = {state: f.properties.state, code: f.properties.code_state}; });

let topo = topology({states: gj}, 1e5);
topo = presimplify(topo);
topo = simplify(topo, quantile(topo, 0.30));

fs.writeFileSync('data/malaysia_states.topo.json', JSON.stringify(topo));
console.log('features:', topo.objects.states.geometries.length,
            '| bytes:', fs.statSync('data/malaysia_states.topo.json').size);
console.log('states:', topo.objects.states.geometries.map(g=>g.properties.state).join(', '));
