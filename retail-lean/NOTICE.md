# Notice and credits

This community release contains modified Motorola/Lenovo OEM Android firmware,
including third-party and Google components. Motorola, Lenovo, MediaTek,
Google, Android contributors and other vendors retain their respective rights,
trademarks and applicable licenses. It is not an official or endorsed update.
No blanket open-source license is granted over proprietary firmware or apps.

Matt Cabrices is the project maintainer, device owner and hardware tester.
Filesystem work used chenxiaolong/afsr (v2.0.0), erofs-utils tooling and AOSP
liblp/AVB format documentation. Those upstream tools remain under their own
licenses; their binaries are not included in these Android release assets.

The release contains no bootloader-unlock payload. The Android images originate
from factory firmware rather than a user's data partition. No device-unique
serial, IMEI, account data, unlock tokens, or private signing keys were added.

Upstreams:
- https://github.com/chenxiaolong/afsr
- https://git.kernel.org/pub/scm/linux/kernel/git/xiang/erofs-utils.git/
- https://android.googlesource.com/platform/external/avb/
- https://android.googlesource.com/platform/system/core/+/main/fs_mgr/liblp/
