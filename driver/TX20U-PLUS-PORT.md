# TX20U Plus macOS port status

Target: TP-Link Archer TX20U Plus, USB `2357:013F`, RTL8852A/RTL8852AU.
Target OS: macOS Tahoe 26, x86_64.

## Confirmed source and build work

- Linux upstream USB device table maps `2357:013F` to `rtw89_8852au_info`.
- The macOS userspace port builds the RTL8852A-specific source set: `rtw8852a`, RFK/table files and `rtw8852au`.
- The daemon includes IOKit USB transport, firmware request support, MLME scan/connect, WPA2 supplicant and Ethernet/utun data-path components.
- The daemon and experimental Airport kext compile on a macOS 26 Intel GitHub runner.
- A hardware test kit is packaged separately from the incomplete Airport kext. It downloads firmware on the target Mac and runs the CLI scan path.
- Windows host sees the physical adapter as `VID_2357&PID_013F`.

## Not yet verified on TX20U Plus + macOS

- USB interface seize and endpoint enumeration under macOS Tahoe.
- RTL8852A power-on, efuse read, firmware boot-ready and PHY/RF calibration on this physical adapter.
- Scan results, WPA2 association, DHCP, bidirectional traffic and stability.
- Native System Settings integration. `RTW89Airport.kext` is milestone 0 and is not a working Wi-Fi kext.

The historical milestones in `docs/PROGRESS.md` describe a different RTL8852B test adapter. They are not proof that this RTL8852A USB device works.

## Safe test route

1. Boot Tahoe and connect TX20U Plus directly to a USB port.
2. Download the `TX20U-Plus-RTL8852AU-test-kit` artifact from the latest successful GitHub Actions run.
3. Extract it and follow the included README.
4. Run the scan test first and share its complete output.
5. Only proceed to association/data-path tests if firmware initialization and scan succeed.

Do not install the Airport kext, modify OpenCore/EFI, disable SIP, or alter security settings for this test.
