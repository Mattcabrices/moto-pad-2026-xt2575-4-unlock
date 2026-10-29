# Installation: tested Android-only scope

For an **already-unlocked XT2575-4**, active slot **a**, using the working
XT2575-4 **17.5.10.020 kernel/vendor/boot baseline**. One unit was tested.
Have matching stock .020 Android images and original vbmeta available locally
before changing the OS. Back up local files and accounts first: a factory reset
was required on the tested unit and erases local data.

## 1. Download and verify

Download all three system image parts, product image, system_ext image,
vbmeta-020.custom-os-flags3.img, BUILD-MANIFEST.json and a reassembly script.
Run `powershell -File .\reassemble.ps1` on Windows, or `sh reassemble.sh`
on Linux. The scripts verify parts and final image hashes; they do not flash.
Do not flash a `.partNN` file.

## 2. Flash the three Android filesystems in fastbootd

Enter Recovery and select Enter fastboot, or from Android with USB debugging:

```text
adb reboot fastboot
fastboot getvar product
fastboot getvar is-userspace
fastboot getvar unlocked
fastboot getvar current-slot
fastboot getvar vendor-fingerprint
```

Check product **XT2575-4**, userspace **yes**, unlocked **yes**, active slot
**a**, and the .020 vendor baseline. Stop on a mismatch or a failed/blank
query; listing a USB serial alone does not establish a working connection.

```text
fastboot flash system_a system_a.travel-lean.UNSIGNED.img
fastboot flash product_a product_a.travel-lean.UNSIGNED.img
fastboot flash system_ext_a system_ext_a.travel-lean.UNSIGNED.img
```

Require successful writes for every chunk. Stop on any failure; do not reboot
with a partially completed installation.

## 3. Apply the custom-OS verification settings in bootloader fastboot

```text
fastboot reboot bootloader
fastboot getvar product
fastboot getvar is-userspace
fastboot getvar unlocked
fastboot getvar current-slot
```

Now check product **sycamore_row_5G**, userspace **no**, unlocked **yes**,
slot **a**. The tested device exposed vbmeta_a only in bootloader fastboot.
The next file already has flags 3: applying it disables verification/verity
for the custom OS and is a persistent reduction in boot-integrity protection.

```text
fastboot flash vbmeta_a vbmeta-020.custom-os-flags3.img
fastboot reboot
```

No bootloader, preloader, kernel, vendor, modem, partition-table, slot-change
or relock command belongs to this installation. In particular, do not flash
LK merely to install these Android images.

USB sometimes stopped responding after mode changes on the test PC. Leaving
the correct mode open and unplugging/reconnecting USB restored communication.
Stop the failed host command and recheck identity/mode before retrying. Small
metadata writes succeeded with the fastboot 35.0.2 client bundled with Software
Fix after transfers failed with the PC's other client; this is an observed
session result, not a claim that one version fixes every USB problem.

## 4. Clean initial setup

On the tested unit the first boot returned to Recovery. **Wipe data/factory
reset -> Factory data reset -> Reboot system now** then allowed normal Android
setup. This erases local apps, accounts and files. Do not treat it as a proven
fix for every boot failure. Confirm the actual screen and preserve any useful
logs before further recovery work.

## Stock Android rollback

Restore matching original **XT2575-4 .020** system_a, product_a and system_ext_a
in fastbootd, then its original unmodified vbmeta_a in bootloader fastboot.
The original vbmeta restores normal verification settings for matching stock
images. Keep the separately installed LK/preloader and working hardware
firmware out of this Android-only restore. A data reset may be required.

Never relock while modified firmware remains installed. No automatic flashing
or data-wipe utility is bundled with this release.
