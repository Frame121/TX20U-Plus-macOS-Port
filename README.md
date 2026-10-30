# TP-Link Archer TX20U Plus — macOS Tahoe port

**Status: experimental / not yet working or validated.**

Independent project for the TP-Link Archer TX20U Plus USB Wi-Fi adapter.

## Target

- Adapter: TP-Link Archer TX20U Plus
- USB VID:PID: `2357:013F`
- Chip family: Realtek RTL8852A / RTL8852AU
- Target OS: macOS Tahoe 26, Intel x86_64 Hackintosh
- Intended features: Wi-Fi scan, WPA2/WPA3 association where implemented, DHCP and network traffic

## Repository layout

- `driver/`: isolated experimental macOS port source tree
- `PORTING_ASSESSMENT.md`: hardware and compatibility findings
- `scripts/`: host-side evidence collection
- `references/` and `vendor/` are local-only and excluded from Git

## Current engineering status

This repository does **not** currently provide a working TX20U Plus macOS driver. The source tree is an experimental RTL8852A adaptation of an existing macOS Realtek project. The upstream project's demonstrated adapter is a different RTL8852B device; the presence of an RTL8852AU source file and a matching USB ID does not establish a complete hardware port.

Still required before this can be called working:

1. Validate RTL8852A USB probe, endpoint layout, power-on and efuse handling on the physical adapter.
2. Validate firmware loading and chip/RF/PHY initialization.
3. Validate USB TX/RX, aggregation and error recovery.
4. Complete and validate macOS networking integration.
5. Build on a real macOS 26 Intel/Xcode SDK environment.
6. Test scan, WPA association, DHCP, DNS and bidirectional traffic on the actual TX20U Plus.

The experimental build workflow is a compile check only. A successful CI build would **not** mean the adapter works.

## Build (macOS only)

On a macOS build host with Xcode command-line tools and the required kernel headers:

```sh
cd driver
bash scripts/fetch-firmware.sh
cd port && make clean && make
cd ../airport && bash build.sh
```

Firmware is fetched locally and is not committed. Review the upstream linux-firmware licensing notice before redistribution.

## Safety

- Do not install this experimental kext into a production EFI.
- Do not replace or modify CherryRed/Cobalt64.
- Keep the existing bootable EFI backed up.
- No files in a production EFI are modified by this repository.

## References

See `driver/THIRD_PARTY.md` for upstream licensing and attribution. See `PORTING_ASSESSMENT.md` for the detailed compatibility assessment.
