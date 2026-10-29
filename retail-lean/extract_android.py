"""Read-only sparse-super inspector/extractor. Output is confined to this project.

Format reference: tools/lp-metadata-format.h (AOSP liblp).
Only system/product/system_ext images may be extracted; source is never changed.
"""
import argparse
import bisect
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parent


class SparseReader:
    def __init__(self, path):
        self.f = path.open('rb')
        magic, major, minor, fh, ch, bs, blocks, count, crc = struct.unpack('<IHHHHIIII', self.f.read(28))
        if magic != 0xED26FF3A or major != 1 or fh < 28 or ch < 12:
            raise ValueError('Unsupported sparse header')
        self.size = blocks * bs
        self.chunks = []
        logical = 0
        self.f.seek(fh)
        for _ in range(count):
            header = self.f.read(ch)
            kind, _, nblocks, total = struct.unpack_from('<HHII', header)
            length = nblocks * bs
            payload = self.f.tell()
            if kind == 0xCAC1:
                if total != ch + length:
                    raise ValueError('Bad raw chunk length')
                fill = None
            elif kind == 0xCAC2:
                if total != ch + 4:
                    raise ValueError('Bad fill chunk')
                fill = self.f.read(4)
            elif kind == 0xCAC3:
                if total != ch:
                    raise ValueError('Bad empty chunk')
                fill = b'\0' * 4
            elif kind == 0xCAC4:
                if length or total != ch + 4:
                    raise ValueError('Bad CRC chunk')
                self.f.seek(payload + 4)
                continue
            else:
                raise ValueError(f'Unknown sparse chunk {kind:x}')
            if length:
                self.chunks.append((logical, length, payload, fill))
            logical += length
            self.f.seek(payload + total - ch)
        if logical != self.size or self.f.tell() != path.stat().st_size:
            raise ValueError('Sparse size mismatch')
        self.starts = [x[0] for x in self.chunks]

    def read(self, offset, length):
        if offset < 0 or length < 0 or offset + length > self.size:
            raise ValueError('Out-of-bounds read')
        result = bytearray()
        while length:
            index = bisect.bisect_right(self.starts, offset) - 1
            start, size, physical, fill = self.chunks[index]
            delta = offset - start
            n = min(length, size - delta)
            if n <= 0:
                raise ValueError('Sparse gap')
            if fill is None:
                self.f.seek(physical + delta)
                data = self.f.read(n)
                if len(data) != n:
                    raise ValueError('Truncated source')
            else:
                data = (fill * ((n + 7) // 4))[delta % 4:delta % 4 + n]
            result.extend(data)
            length -= n
            offset += n
        return bytes(result)


def sha_check(data, offset, expected):
    data = bytearray(data)
    data[offset:offset + 32] = b'\0' * 32
    if hashlib.sha256(data).digest() != expected:
        raise ValueError('Metadata checksum mismatch')


def inspect(reader):
    geom = reader.read(4096, 52)
    magic, size = struct.unpack_from('<II', geom)
    if magic != 0x616C4467 or size != 52:
        raise ValueError('Bad LP geometry')
    sha_check(geom, 8, geom[8:40])
    max_size, slots, block_size = struct.unpack_from('<III', geom, 40)
    prefix = reader.read(12288, 128)
    magic, major, minor, hsize = struct.unpack_from('<IHHI', prefix)
    if magic != 0x414C5030 or major != 10 or minor > 2 or not 128 <= hsize <= max_size:
        raise ValueError('Unsupported LP header')
    header = reader.read(12288, hsize)
    sha_check(header, 12, header[12:44])
    tsize = struct.unpack_from('<I', header, 44)[0]
    if hsize + tsize > max_size:
        raise ValueError('LP tables too large')
    tables = reader.read(12288 + hsize, tsize)
    if hashlib.sha256(tables).digest() != header[48:80]:
        raise ValueError('LP table checksum mismatch')

    def table(offset, minimum):
        off, count, stride = struct.unpack_from('<III', header, offset)
        if stride < minimum or off + count * stride > len(tables):
            raise ValueError('Bad table descriptor')
        return [tables[off+i*stride:off+(i+1)*stride] for i in range(count)]

    devices = table(116, 64)
    if len(devices) != 1:
        raise ValueError('Only single-device super supported')
    extents = [struct.unpack_from('<QIQI', row) for row in table(92, 24)]
    partitions = []
    for row in table(80, 52):
        name = row[:36].split(b'\0')[0].decode('ascii')
        if not re.fullmatch(r'[A-Za-z0-9_]+', name):
            raise ValueError('Invalid partition name')
        attr, first, count, group = struct.unpack_from('<IIII', row, 36)
        if first + count > len(extents):
            raise ValueError('Bad extent indexes')
        selected = extents[first:first+count]
        for sectors, kind, target, source in selected:
            if kind not in (0, 1) or source != 0 or (kind == 0 and (target + sectors) * 512 > reader.size):
                raise ValueError('Unsupported/out-of-range extent')
        partitions.append(dict(name=name, attributes=attr, group=group,
                               size=sum(e[0]*512 for e in selected), extents=selected))
    return dict(metadata_checksums_valid=True, version=f'{major}.{minor}',
                logical_size=reader.size, metadata_slots=slots,
                logical_block_size=block_size, partitions=partitions)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('--extract', nargs='*', default=[])
    args = parser.parse_args()
    allowed = {'system_a', 'product_a', 'system_ext_a'}
    if not set(args.extract) <= allowed:
        raise ValueError(f'Only Android customization partitions allowed: {allowed}')
    reader = SparseReader(args.source)
    info = inspect(reader)
    info['source'] = str(args.source)
    images = ROOT / 'stock-images'
    images.mkdir(exist_ok=True)
    found = set()
    for part in info['partitions']:
        print(part['name'], part['size'], flush=True)
        if part['name'] not in args.extract:
            continue
        found.add(part['name'])
        output = images / (part['name'] + '.img')
        digest = hashlib.sha256()
        with output.open('xb') as out:
            for sectors, kind, target, source in part['extents']:
                remaining = sectors * 512
                offset = target * 512
                while remaining:
                    n = min(8 * 1024 * 1024, remaining)
                    data = reader.read(offset, n) if kind == 0 else b'\0' * n
                    out.write(data)
                    digest.update(data)
                    offset += n
                    remaining -= n
        part['extracted_sha256'] = digest.hexdigest()
        part['extracted_path'] = str(output)
    if found != set(args.extract):
        raise ValueError(f'Missing partitions: {set(args.extract) - found}')
    (ROOT / 'super-inventory.json').write_text(json.dumps(info, indent=2) + '\n')


if __name__ == '__main__':
    main()
