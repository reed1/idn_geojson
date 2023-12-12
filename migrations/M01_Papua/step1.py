import json
import os
import fmg
import csv

def main():
    with open('box/prov.csv') as f:
        provs = list(csv.DictReader(f))
    with open('box/ADM1_New.geojson') as f:
        geo = json.load(f)

    arows = [e['properties'] for e in geo['features']]
    brows = provs
    m = fmg.fuzzy_match_group(arows, 'wilayah', brows, 'nama')
    if len(m['no_match']['a']) > 0:
        raise Exception('No match', m['no_match']['a'])

    mapping = {}
    for p in m['pairs']:
        mapping[p['a']['wilayah']] = p['b']

    for f in geo['features']:
        prov = mapping[f['properties']['wilayah']]
        f['properties'] = {
            'ADM1_EN': prov['nama'],
            'ADM1_PCODE': 'ID' + prov['kode'],
        }

    os.makedirs('box/result_maps', exist_ok=True)
    with open('box/result_maps/idn_admin1.geojson', 'w') as f:
        json.dump(geo, f)

if __name__ == '__main__':
    main()