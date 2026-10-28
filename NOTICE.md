# Credits and legal notice

## Val Protocol

This build would not exist without **Val Protocol**, by **Maikyxd**:

- Repository: <https://github.com/Maikyxd/val-protocol>
- Tested revision: `dc7f41f9b1a32da1a78ef327bb62d2bef17d7bd0`
- License: GNU Affero General Public License v3.0 (AGPL-3.0)

Val Protocol supplied the LK container handling, CERT2 hash-update/repack flow,
and the `verify_mtk_image.py` verification used to produce and validate
`lk.oem-unlock-gate.17.5.10.020.img`. All credit for that tooling belongs to its
author and contributors. Val Protocol is licensed AGPL-3.0. This repository does
not redistribute its source code; obtain it from the upstream repository.

Val Protocol credits prior public Motorola/MTK LK research and tooling:

- kasnria001/pwnage24mtk
- R0rt1z2/liblk
- R0rt1z2/lkpatcher

## Hardware validation

**Matt Cabrices** — device owner, hardware testing, and validation. The patched
LK was flashed to `lk_a`, booted, and the bootloader was unlocked on the tested
XT2575-4 unit. Serial numbers are intentionally omitted from this repository.

## Firmware source

The patched image is derived from the official Motorola/Lenovo XT2575-4
`17.5.10.020` factory firmware (`lk.img`), supplied by the device owner's
factory package. No production vendor signing keys, unlock tokens, or
device-unique secrets are added. The image preserves the stock firmware's own
embedded key material.

Motorola, Lenovo, Moto, and related marks are trademarks of their respective
owners. This project is not affiliated with or endorsed by Motorola, Lenovo, or
MediaTek.

## Legal and ethical use

- Use only on hardware you own or are explicitly authorized to service.
- Unlocking may erase all data, void the warranty, and affect carrier or
  enterprise terms.
- Firmware redistribution may be restricted in some jurisdictions. The image is
  provided for repair, interoperability research, and personal device recovery.
- Do not use this work to access a device you do not own or to bypass another
  person's security or account controls.
- You are responsible for complying with local law, warranty terms, and
  contracts that apply to your device.

## No warranty

The files and instructions are provided “as is”, without warranty of any kind,
express or implied, including but not limited to merchantability, fitness for a
particular purpose, and non-infringement. The authors are not liable for data
loss, device damage, bricking, warranty voiding, or any other damages arising
from use of this material. Bootloader modification is inherently risky; see
[SAFETY.md](SAFETY.md).
