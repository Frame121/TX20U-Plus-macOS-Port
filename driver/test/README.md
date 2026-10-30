# RTL8852AU macOS Tahoe — hardware test kit (experimental)

Target adapter: TP-Link Archer TX20U Plus, USB VID:PID 2357:013F.
Target host: macOS Tahoe 26, Intel/AMD x86_64.

## Important status

This is a **userspace driver hardware-test build**, not a signed installer and not a finished native macOS Wi-Fi driver. The binary contains the RTL8852A/RTL8852AU upstream rtw89 backend and an IOKit USB transport shim. The included scan path must still be verified on the actual TX20U Plus under macOS.

The separate RTW89Airport.kext is not included here: its current source is milestone 0 and returns unsupported for requests. Do not install any experimental kext into OpenCore/EFI.

## Before testing

1. Boot macOS Tahoe and plug the TX20U Plus directly into the Mac (avoid hubs for the first test).
2. Confirm the adapter enumerates as USB 2357:013F in System Information > USB.
3. Extract this folder somewhere writable, e.g. ~/TX20U-Plus-Test.
4. Open Terminal in the extracted folder.

## Test 1 — firmware and scan

```sh
chmod +x scripts/*.sh
./scripts/scan.sh
```

The script downloads the two RTL8852A firmware variants from the linux-firmware project, validates their minimum size, then runs the driver's scan command. Firmware is not bundled; check the upstream firmware licence before redistribution.

Expected useful output includes the USB VID:PID, endpoint count, chip/firmware initialization messages, and discovered BSS entries. A successful compile alone is not a successful hardware test.

## Test 2 — connect (only after scan succeeds)

Create a password file with restrictive permissions:

```sh
umask 077
printf '%s' 'YOUR_WIFI_PASSWORD' > ~/.rtw89_psk
RTW89_FW_DIR="$PWD/rtw89" RTW89_PSK_FILE="$HOME/.rtw89_psk" ./rtw89d connect "YOUR_SSID"
```

The connection/data path is experimental. The utun/DHCP path may require elevated privileges depending on the host configuration. Do not set RTW89_SET_DEFAULT=1 on the first test.

## Report back

Please send the complete Terminal output from Test 1, plus:

- macOS version and build (sw_vers)
- USB device listing (system_profiler SPUSBDataType)
- Whether networks were listed
- Any panic/reboot or USB disconnect (stop immediately if this happens)

Do not install to EFI, disable SIP, or change security settings for this test.
