# TX20U Plus port notes (experimental)

Target: TP-Link Archer TX20U Plus, USB `2357:013F`, Linux rtw89 chip family `RTL8852A` / `RTL8852AU`.

## Changes in this working copy

- Switched the userspace rtw89 build object list from the tested RTL8852B/RTL8852BU target to the RTL8852A/RTL8852AU source files already present in `rtw89/src`.
- Added an RTL8852A firmware fetch script for `rtw8852a_fw.bin` and `rtw8852a_fw-1.bin`.
- The upstream `rtw8852au.c` USB table already includes `2357:013F` with interface class/subclass/protocol `FF/FF/FF` and selects `rtw89_8852au_info`.
- The daemon's existing USB enumeration path uses the selected driver's `id_table`; TX20U Plus is expected to bind directly and does not need the Nano's `0BDA:1A2B` virtual-CD mode switch if it enumerates as `2357:013F`.

## Important unverified items

- This patch is static source preparation only. It has NOT been compiled or run.
- The original macOS repository's verified hardware milestone is a different RTL8852B adapter. Presence of `rtw8852au.c` and the USB ID table is not proof that its full macOS userspace port is complete for RTL8852AU.
- `rtw8852a` USB power-on, efuse, RF/PHY, firmware, TX/RX and aggregation must be verified on the real TX20U Plus.
- Full Xcode/macOS SDK is required for `airport` and kext builds. This Windows host has no Xcode, and WSL/Linux is not installed.
- Do not install this experimental build in the production EFI. Keep `E:\EFI` unchanged until macOS scan, association and traffic tests pass.

## Build sequence on a macOS 26 x86_64 build host

1. Review `scripts/fetch-firmware.sh` and fetch licensed firmware.
2. `cd port && make clean && make`
3. `cd airport && ./build.sh`
4. `cd kext && ./build.sh`
5. Validate daemon probe, firmware ready, scan, WPA2 association, DHCP and bidirectional traffic before any EFI deployment.

## Firmware fetched for this experimental worktree

- `rtw8852a_fw.bin`: 1,428,272 bytes; SHA-256 `7EB1FE457F5A704B7A4F05A66C67CFA6AF2F1142566B640C8E402445D04B0159`.
- `rtw8852a_fw-1.bin`: 1,958,648 bytes; SHA-256 `FDB5513CF7372440D7980A61AA4B753B192B056734A978458AE4A4EF7F4B2C1E`.
- Both were fetched from the linux-firmware GitLab mirror after the kernel.org endpoint returned an anti-bot HTML page; payload sizes were checked so the HTML response was not retained.
- Firmware files are local-only and excluded from source-control changes.
