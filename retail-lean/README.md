# Moto Pad OEM Retail Lean — community v1

This is a stripped-down Motorola/Lenovo OEM Android 16 build for the **Moto Pad
2026 XT2575-4**. It keeps the familiar tablet interface, Motorola launchers,
multitasking, pen support, camera, audio components and everyday Google apps.
It is intended to reduce preload clutter while retaining the OEM tablet experience.

The Android base is **XT2575-3 retail ZUI 17.5.10.109**, used with the tested
XT2575-4 **.020 kernel/vendor/boot baseline**. This is a community cross-variant
Android build. It is not an official Motorola update, Pixel ROM, AOSP build,
universal GSI, or complete factory-flash package.

## What changed and why

The retail Android base already lacks the Metro/T-Mobile and Meta background
packages found in the XT2575-4 carrier-containing image. This cleanup removes
**27 additional packages / 29 APKs**, including WPS, RuStore, optional Google
preloads, partner recommendations, promotional feeds, Entertainment Space,
retail demo mode and the Motorola OMA-DM/Verizon provisioning pair.
Their package-specific configuration entries were pruned in 27 XML files.
See [REMOVED-APPS.md](REMOVED-APPS.md) and [recipe.json](recipe.json).

Google Play and services, Chrome/WebView, Maps, Photos, Gmail, YouTube, Drive,
Files, Gboard and Search remain. The stock Motorola Android boot animation,
OEM tablet/desktop launchers, pen and multitasking integration, camera,
Dolby audio components, accessibility, normal networking and telephony support
remain. The current custom geometric wallpaper is included. The early boot
logo, bootloader, preloader, kernel, vendor and modem were not changed by this
Android installation. Generic APN/carrier configuration is retained.

The purpose is a cleaner travel tablet with fewer unwanted preloads, while
keeping the OEM features that make the device useful. No speed or battery-life
benchmark claim is made.

## What has actually been tested

The owner installed this exact build on **one XT2575-4**. The initial boot
returned to Recovery; a Recovery factory data reset allowed Android to boot.
The owner specifically reports working audio and multitasking, Dolby Atmos
still enabled, and normal functionality in use so far. This is not a complete
independent hardware, radio, DRM, app-compatibility or reliability test.

All three rebuilt filesystems passed unpack-and-compare validation, including
retained file hashes and Linux ownership/modes/SELinux metadata. Removed APKs
were confirmed absent. The Android boot animation matches its OEM source
byte-for-byte. Vendor-interface XML files match the working .020 firmware;
the core framework signing certificate matches. SELinux policy definitions
and context entries match after accounting for declaration/member ordering.
See [FILESYSTEM-VALIDATION.json](FILESYSTEM-VALIDATION.json).

## Security and version information

The Android security patch is **June 5, 2026**. This is older than the tested
XT2575-4 .020 stock Android base, which reports September 5, 2026. Build numbers
belong to separate variant release sequences; `.109` does not mean a newer
security patch than `.020`. Debloating does not add security updates.

These modified Android images do not match the manufacturer's original AVB
hashes. The included .020-derived `vbmeta_a` has flags **3**, disabling AVB
verification and dm-verity for the custom OS. This weakens boot-integrity
protection, requires an already-unlocked device, and persists until matching
stock verification metadata is restored. **Do not relock with this build.**

## Download and installation

Download the assets from the **oem-retail-lean-v1** GitHub release. The system
image is split into three parts to fit GitHub's per-asset size limit. Product,
system_ext and vbmeta are separate files. This is not a recovery-flashable ZIP.

Use [reassemble.ps1](reassemble.ps1) or [reassemble.sh](reassemble.sh) with
BUILD-MANIFEST.json to verify all downloaded parts and reconstructed images.
Follow [INSTALL.md](INSTALL.md) for the exact tested partition scope, data-loss
expectations and stock-restore approach. Do not apply this package to other
models or firmware baselines without establishing their compatibility.

Developer options on this OEM interface are enabled by tapping **Software
Version** seven times on the main About tablet page. The Build number inside
the Android version details screen is display-only.

## Rebuild information

The recipe, APK inventory, wallpaper assets and filesystem build/validation
scripts are included for review. Regenerate stock-tree, stock-images and the
AFSR metadata from the exact original firmware before running the scripts;
generated source/validation trees are not stored in Git. See [BUILDING.md](BUILDING.md).

Motorola, Lenovo, MediaTek, Google and other vendors retain their firmware and
application rights. See [NOTICE.md](NOTICE.md). No device serial, IMEI,
user data, account tokens or private signing keys are included in this release.
