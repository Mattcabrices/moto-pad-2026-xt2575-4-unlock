"""Pack the metadata recipe as PAX tar, then create LZ4HC EROFS images.

Uses the same LIBARCHIVE.xattr encoding as AFSR's create_tarball_erofs.
The separate formatter is required because AFSR v2 does not enable compression
and its bundled formatter rejects -z in this release.
"""
import base64
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import tomllib
from urllib.parse import quote_from_bytes

ROOT = Path(__file__).resolve().parent
MKFS = Path(os.environ.get('MKFS_EROFS', 'mkfs.erofs.exe' if os.name == 'nt' else 'mkfs.erofs'))
PARTS = {'system': 'system_a', 'product': 'product_a', 'system_ext': 'system_ext_a'}


def binary_string(value):
    result = bytearray()
    previous = 0
    for match in re.finditer(r'\\(x[0-9a-fA-F]{2}|0|\\)', value):
        literal = value[previous:match.start()]
        if '\\' in literal:
            raise ValueError(f'Unexpected byte-string escape: {value!r}')
        result.extend(literal.encode('utf-8'))
        token = match.group(1)
        result.extend(bytes([int(token[1:],16)]) if token.startswith('x') else b'\0' if token == '0' else b'\\')
        previous = match.end()
    tail = value[previous:]
    if '\\' in tail:
        raise ValueError(f'Unexpected byte-string escape: {value!r}')
    result.extend(tail.encode('utf-8'))
    return bytes(result)


def pack_one(part, name):
    doc = tomllib.loads((ROOT / f'{part}.lean.toml').read_text())
    meta = doc['metadata']
    candidate_dir = ROOT / 'output' / 'candidates'
    candidate_dir.mkdir(exist_ok=True)
    output = candidate_dir / f'{name}.travel-lean.UNSIGNED.img'
    tarpath = candidate_dir / f'{part}.metadata-preserved.tar'
    if output.exists() or tarpath.exists():
        raise ValueError(f'Refusing to overwrite existing output for {part}')
    print(f'Preparing {part} PAX archive...', flush=True)
    with tarfile.open(tarpath, 'w', format=tarfile.PAX_FORMAT) as archive:
        for entry in doc['entries']:
            info = tarfile.TarInfo(entry['path'])
            info.mode = int(entry.get('file_mode','000'), 8)
            info.uid = entry.get('uid',0)
            info.gid = entry.get('gid',0)
            mtime = datetime.fromisoformat(entry.get('mtime','1970-01-01T00:00:00Z')).timestamp()
            info.mtime = int(mtime)
            info.pax_headers = {'path':entry['path'], 'mtime':str(mtime)}
            for key,value in entry.get('xattrs',{}).items():
                encoded_key = quote_from_bytes(binary_string(key), safe='')
                info.pax_headers['LIBARCHIVE.xattr.' + encoded_key] = base64.b64encode(binary_string(value)).decode('ascii')
            kind = entry['file_type']
            if kind == 'RegularFile':
                source = (ROOT / entry['source']).resolve()
                if not source.is_relative_to(ROOT):
                    raise ValueError('Source outside project')
                info.type = tarfile.REGTYPE
                info.size = source.stat().st_size
                with source.open('rb') as f:
                    archive.addfile(info, f)
            else:
                info.type = {'Directory':tarfile.DIRTYPE, 'Symlink':tarfile.SYMTYPE,
                             'CharDevice':tarfile.CHRTYPE, 'BlockDevice':tarfile.BLKTYPE,
                             'Fifo':tarfile.FIFOTYPE}[kind]
                if kind == 'Symlink':
                    info.linkname = entry['symlink_target']
                    info.pax_headers['linkpath'] = info.linkname
                info.devmajor = entry.get('device_major',0)
                info.devminor = entry.get('device_minor',0)
                archive.addfile(info)
    timestamp = int(datetime.fromisoformat(meta['creation_time']).timestamp())
    command = [str(MKFS), '-zlz4hc,level=9', '-b4096', '-C4096',
               '-T'+str(timestamp), '--mkfs-time', '--preserve-mtime',
               '-U'+meta['uuid'], '-Exattr-name-filter', '--tar=f',
               output.as_posix(), tarpath.as_posix()]
    print(f'Compressing {part} with LZ4HC...', flush=True)
    with (candidate_dir / f'{part}.pack.log').open('w') as log:
        subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT)
    with output.open('rb') as f:
        sha = hashlib.file_digest(f, 'sha256').hexdigest()
    # Delete only this script's completed intermediate, after verifying its path.
    if tarpath.resolve().parent != candidate_dir.resolve():
        raise ValueError('Unexpected intermediate path')
    tarpath.unlink()
    return dict(path=str(output), bytes=output.stat().st_size, sha256=sha)


def main():
    images = [pack_one(part,name) for part,name in PARTS.items()]
    report = json.loads((ROOT / 'build-report.json').read_text())
    report['uncompressed_intermediate_images'] = report['images']
    report['images'] = images
    report['compression'] = 'LZ4HC level 9, 4096-byte filesystem/physical clusters'
    (ROOT / 'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Compressed candidates complete; round-trip validation required.',flush=True)


if __name__ == '__main__':
    main()
