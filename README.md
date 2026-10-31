# Moto Pad 2026 (XT2575-4) Bootloader Unlock — Val Protocol build

## Lean OEM Android build

The [Moto Pad OEM Retail Lean build](retail-lean/README.md) removes unwanted preloads while retaining the OEM tablet features. See the [download and installation release](https://github.com/Mattcabrices/moto-pad-2026-xt2575-4-unlock/releases/tag/oem-retail-lean-v1) for verified images, supported baseline, owner testing and restore instructions.


**STOP AND READ [SAFETY.md](SAFETY.md) FIRST.** Bootloader modification can
permanently brick the tablet. Unlocking erases all user data. Use this only on
hardware you own or are explicitly authorized to service.

## Tested result

- Device: Motorola Moto Pad 2026 **XT2575-4**, product `sycamore_row_5G`
- Active slot: **a**
- Installed Android: `XT2575-4_ROW_OPEN_USER_M1317.3_W_ZUI_17.5.10.017_ST`
- LK source: official `17.5.10.020` factory package
- Bootloader after flash: `sycamore_row_5G_27256d543_202609231741`
  (before: `sycamore_row_5G_27256d543_202607101822`)
- `fastboot oem unlock`: `Start unlock flow` → `unlock success` → `OKAY`
- Final state: `unlocked: yes`; Android `ro.boot.flash.locked=0`,
  `ro.boot.verifiedbootstate=orange`
- Original maintainer hardware validation: **one unit**. The device serial is intentionally omitted.
- An additional XT2575-4 owner reports a successful unlock and subsequent root.
  See [community success reports](SUCCESS-REPORTS.md) for attribution, configuration,
  observed differences and evidence limits. This is not an additional retail-ROM test.

## What this is

`lk.oem-unlock-gate.17.5.10.020.img` is a full LK partition image built from the
official XT2575-4 17.5.10.020 factory firmware.

- Patch: `0x975c` in the LK payload (`0xffff000050f0975c`),
  `cbz w8, auth_fail` (`c80b0034`) → `nop` (`1f2003d5`).
- Effect: skips the `Sn Image Auth` guard in the `fastboot oem unlock` handler.
  The handler keeps its volume-key confirmation, lock-state check and
  `set_lock_state(0)` path.
- Repack: Val Protocol's CERT2 hash-override flow. CERT1/CERT2 signatures remain
  valid, the image hash matches, and every container component except `lk` and
  `cert2` is byte-identical to the official image.
- The `.bin` file is the patched LK payload for reference and hash comparison.

This is **not** a universal exploit. It depends on the tablet accepting the
modified LK and on `flash_lock: no`. Only the configuration above was tested.

**No serial-derived unlock key is used.** The XT2575-4 `oem unlock` handler
ignores the command argument; the unlock is enabled by the authorization-gate
patch alone.

## Files

| File | Purpose |
| --- | --- |
| `lk.oem-unlock-gate.17.5.10.020.img` | Patched LK partition image (flash this) |
| `lk.oem-unlock-gate.17.5.10.020.bin` | Patched LK payload (reference) |
| `MANIFEST.json` | Build, hash, patch and hardware-result record |
| `SAFETY.md` | Mandatory preflight and recovery checklist |
| `VAL-PROTOCOL-NOTES.md` | Technical adaptation notes and reproduction details |
| `NOTICE.md` | Credits and legal notice |
| `SHA256SUMS.txt` | Hashes for every published file |

## Verified hashes

```text
81ee5de950470c9e31552135349589e8b056a4312f93419930a9502f4bbbd034  lk.oem-unlock-gate.17.5.10.020.img
95462aa5ba178ac1217f3d0a3271d2b568b8dd9a8460fcfa15ec7b7c346717cc  lk.oem-unlock-gate.17.5.10.020.bin
e74a2e9808ec0ce016453acf02920ce9ddc32807dc3e2ec32c680f8922a59c98  stock container (17.5.10.020 lk.img)
10008c0ab880bd5bd5979e4299e3c06e34768d93a9a073e28f13488e0c0fee46  stock LK payload
```

Verify before flashing:

```powershell
Get-FileHash .\lk.oem-unlock-gate.17.5.10.020.img -Algorithm SHA256
# or
certutil -hashfile lk.oem-unlock-gate.17.5.10.020.img SHA256
```

## Prerequisites

- Windows PC with Android platform-tools (`adb.exe`, `fastboot.exe`)
- Good USB cable, stable USB port, tablet charged
- The official XT2575-4 17.5.10.020 factory package for recovery
  (`SPFlashToolV6.exe`, `da.auth`, `DA_BR.bin`, scatter, stock `lk.img`)
- Acceptance that unlocking **wipes all user data** and may **void warranty**

## Step 1 — Preflight (read-only)

Connect the tablet, enable USB debugging if needed, then:

```text
adb devices
adb reboot bootloader
fastboot devices
fastboot getvar product
fastboot getvar current-slot
fastboot getvar unlocked
fastboot getvar flash_lock
```

Expected on the tested configuration:

```text
product: sycamore_row_5G
current-slot: a
unlocked: no
flash_lock: no
```

**Abort if product is not `sycamore_row_5G`, the active slot is not `a`, or
`flash_lock` is not `no`.**

Do **not** run `fastboot oem device-info` or `fastboot getvar version-baseband`
on this bootloader. Both wedged the USB endpoint during testing. If `getvar`
starts timing out, power-cycle the tablet: unplug USB, hold **Power + Volume
Down** for 10–15 seconds, boot Android, reconnect, then `adb reboot bootloader`.

## Step 2 — Flash the patched LK to lk_a only

```text
fastboot flash lk_a lk.oem-unlock-gate.17.5.10.020.img
```

Expected:

```text
Sending 'lk_a' (2845 KB)                           OKAY
Writing 'lk_a'                                     OKAY
Finished.
```

If the flash is rejected, **stop**. A rejection is non-destructive.

Then reboot the bootloader and prove the new LK starts:

```text
fastboot reboot-bootloader
fastboot getvar version-bootloader
```

Expected: `sycamore_row_5G_27256d543_202609231741`.

If fastboot does not come back, **do not keep retrying**. Go to Recovery.

## Step 3 — Unlock

```text
fastboot oem unlock
```

The tablet shows the unlock warning. **Tap Volume Up and Volume Down
alternately, rapidly, during the ~5-second window.** Holding a key before the
command did not register on the tested unit; tapping did.

Expected:

```text
(bootloader) Start unlock flow
(bootloader) unlock success
OKAY
```

## Step 4 — Verify

```text
fastboot getvar unlocked
# yes

fastboot reboot
```

After Android starts:

```text
adb shell getprop ro.boot.flash.locked
# 0
adb shell getprop ro.boot.verifiedbootstate
# orange
```

The orange bootloader-unlocked warning at startup is normal. User data was
erased; complete Android setup again.

## Aftercare

- Do **not** relock the bootloader.
- Do **not** write `lk_b`; only slot `a` was tested.
- Do **not** run a full stock flashing script as “cleanup” unless you have a
  tested recovery path.
- Keep the stock `.020` factory package and a copy of the original `lk.img`.

## Recovery

1. **fastboot still works:** reflash the stock LK from the factory package:
   `fastboot flash lk_a <stock-lk.img>`, then reboot the bootloader.
2. **No fastboot:** use the factory **SP Flash Tool V6** package with
   `Flash.cmd` / `da.auth` / `DA_BR.bin` in BROM/Preloader mode. This is the
   intended factory recovery path, but it was **not tested on this unit** in
   this project. Follow the package's own instructions and do not interrupt it.
3. **Flash rejected:** stop; the tablet was not modified.

## How it was built

1. Extracted the `lk` subimage from the official 17.5.10.020 `lk.img`.
2. Verified stock payload SHA-256 and the guard bytes at `0x975c`.
3. Replaced the guard branch with `nop`; no other payload bytes changed.
4. Repacked with Val Protocol's `lk_repack_signed.py` (`--legacy` CERT2 update).
5. Verified with `verify_mtk_image.py -n lk` → `Result: VALID`.
6. Independent container check: only `lk` and `cert2` differ; all other
   components byte-identical. Offline handler emulation: 7/7 tests passed.

The repack and verification commands (from the Val Protocol checkout):

```text
python lk_repack_signed.py \
  --original-image lk.stock-17.5.10.020.img \
  --patched-lk-bin lk.oem-unlock-gate.17.5.10.020.bin \
  --output lk.oem-unlock-gate.17.5.10.020.img

python tools/verify_mtk_image.py \
  lk.oem-unlock-gate.17.5.10.020.img -n lk
```

The stock `lk.img` is not redistributed here; use the official 17.5.10.020
factory package to reproduce the build.

## Credits

- **Val Protocol** — Maikyxd — <https://github.com/Maikyxd/val-protocol>
  (tested against commit `dc7f41f9b1a32da1a78ef327bb62d2bef17d7bd0`).
  Val Protocol is licensed AGPL-3.0. The repack, CERT2 update and verification
  pipeline used here comes from that project. Its source is not redistributed
  here; obtain it from the upstream repository.
- Upstream projects credited by Val Protocol:
  - kasnria001/pwnage24mtk
  - R0rt1z2/liblk
  - R0rt1z2/lkpatcher
- **Matt Cabrices** — device owner, hardware testing, and validation.
- Motorola/Lenovo factory firmware was used as the base. The image preserves the
  stock firmware's own embedded key material; no production vendor signing
  keys, unlock tokens, or device-unique secrets are added.

See [NOTICE.md](NOTICE.md) for the full notice.

## Disclaimer

Provided as-is, without warranty of any kind. You are responsible for complying
with warranty, carrier, and local law. Bootloader modification can brick the
device and erase all data. Only use on hardware you own or are authorized to
service.
