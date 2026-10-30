# TX20U Plus -> macOS Tahoe port assessment

Date: 2026-10-30
Target: TP-Link Archer TX20U Plus, USB VID:PID 2357:013F
Target OS: macOS Tahoe 26, x86_64 Hackintosh

## Work completed on the connected Windows host

- Cloned `Long0823-1/rtw89-macos` into `references/rtw89-macos`.
- Cloned `hyekalhitech/ArcherRTL8832AU` into `references/ArcherRTL8832AU`.
- Cloned `lwfinger/rtl8852au` into `references/rtl8852au-linux`.
- Confirmed the Linux USB table maps 2357:013F to `RTL8852A` in `os_dep/linux/usb_intf.c`.
- Confirmed this host has no WSL/Linux installation (`wsl --list --verbose` reports WSL is not installed).
- No Xcode/macOS SDK is present on this Windows host. No macOS kext has been built or tested.
- `E:\EFI` was not modified.

## Critical compatibility finding

The macOS reference is useful, but it is not a drop-in driver for TX20U Plus.

The Linux TX20U Plus driver identifies 2357:013F as `RTL8852A` (RTL8852AU USB family).
The macOS reference repository has mixed historical notes: `docs/PROGRESS.md` describes the 8852AU port plan and contains 8852A source files, but its current tested milestone and current build Makefile are centered on RTL8852B / 35BC:0108. Its README and current USB mode-switch path also describe a different adapter enumeration (0BDA:1A2B -> 35BC:0108). Therefore adding 2357:013F to an Info.plist alone would be unsafe and would not implement the correct chipset initialization.

The current `port/Makefile` RTW object list must be audited and extended for the RTL8852A USB path before attempting to bind this device. Required review areas include:

1. Correct chip identification and `rtw8852au` USB ops / endpoint layout.
2. USB interface matching for 2357:013F (vendor 0x2357, product 0x013F, interface class 0xFF).
3. RTL8852A firmware selection and firmware loading sequence (do not reuse 8852B firmware blindly).
4. RTL8852A efuse, RF, PHY and power-on configuration.
5. TX/RX aggregation, USB bulk endpoint mapping and URB completion behavior.
6. Existing userspace `rtw89d` network/MLME integration and macOS network interface glue.
7. Tahoe IO80211/AirPort integration requirements and AMFIPass / Modern Wireless compatibility.

## Correct development route

- Use the Linux vendor driver and its 2357:013F USB table as hardware behavior/reference evidence; it is not a macOS binary.
- Use the macOS `rtw89-macos` project as an architectural port reference, not as a ready-made TX20U Plus driver.
- Collect actual USB descriptors and Linux probe/firmware logs from the physical TX20U Plus before changing the macOS port.
- Implement and test the RTL8852A USB path separately from the already-tested RTL8852B path.
- Build `rtw89d` and kext components on macOS with full Xcode / macOS SDK. Linux can collect evidence and validate the Linux reference driver, but cannot produce a supported Apple kext build by itself.
- Only install into a backed-up test EFI after the driver enumerates, initializes, scans, associates, and passes traffic tests on macOS.

## Current status

Source/reference workspace prepared. No working TX20U Plus macOS driver exists in this workspace yet. Do not copy the Nano kexts into EFI and do not change `E:\EFI`.
