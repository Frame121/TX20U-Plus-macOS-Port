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
cd ../kext && bash build.sh
```

Firmware is fetched locally and is not committed. Review the upstream linux-firmware licensing notice before redistribution.

## Installation & Testing on macOS

### Prerequisites (for macOS Sonoma / Sequoia / Tahoe)
- **OpenCore EFI**: Hackintosh systems running modern macOS require legacy Wi-Fi framework support because Apple dropped older Wi-Fi drivers:
  - Inject `IOSkywalkFamily.kext` (v1.0) and `IO80211FamilyLegacy.kext` (v1.0) via OpenCore.
  - Apply OpenCore Legacy Patcher (OCLP) Root Patch (Modern Wireless) with `AMFIPass.kext` / `amfi=0x80`.
- Connect the TP-Link Archer TX20U Plus directly to a USB 3.0 / USB 2.0 port (avoid unpowered hubs during testing).
- Confirm the device is recognized in macOS: Apple Menu > About This Mac > System Report > USB (`TP-Link 802.11ax WLAN Adapter` with VID: `0x2357`, PID: `0x013F`).

### Phase 1: Standalone CLI Test (Zero EFI Risk)
You do not need to install kexts to verify that the adapter and firmware work:
1. Extract `TX20U-Plus-RTL8852AU-test-kit` or compile `rtw89d`.
2. Run the scan test:
   ```sh
   chmod +x scripts/*.sh
   ./scripts/scan.sh
   ```
3. If probe and scan succeed (networks listed), test association:
   ```sh
   umask 077
   printf '%s' 'YOUR_WIFI_PASSWORD' > ~/.rtw89_psk
   RTW89_FW_DIR="$PWD/rtw89" RTW89_PSK_FILE="$HOME/.rtw89_psk" ./rtw89d connect "YOUR_SSID"
   ```

### Phase 2: Full System Settings Integration
Once CLI tests pass:
1. Copy `RTW89Airport.kext` to `EFI/OC/Kexts/` and add it to `config.plist` (under `Kernel -> Add`, loaded after `IO80211FamilyLegacy`).
2. Install the background daemon and auto-join service:
   ```sh
   sudo bash install/install.sh
   ```
3. Reboot macOS. The adapter will appear as an active Wi-Fi interface in **System Settings > Wi-Fi**.
4. Check daemon status at any time:
   ```sh
   echo status | nc -U /var/run/rtw89d.sock
   tail -f /var/log/rtw89d.log
   ```

## Safety

- Do not install this experimental kext into a production EFI.
- Do not replace or modify CherryRed/Cobalt64.
- Keep the existing bootable EFI backed up.
- No files in a production EFI are modified by this repository.

## References

See `driver/THIRD_PARTY.md` for upstream licensing and attribution. See `PORTING_ASSESSMENT.md` for the detailed compatibility assessment.
