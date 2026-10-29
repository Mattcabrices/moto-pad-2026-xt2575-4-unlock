"""Round-trip every built filesystem; compare contents and Linux metadata."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parent
AFSR = Path(os.environ.get('AFSR', 'afsr.exe' if os.name == 'nt' else 'afsr'))
PARTS = {'system': 'system_a', 'product': 'product_a', 'system_ext': 'system_ext_a'}


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    report = json.loads((ROOT / 'build-report.json').read_text())
    if len(report['images']) != 3:
        raise ValueError('Build incomplete')
    inventory = json.loads((ROOT / 'super-inventory.json').read_text())
    partitions = {p['name']:p for p in inventory['partitions']}
    results = []
    for part, name in PARTS.items():
        built = ROOT / 'output' / 'candidates' / f'{name}.travel-lean.UNSIGNED.img'
        if built.stat().st_size > partitions[name]['size']:
            raise ValueError(f'{name} no longer fits stock logical partition')
        if sha(ROOT / 'stock-images' / f'{name}.img') != partitions[name]['extracted_sha256']:
            raise ValueError(f'Stock image changed: {name}')
        tree = ROOT / 'validation-tree' / part
        meta = ROOT / f'{part}.roundtrip.toml'
        if tree.exists() or meta.exists():
            raise ValueError(f'Refusing to reuse prior validation outputs: {part}')
        print(f'Round-trip unpacking {part}...', flush=True)
        with (ROOT / 'output' / f'{part}.unpack.log').open('w') as log:
            subprocess.run([str(AFSR), 'unpack', '-i', str(built),
                            '--output-tree', str(tree), '--output-metadata', str(meta)],
                           check=True, stdout=log, stderr=subprocess.STDOUT)
        expected_doc = tomllib.loads((ROOT / f'{part}.lean.toml').read_text())
        actual_doc = tomllib.loads(meta.read_text())
        original_doc = tomllib.loads((ROOT / f'{part}.stock.toml').read_text())
        for key in ('type', 'uuid', 'block_size', 'creation_time'):
            if expected_doc['metadata'].get(key) != actual_doc['metadata'].get(key):
                raise ValueError(f'{part}: filesystem metadata differs: {key}')
        if set(actual_doc['metadata']['features']) - set(original_doc['metadata']['features']):
            raise ValueError(f'{part}: introduces unsupported/unreviewed filesystem features')
        expected = {e['path']: e for e in expected_doc['entries']}
        actual = {e['path']: e for e in actual_doc['entries']}
        if expected.keys() != actual.keys():
            raise ValueError(f'{part}: round-trip entry set mismatch')
        checked_files = checked_bytes = 0
        for path, a in expected.items():
            b = actual[path]
            for key, default in [('file_type', None), ('file_mode', '000'), ('uid', 0), ('gid', 0),
                                 ('mtime', None), ('symlink_target', None), ('xattrs', {})]:
                if a.get(key, default) != b.get(key, default):
                    raise ValueError(f'{part}{path}: metadata differs: {key}')
            if a['file_type'] == 'RegularFile':
                source = ROOT / a['source']
                out = tree / b.get('source', path.lstrip('/'))
                if sha(source) != sha(out):
                    raise ValueError(f'{part}{path}: contents differ')
                checked_files += 1
                checked_bytes += out.stat().st_size
        results.append(dict(partition=name, filesystem_roundtrip_valid=True,
                            entries=len(expected), regular_files=checked_files,
                            file_bytes=checked_bytes, image_bytes=built.stat().st_size,
                            stock_partition_bytes=partitions[name]['size'],
                            fits_stock_partition=True, stock_extracted_image_unchanged=True,
                            filesystem_features=actual_doc['metadata']['features'],
                            image_sha256=sha(built)))
        print(f'{part}: verified {len(expected)} entries, {checked_files} file hashes', flush=True)
    # Audit selected Android files to demonstrate absence of removed APKs.
    original_apps = json.loads((ROOT / 'apps.json').read_text())
    removed = set(report['removed_packages'])
    for app in original_apps:
        part, rel = app['path'].split('/', 1)
        path = ROOT / 'validation-tree' / part / rel
        if path.exists() == (app['package'] in removed):
            raise ValueError(f'Unexpected APK retention/removal: {app["path"]}')
    result = dict(status='OFFLINE FILESYSTEM VALIDATION PASSED - NOT BOOT TESTED',
                  partitions=results, package_removals_verified=True,
                  manufacturer_signing=False, avb_chain_updated=False,
                  device_flashed=False, device_boot_tested=False)
    (ROOT / 'validation-report.json').write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
