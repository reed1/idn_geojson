import csv
import glob
import os
import json

import subprocess
root = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                      capture_output=True).stdout.decode('utf8').strip()

def main():
    with open('box/kab_mapping.csv') as f:
        kabmaps = list(csv.DictReader(f))
    with open('box/step3.sh', 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('set -euo pipefail\n')
        f.write('\n')

        for fname in os.listdir('box/result_maps'):
            src = f'box/result_maps/{fname}'
            dst = root + '/maps/' + fname
            f.write(f'cp "{src}" "{dst}"\n')

        for e in kabmaps:
            kode_old = e['kode_old']
            kode_new = e['kode_new']
            srcs = glob.glob(f'{root}/maps/idn_{kode_old}*.json')
            for src in srcs:
                dst = src.replace(kode_old, kode_new)
                f.write(f'mv "{src}" "{dst}"\n')

    print('Generated, now run box/step3.sh manually')

if __name__ == '__main__':
    main()