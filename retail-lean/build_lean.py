"""Create reversible filesystem recipes and optional offline EROFS images.

Never invokes adb/fastboot/flashing tools or modifies source firmware/stock trees.
Linux metadata is retained in TOML; regular files reference the stock tree or
an explicitly supplied asset under assets/.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tomllib
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
AFSR = Path(os.environ.get('AFSR', 'afsr.exe' if os.name == 'nt' else 'afsr'))
PARTS = {'system': 'system_a', 'product': 'product_a', 'system_ext': 'system_ext_a'}


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pack', action='store_true')
    args = ap.parse_args()
    recipe = json.loads((ROOT / 'recipe.json').read_text())
    apps = json.loads((ROOT / 'apps.json').read_text())
    if any('error' in a for a in apps):
        raise ValueError('APK inventory contains parse errors')
    packages = {a['package'] for a in apps}
    removed = set(recipe['remove_packages'])
    keep = set(recipe['keep_packages'])
    if removed & keep or removed - packages or keep - packages:
        raise ValueError(f'Invalid recipe: overlap={removed & keep}, unknown removals={removed-packages}, missing protected={keep-packages}')
    dirs = {part: set() for part in PARTS}
    removed_apks = []
    for app in apps:
        if app['package'] in removed:
            part, path = app['path'].split('/', 1)
            dirs[part].add('/' + str(PurePosixPath(path).parent))
            removed_apks.append(app)

    # Leave the unused carrier facade library in place: other signed OEM APKs
    # may declare it as a shared library. It is not an app or a running process.
    overrides = {}
    assets_map = ROOT / 'assets' / 'overrides.json'
    if assets_map.exists():
        overrides = json.loads(assets_map.read_text())
    changed_xml = []
    removed_entries = []
    for part in PARTS:
        metadata_text = (ROOT / f'{part}.stock.toml').read_text(encoding='utf-8')
        chunks = re.split(r'(?m)^\[\[entries\]\]\s*$', metadata_text)
        parsed = tomllib.loads(metadata_text)
        if len(chunks) - 1 != len(parsed['entries']):
            raise ValueError('Unexpected metadata layout')
        output = [chunks[0]]
        for text, entry in zip(chunks[1:], parsed['entries']):
            path = entry['path']
            if any(path == d or path.startswith(d + '/') for d in dirs[part]):
                removed_entries.append({'partition': part, 'path': path})
                continue
            if entry['file_type'] == 'RegularFile':
                source = 'stock-tree/' + part + path
                full_source = ROOT / source
                if path.endswith('.xml') and '/etc/' in path:
                    try:
                        raw = full_source.read_bytes()
                        if any(p.encode() in raw for p in removed):
                            root = ET.fromstring(raw)

                            def matches(node):
                                return any(v in removed for v in node.attrib.values()) or (node.text or '').strip() in removed

                            count = [0]

                            def prune(parent):
                                for child in list(parent):
                                    identity_record = (
                                        child.tag == 'app' and any(
                                            node.tag == 'name' and matches(node) for node in child
                                        )
                                    ) or (
                                        child.tag == 'policy' and any(
                                            node.tag == 'app' and matches(node) for node in child
                                        )
                                    )
                                    if matches(child) or identity_record:
                                        parent.remove(child)
                                        count[0] += 1
                                    else:
                                        prune(child)

                            if matches(root):
                                removed_entries.append({'partition': part, 'path': path, 'reason': 'dedicated removed-package configuration'})
                                continue
                            prune(root)
                            if count[0]:
                                target = ROOT / 'assets' / 'config' / part / path.lstrip('/')
                                target.parent.mkdir(parents=True, exist_ok=True)
                                ET.ElementTree(root).write(target, encoding='utf-8', xml_declaration=True)
                                source = target.relative_to(ROOT).as_posix()
                                changed_xml.append({'partition': part, 'path': path, 'removed_nodes': count[0]})
                    except ET.ParseError as e:
                        raise ValueError(f'Cannot safely edit {full_source}: {e}') from e
                source = overrides.get(part + path, source)
                resolved = (ROOT / source).resolve()
                if not resolved.is_relative_to(ROOT) or not resolved.is_file():
                    raise ValueError(f'Invalid input source: {source}')
                text = re.sub(r'(?m)^source\s*=.*\n?', '', text)
                text = '\nsource = ' + json.dumps(source) + '\n' + text.lstrip('\n')
            output.append('[[entries]]\n' + text)
        outpath = ROOT / f'{part}.lean.toml'
        outpath.write_text(''.join(output), encoding='utf-8')
        rebuilt = tomllib.loads(outpath.read_text())
        paths = {e['path'] for e in rebuilt['entries']}
        if len(paths) != len(rebuilt['entries']):
            raise ValueError('Duplicate filesystem entry')
        for e in rebuilt['entries']:
            if e['path'] != '/' and str(PurePosixPath(e['path']).parent) not in paths:
                raise ValueError(f'Missing parent for {e["path"]}')
        # All retained entries retain their original inode metadata. The only
        # field that may change is the host-side regular-file source reference.
        original = {e['path']: e for e in parsed['entries']}
        for e in rebuilt['entries']:
            a = {k:v for k,v in original[e['path']].items() if k != 'source'}
            b = {k:v for k,v in e.items() if k != 'source'}
            if a != b:
                raise ValueError(f'Unexpected metadata change: {part}{e["path"]}')

    report = dict(name=recipe['name'], status=recipe['status'],
                  removed_packages=recipe['remove_packages'], removed_apks=removed_apks,
                  removed_apk_bytes=sum(a['bytes'] for a in removed_apks),
                  removed_entries=removed_entries, edited_xml=changed_xml,
                  asset_overrides=overrides, protected_packages=sorted(keep),
                  remaining_branding=recipe['remaining_branding'], deferred=recipe['defer_packages'],
                  metadata_preserved=True, images=[])
    outdir = ROOT / 'output'
    outdir.mkdir(exist_ok=True)
    (ROOT / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'Removed {len(removed)} packages ({len(removed_apks)} APKs); {report["removed_apk_bytes"]/1024**2:.1f} MiB APK bytes; {len(changed_xml)} configuration edits', flush=True)
    if args.pack:
        subprocess.run([sys.executable, str(ROOT / 'compress_images.py')], check=True)


if __name__ == '__main__':
    main()
