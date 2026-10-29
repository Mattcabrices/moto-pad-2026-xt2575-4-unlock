# Rebuilding the filesystem cleanup

This is a repack of OEM Android filesystems; it does not compile Android,
the kernel, bootloader or modem from source. The scripts require Python 3.11+,
AFSR 2.0.0 and compatible erofs-utils (the tested formatter was 1.8.10 with
LZ4HC). Put `afsr` and `mkfs.erofs` on PATH or set AFSR and MKFS_EROFS to
their executable paths. On Windows, include .exe in explicit tool paths.

Acquire the exact original archive:
XT2575-3_ROW_OPEN_USER_M1317.3_W_ZUI_17.5.10.109_ST_260605.zip

SHA256: b6ef1ae98ba8bb5dc8c81af33bac98394fac511cf749d94e57d67d9772a64124

Source directory:
https://mirrors.lolinet.com/firmware/lenomola/2025/tablet/Pad_60_Neo/official/

Extract its image/super.img into a working directory. From this retail-lean
directory, with an empty set of generated output directories:

```text
python extract_android.py /path/to/super.img --extract system_a product_a system_ext_a
afsr unpack -i stock-images/system_a.img --output-tree stock-tree/system --output-metadata system.stock.toml
afsr unpack -i stock-images/product_a.img --output-tree stock-tree/product --output-metadata product.stock.toml
afsr unpack -i stock-images/system_ext_a.img --output-tree stock-tree/system_ext --output-metadata system_ext.stock.toml
python inventory_apps.py
python build_lean.py --pack
python verify_build.py
```

The stock Android boot animation is retained without an override. Wallpaper
overrides are in assets/overrides.json. Linux inode metadata is carried in AFSR
TOML and the PAX archive used for EROFS generation. Never rely on Windows host
file ownership as Android filesystem metadata. Keep sources and output hashes.

This rebuild does not create manufacturer-valid AVB signatures. The released
vbmeta uses the original XT2575-4 .020 metadata with only its flag byte at
offset 123 changed to 3, equivalent to fastboot's standard disable-verity and
disable-verification settings. It is intended only for the already-unlocked
test installation documented in INSTALL.md, and is not a secure-boot signing key.
