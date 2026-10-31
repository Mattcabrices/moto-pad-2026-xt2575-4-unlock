# Community success reports

These are contributor-reported outcomes, separate from the maintainer's original
hardware validation. No raw device logs, partition backups, or benchmark captures
were supplied with the report below. The maintainer has not independently
reproduced its additional claims.

## XT2575-4: u/Mountain_Quail_8715

Recorded **October 30, 2026**, from a Reddit comment pasted to the maintainer
by u/mattcabrices. Attribution: **u/Mountain_Quail_8715**. The supplied excerpt
did not include a comment permalink; relative timestamps are not treated as
an exact test date. This entry summarizes the report rather than reproducing
the full AI-assisted postmortem.

The contributor reports following this repository's unlock guide successfully
on another Moto Pad 2026. Their reported configuration and results:

| Item | Contributor report |
| --- | --- |
| Device | Moto Pad 2026 XT2575-4, product `sycamore_row_5G` |
| Android build | `17.5.10.017_ST_260711` |
| Android security patch | `2026-07-05` |
| LK build before | `27256d543_202607101822` |
| LK build after | `27256d543_202609231741` |
| Active slot | `a` |
| Initial `flash_lock` | `no` |
| LK image write | Sending and writing both reported `OKAY` |
| Unlock | Reported successful; tapping the volume buttons during the confirmation window worked, holding did not |
| User data during unlock | Reportedly was not wiped on this unit |
| Root afterward | Reported Magisk v31.1 using `init_boot` |
| Later factory reset | Reportedly retained unlock and root; Magisk app needed reinstalling |
| Banking app | One unspecified app reportedly continued working |
| OTA check | Settings reportedly offered no update while on `.017` |

The contributor also reports creating hashed partition backups, capturing a
clean baseline, and subsequently debloating their own installation. Their
write-up describes 24 removals, a clean reboot, and a WPS cold-start change from
663 ms to 502 ms. These are self-reported results without the underlying
artifacts or measurement method available here.

### What this adds

This is an **additional community-reported unlock success** for the same model,
slot, initial `flash_lock` state and LK build transition as the original test.
It is **not a second validation of the OEM Retail Lean ROM**: the contributor
describes their own rooted and debloated `.017` installation, not installation
of the repository's XT2575-3-based retail Android images.

### Limits and differences

- Always back up and plan for data loss. This contributor's no-wipe observation
  does not establish that another unlock will preserve data. A factory reset
  does erase local user data even if modified boot images remain installed.
- One working banking app does not establish Play Integrity, Google Wallet,
  DRM, or compatibility with other banking apps.
- An update check offering nothing at one point does not establish that future
  OTAs will never arrive or that installing one would be safe.
- The AI-assisted narrative additionally asserts problems with factory recovery
  files and an encrypted lock-state mechanism. No supporting files or logs were
  supplied for those assertions. They are not adopted here as verified facts
  or a tested recovery procedure.
- The reported root and factory-reset behavior does not establish compatibility
  with other builds, models, slots, or firmware packages.

Thanks to u/Mountain_Quail_8715 for reporting their experience and configuration.
