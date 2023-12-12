import csv
import json
import fmg

import subprocess
root = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                      capture_output=True).stdout.decode('utf8').strip()


def read_papua_kabs():
    with open('box/kab.csv') as f:
        rows = list(csv.DictReader(f))
    return [e for e in rows if 'papua' in e['prov_nama'].lower()]


def read_features():
    files = [
        root + '/maps/idn_ID91.json',
        root + '/maps/idn_ID94.json',
    ]
    features = []
    for f in files:
        with open(f) as f:
            geo = json.load(f)
        features += geo['features']
    return features


def main():
    features = read_features()
    arows = [e['properties'] for e in features]
    brows = read_papua_kabs()

    m = fmg.fuzzy_match_group(arows, 'ADM2_EN', brows, 'kab_nama')
    if len(m['no_match']['a']) > 0:
        raise Exception('No match', m['no_match']['a'])
    prov_kodes = set(e['prov_kode'] for e in brows)
    kab_mapping = {}
    for prov_kode in prov_kodes:
        kab_pairs = [e for e in m['pairs'] if e['b']['prov_kode'] == prov_kode]
        kab_features = []
        for kp in kab_pairs:
            kab_feat = next(
                e for e in features
                if e['properties']['ADM2_PCODE'] == kp['a']['ADM2_PCODE'])
            new_feat = {
                **kab_feat,
                'properties': {
                    'ADM0_PCODE': 'ID',
                    'ADM0_EN': 'Indonesia',
                    'ADM1_PCODE': 'ID' + kp['b']['prov_kode'],
                    'ADM1_EN': kp['b']['prov_nama'],
                    'ADM2_PCODE': 'ID' + kp['b']['kab_kode'],
                    'ADM2_EN': kp['b']['kab_nama'],
                }
            }
            kab_features.append(new_feat)
            kab_mapping[kab_feat['properties']['ADM2_PCODE']] = kp['b']
        with open(f'box/result_maps/idn_ID{prov_kode}.json', 'w') as f:
            json.dump({
                'type': 'FeatureCollection',
                'features': kab_features
            }, f)

    with open('box/kab_mapping.csv', 'w') as f:
        w = csv.writer(f)
        w.writerow(['kode_old', 'kode_new'])
        for k, v in kab_mapping.items():
            if k != 'ID' + v['kab_kode']:
                w.writerow([k, 'ID' + v['kab_kode']])

    with open(root + '/maps/idn_admin2.json') as f:
        adm2 = json.load(f)
    for feat in adm2['features']:
        kab_kode = feat['properties']['ADM2_PCODE']
        if kab_kode in kab_mapping:
            kab_row = kab_mapping[kab_kode]
            feat['properties'] = {
                'ADM0_PCODE': 'ID',
                'ADM0_EN': 'Indonesia',
                'ADM1_PCODE': 'ID' + kab_row['prov_kode'],
                'ADM1_EN': kab_row['prov_nama'],
                'ADM2_PCODE': 'ID' + kab_row['kab_kode'],
                'ADM2_EN': kab_row['kab_nama'],
            }
    with open('box/result_maps/idn_admin2.json', 'w') as f:
        json.dump(adm2, f)


if __name__ == '__main__':
    main()