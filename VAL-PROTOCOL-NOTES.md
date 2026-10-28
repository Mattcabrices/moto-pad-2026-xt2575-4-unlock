# How Val Protocol was adapted for the XT2575-4

This is the technical explanation of what "making Val Protocol work for this
device" means. The upstream serial presets do not apply; Val's container,
repack, certification and verification tooling does.

## 1. Why the stock presets fail

Val's presets are pattern-based. They expect a Motorola unlock flow containing:

- an FRP/OEM checker call,
- a key-validator function,
- unlock erase calls, and
- a runtime serial getter used by that validator.

The XT2575-4 LK (`17.5.10.020`) has a different implementation. Val's analyzer
on the extracted payload reported:

```text
FRP checkers : 0
KEY validators: 0
Erase permission checks: 0
Partition erase ops: 0
```

`fastboot oem unlock` checks an `Sn Image Auth` flag at
`0xffff000051012870`. The flag is set by `validate_unlock_image`
(`0xffff000050f0b514`) after a vendor-signed unlock image passes its signature
and device-serial checks. If the flag is zero, the handler branches to
`ERROR: Sn Image Auth fail`.

## 2. The actual gate

In the LK payload, `fastboot oem unlock` is at offset `0x9744`
(`0xffff000050f09744`):

```asm
0xffff000050f09758  ldr  w8, [x8, #0x870]   ; Sn Image Auth flag
0xffff000050f0975c  cbz  w8, #0xffff000050f098d4  ; zero -> auth failure
...
0xffff000050f09838  ; volume-key confirmation
0xffff000050f09868  bl   set_lock_state        ; set_lock_state(0)
```

Removing that one branch is sufficient. The handler still:

- prints the unlock warnings,
- waits for Volume Up/Down confirmation,
- refuses if the device is already unlocked,
- calls `set_lock_state(0)`,
- handles writer errors and returns to fastboot.

It never reads the command argument.

## 3. The patch

| Item | Value |
| --- | --- |
| Payload offset | `0x975c` |
| Virtual address | `0xffff000050f0975c` |
| Before | `c80b0034` — `cbz w8, #0xffff000050f098d4` |
| After | `1f2003d5` — `nop` |
| Changed payload bytes | 4 |
| Stock payload SHA-256 | `10008c0ab880bd5bd5979e4299e3c06e34768d93a9a073e28f13488e0c0fee46` |
| Patched payload SHA-256 | `95462aa5ba178ac1217f3d0a3271d2b568b8dd9a8460fcfa15ec7b7c346717cc` |
| Patched image SHA-256 | `81ee5de950470c9e31552135349589e8b056a4312f93419930a9502f4bbbd034` |

Only the `lk` payload and `cert2` component differ from the official image.

## 4. Val's pipeline that is still used

1. **Extract** the `lk` subimage from the official Motorola container. Val's
   `liblk` parser handles the multi-image layout.
2. **Patch** the payload in place (the 4 bytes above).
3. **Repack** with `lk_repack_signed.py`:
   - `sign_mtk_cert.py -w --legacy` adds the CERT2 hash override and updates the
     CERT2 `dsize`,
   - `build-part-img.py replace` writes the patched signed block back into the
     original container.
4. **Verify** with `verify_mtk_image.py -n lk`. Expected result:

   ```text
   CERT1 signature: OK
   CERT2 signature: OK
   Image header hash: OK
   Image data hash: OK
   Result: VALID
   ```

   This verifies the certificate structure and hashes. It does not prove the
   tablet's boot ROM/preloader will accept the image; only hardware flash and
   boot does that.

The build script in the development workspace is `build_tablet_unlock.py`. It
performs these steps with stock-hash and guard-byte checks and writes the build
manifest. The published artifact and `MANIFEST.json` record the exact result.

## 5. Hardware delivery

The tested sequence:

```text
fastboot getvar product          # sycamore_row_5G
fastboot getvar current-slot     # a
fastboot getvar flash_lock       # no
fastboot getvar unlocked         # no
fastboot flash lk_a lk.oem-unlock-gate.17.5.10.020.img
fastboot reboot-bootloader
fastboot getvar version-bootloader
# sycamore_row_5G_27256d543_202609231741
fastboot oem unlock
```

The unlock handler requires Volume Up/Down confirmation within about five
seconds. **Tap** the volume key repeatedly; holding it before the command did
not register in testing. Successful output:

```text
(bootloader) Start unlock flow
(bootloader) unlock success
OKAY
```

Final state: `unlocked: yes`; Android `ro.boot.flash.locked=0`,
`ro.boot.verifiedbootstate=orange`.

`lk_b` was never written and no slot switch occurred.

## 6. Limits

- One XT2575-4 unit, slot `a`, `flash_lock: no`, build `17.5.10.017`, patched
  from the official `17.5.10.020` factory LK.
- Not tested on other models, builds, slots, or flash-lock states.
- CERT2 hash-override acceptance is hardware- and boot-chain-dependent. A
  modified LK that fails this check can leave the tablet unable to reach
  fastboot.
- Keep the official factory package (SP Flash Tool V6, `da.auth`, `DA_BR.bin`,
  scatter, stock images) for recovery. Recovery was not exercised on this unit.
