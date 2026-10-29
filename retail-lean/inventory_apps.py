"""Inventory APK manifests without executing code from the firmware."""
import csv
import json
from pathlib import Path
import struct
import zipfile

ROOT = Path(__file__).resolve().parent


def manifest_info(data):
    strings = []
    result = {'package': None, 'version': None, 'label': None}
    off = 8
    while off + 8 <= len(data):
        kind, hsize, size = struct.unpack_from('<HHI', data, off)
        if size < hsize or size < 8 or off + size > len(data):
            raise ValueError('Invalid binary XML chunk')
        if kind == 1:
            count, styles, flags, start, _ = struct.unpack_from('<IIIII', data, off + 8)
            offsets = struct.unpack_from(f'<{count}I', data, off + hsize)
            strings = []
            for pos in offsets:
                p = off + start + pos
                if flags & 0x100:
                    # Skip UTF-16 character count, then decode UTF-8 byte count.
                    p += 2 if data[p] & 0x80 else 1
                    n = data[p]
                    p += 1
                    if n & 0x80:
                        n = ((n & 0x7f) << 8) | data[p]
                        p += 1
                    strings.append(data[p:p+n].decode('utf-8'))
                else:
                    n = struct.unpack_from('<H', data, p)[0]
                    p += 2
                    if n & 0x8000:
                        n = ((n & 0x7fff) << 16) | struct.unpack_from('<H', data, p)[0]
                        p += 2
                    strings.append(data[p:p+2*n].decode('utf-16le'))
        elif kind == 0x102:
            name_index = struct.unpack_from('<I', data, off + 20)[0]
            attr_start, attr_size, count = struct.unpack_from('<HHH', data, off + 24)
            element = strings[name_index]
            for i in range(count):
                p = off + 16 + attr_start + i*attr_size
                ns, name, raw = struct.unpack_from('<III', data, p)
                value_type = data[p+15]
                value_data = struct.unpack_from('<I', data, p+16)[0]
                value = strings[raw] if raw != 0xffffffff else (
                    strings[value_data] if value_type == 3 else f'@0x{value_data:08x}')
                key = strings[name]
                if element == 'manifest' and key == 'package':
                    result['package'] = value
                elif element == 'manifest' and key == 'versionName':
                    result['version'] = value
                elif element == 'application' and key == 'label':
                    result['label'] = value
        off += size
    if not result['package']:
        raise ValueError('No manifest package')
    return result


def main():
    rows = []
    for path in sorted((ROOT / 'stock-tree').rglob('*.apk')):
        row = dict(path=path.relative_to(ROOT / 'stock-tree').as_posix(), bytes=path.stat().st_size)
        try:
            with zipfile.ZipFile(path) as apk:
                row.update(manifest_info(apk.read('AndroidManifest.xml')))
        except Exception as e:
            row['error'] = str(e)
        rows.append(row)
    (ROOT / 'apps.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
    with (ROOT / 'apps.csv').open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['package', 'label', 'version', 'bytes', 'path', 'error'])
        writer.writeheader()
        writer.writerows(rows)
    print(f'APKs: {len(rows)}; manifest errors: {sum("error" in r for r in rows)}')
    for row in rows:
        if any(word in row['path'].lower() + ' ' + str(row.get('package', '')).lower()
               for word in ['metro', 'tmobile', 't-mobile', 'facebook', 'meta.', 'amazon', 'netflix', 'launcher']):
            print(row)


if __name__ == '__main__':
    main()
