# SAFETY PROTOCOL — read and complete before flashing

Bootloader modification is a high-risk operation. A bad LK write can leave the
tablet unable to boot, and recovery is not guaranteed. Unlocking destroys all
user data. This protocol is mandatory.

## 0. Scope

This build was validated on **one** device:

- Motorola Moto Pad 2026 **XT2575-4**, product `sycamore_row_5G`
- Active slot **a**
- Installed Android `17.5.10.017`
- LK source `17.5.10.020`
- `flash_lock: no`, `unlocked: no` before the procedure

Do not use it on another model, another slot, or a device whose preflight
values differ. Do not assume it works on other XT2575-4 firmware revisions.

## 1. Authorization

- [ ] I own this tablet, or I have explicit authorization to service it.
- [ ] I understand unlocking may void the warranty and carrier terms.
- [ ] I am not using this to bypass another person's device or account.

If any box is unchecked, **stop**.

## 2. Data and recovery

- [ ] I accept that unlocking **erases all user data**.
- [ ] I have backed up anything I still need.
- [ ] I have the official XT2575-4 17.5.10.020 factory package with
      `SPFlashToolV6.exe`, `da.auth`, `DA_BR.bin`, the scatter, and stock
      `lk.img`.
- [ ] I have read the package's own recovery instructions.
- [ ] I understand that SP Flash Tool recovery was **not tested on this unit**
      by this project.
- [ ] I will not interrupt a flash or recovery while it is writing.

If I do not have a recovery path, **stop**.

## 3. Preflight verification (read-only)

Run only these queries on this bootloader:

```text
fastboot getvar product
fastboot getvar current-slot
fastboot getvar unlocked
fastboot getvar flash_lock
```

Required values:

- [ ] `product: sycamore_row_5G`
- [ ] `current-slot: a`
- [ ] `unlocked: no` (before the unlock step)
- [ ] `flash_lock: no`

Do **not** run `fastboot oem device-info` or `fastboot getvar version-baseband`.
Both wedged the USB endpoint during testing. If `getvar` starts timing out:

1. Unplug USB.
2. Hold **Power + Volume Down** for 10–15 seconds.
3. Let the tablet boot Android.
4. Reconnect and run `adb reboot bootloader`.

Do not flash while the endpoint is timing out.

## 4. File integrity

- [ ] I verified the image SHA-256 is
      `81ee5de950470c9e31552135349589e8b056a4312f93419930a9502f4bbbd034`.
- [ ] I verified the payload SHA-256 is
      `95462aa5ba178ac1217f3d0a3271d2b568b8dd9a8460fcfa15ec7b7c346717cc`.
- [ ] I am using the image from this repository, not a modified copy.

If a hash differs, **stop**.

## 5. Write rules

- [ ] Flash **`lk_a` only**. Never write `lk_b`.
- [ ] Never switch slots to “recover” a bad LK.
- [ ] Never relock the bootloader.
- [ ] Never flash both bootloader slots.
- [ ] Use a stable USB port and cable; keep the tablet charged.
- [ ] Do not disconnect during `Sending` or `Writing`.

If the flash is rejected, **stop** — a rejection does not modify the device.

## 6. Unlock confirmation

- [ ] I am physically at the tablet for the unlock step.
- [ ] I will **tap** Volume Up and Volume Down alternately during the
      ~5-second confirmation window. Holding a key before the command did not
      register on the tested unit.
- [ ] I understand the unlock erases data and reboots the tablet.

If the command fails after ~5 seconds without a confirmation, nothing was
unlocked. Re-check that the tablet is showing the warning screen and tap the
keys during the window.

## 7. Stop conditions

**Stop immediately and do not continue** if any of these occur:

- Product is not `sycamore_row_5G`.
- Active slot is not `a`.
- `flash_lock` is not `no`.
- Image or payload hash differs.
- The flash command is rejected.
- Fastboot does not come back after `fastboot reboot-bootloader`.
- The tablet shows an error instead of the unlock warning.
- The USB endpoint times out or the device disappears mid-write.

If fastboot is gone, use the factory SP Flash Tool package. Do not repeatedly
power-cycle a device that is actively writing.

## 8. Post-unlock rules

- [ ] Verify `fastboot getvar unlocked` returns `yes`.
- [ ] After Android boots, verify `ro.boot.flash.locked` is `0`.
- [ ] Accept the orange “bootloader unlocked” warning as expected.
- [ ] Do not relock or write `lk_b`.
- [ ] Keep the stock package and original `lk.img` for recovery.

## Acknowledgement

I have read this protocol, I meet the authorization requirement, I have a
recovery path, and I accept the risk of data loss and permanent bricking.

Signed: ____________________  Date: ____________
