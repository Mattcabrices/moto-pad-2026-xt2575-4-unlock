#!/bin/sh
set -eu
cd "$(dirname "$0")"
if command -v sha256sum >/dev/null 2>&1; then
    check_hashes() { sha256sum -c "$1"; }
elif command -v shasum >/dev/null 2>&1; then
    check_hashes() { shasum -a 256 -c "$1"; }
else
    echo 'Install sha256sum or shasum before reassembly.' >&2
    exit 1
fi
check_hashes DOWNLOAD-SHA256SUMS.txt
if [ ! -e system_a.travel-lean.UNSIGNED.img ]; then
    cat system_a.travel-lean.UNSIGNED.img.part01 \
        system_a.travel-lean.UNSIGNED.img.part02 \
        system_a.travel-lean.UNSIGNED.img.part03 > system_a.travel-lean.UNSIGNED.img
fi
check_hashes SHA256SUMS.txt
echo 'All four images verified. No flashing or device changes were performed.'
