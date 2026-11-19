# TX20U Plus Linux reference capture — 2026-11-01

## Hardware confirmed on the Linux development host

- Host: CachyOS x86_64, kernel 7.3.1-1-cachyos.
- Adapter: TP-Link 802.11ax WLAN Adapter, USB VID:PID 2357:013F.
- USB 3.0 SuperSpeed, negotiated 5 Gbit/s.
- Interface 0, vendor-specific class/subclass/protocol FF/FF/FF.
- One Bulk IN endpoint: 0x84.
- Seven Bulk OUT endpoints: 0x05, 0x06, 0x07, 0x09, 0x0A, 0x0B, 0x0C.
- All observed bulk endpoints have 1024-byte max packet; IN endpoint reports burst 3, OUT endpoints burst 1.
- Linux module: rtw89_8852au; dependencies include rtw89_usb and rtw89_8852a.
- Driver bound at /sys/bus/usb/drivers/rtw89_8852au.
- Network interface wlan0 is associated and passing traffic.

## Firmware and chip information

Kernel log confirms rtw89/rtw8852a_fw-1.bin was loaded.
- Firmware version: 0.13.36.2.
- Firmware tag: 52acc807.
- BB version: 00 16 00 00.
- Radio A version: 00 38 00 00.
- NCTL version: 00 0d 00 00.
- TXPWR version: 00 37 00 00.
- PWR_TRK version: 00 22 00 00.
- Chip info: CID 0, CV 2, AID 0, ACV 0, RFE 1.

Observed Wi-Fi link: channel 36, 5180 MHz, 80 MHz. Instantaneous PHY rates varied during sampling (RX 468–585 Mbit/s, TX 260 Mbit/s); these are PHY rates, not internet throughput.

## Driver source findings

The checked-in Linux rtw89 source maps 2357:013F with interface class FF/FF/FF to rtw89_8852au_info and rtw8852a_chip_info.

The 8852AU USB profile uses a queue-to-bulk-out mapping table:
- ACH0 -> bulkout index 3
- ACH2 -> bulkout index 5
- ACH4 -> bulkout index 4
- ACH6 -> bulkout index 6
- B0MG/B0HI -> bulkout index 0
- B1MG/B1HI -> bulkout index 1
- H2C -> bulkout index 2

Important: these are indices into the endpoint array populated by rtw89_usb_parse(), not USB endpoint addresses. The Linux parser enumerates bulk OUT descriptors in descriptor order and stores endpoint numbers in out_pipe[]. For this device that means the observed descriptor order must be preserved when mapping queues.

The 8852A USB profile also sets RX aggregation alignment to 8 bytes. The USB layer uses 8 RX URB control blocks, 16 RX SKB buffers, and a 20,480-byte receive buffer. RX aggregation for RTL8852A uses the v1 register profile.

## macOS porting consequences

1. Preserve the distinction between endpoint address and endpoint-array index. A mismatch here will route H2C and data queues to the wrong USB pipes.
2. Ensure the macOS IOKit endpoint enumeration order matches the Linux descriptor order, or explicitly build a stable endpoint-index map.
3. Validate the exact 8852A profile and do not reuse the 8852B Nano path or firmware.
4. Port USB vendor control transfers (request 0x05, read type 0xC0, write type 0x40), bulk RX/TX, RX aggregation, descriptor parsing, and completion semantics.
5. Use local firmware supplied by the user. Do not commit firmware blobs or include them in public artifacts.
6. USB transport and firmware boot are not sufficient for a usable macOS Wi-Fi interface. MLME, crypto, data path and the OS integration layer remain separate milestones.

## Evidence files

Raw capture from the Linux host is stored alongside this document at:
linux-evidence-2026-11-01/tx20u-linux-capture.txt

No USB reset, device rebind, firmware write, register poke, or disruptive unload/reload was performed during this capture.


## 2026-11-01 development update — USB transport hardening

Changes made in `port/host/usb_shim.c` (uncommitted, local only):

- Check IOKit interface iterator, plug-in creation, QueryInterface, interface open, endpoint-count and per-pipe property return codes.
- Verify that the claimed interface is interface 0; reject unexpected endpoint counts and invalid/duplicate endpoint mappings rather than probing with incomplete pipe tables.
- Preserve IOKit pipe order in the emulated Linux endpoint descriptor array. The bulk endpoint address and the one-based IOKit pipe reference remain separate values.
- Capture the actual max-packet size for every bulk OUT endpoint.
- Determine URB_ZERO_PACKET from that endpoint's max-packet size, not a hard-coded 512-byte modulus. This matters on this adapter: its SuperSpeed OUT endpoints report 1024-byte max packets, so a 512-byte transfer must not receive a ZLP while 1024-byte multiples do.
- Clear endpoint and max-packet maps on close.

Validation performed on CachyOS (no device reset/rebind and no firmware/register writes):

- Endpoint-order test passed for IN EP4 and OUT EP5, EP6, EP7, EP9, EP10, EP11, EP12.
- Queue mapping passed: B0MG -> EP5, B1MG -> EP6, H2C -> EP7, ACH0 -> EP9, ACH4 -> EP10, ACH2 -> EP11, ACH6 -> EP12.
- IOKit one-based pipe-reference mapping passed for all eight endpoints.
- SuperSpeed ZLP boundary checks passed for 512, 1024 and 2048-byte payload lengths.
- `git diff --check` passed; Linux adapter remained associated on wlan0.

## Remaining validation boundary

The RX/TX descriptor and RX aggregation implementation is already present in upstream `rtw89/src/usb.c` and the RTL8852A profile sets 8-byte RX aggregation alignment. Firmware download and H2C command submission are present in `fw.c` and `usb.c`; MLME/supplicant, data path, daemon and Airport bridge sources are also present.

These source files being present is not proof that the complete stack works with this exact 2357:013f adapter on macOS. Linux cannot compile or execute the IOKit USB shim. The next required validation is a macOS SDK build, followed by hardware tests for: firmware-ready/C2H response, RX aggregation parsing, TX completion/fence handling, scan, association and encrypted data traffic. The later macOS Network Integration milestone must be re-verified for this RTL8852AU variant; previous progress notes about System Settings integration were for a different RTL8852B device and must not be treated as proof for this adapter.


## 2026-11-01 development update — RX/TX and error handling

Additional local, uncommitted changes in `rtw89/src/usb.c`:

- Implemented the USB HCI `flush_queues` callback. It waits for the software TX queues and submitted TX URBs on data channels to drain, excludes firmware command channel 12 (matching the PCI HCI convention), and emits per-channel timeout diagnostics. The total wait is bounded to one second rather than one second per channel.
- Replaced the USB error-status TODO with software-side diagnostics for RX queue depth, RX free-buffer depth, continual I/O errors, and TX queue/in-flight counts. No speculative MMIO reads were added.
- Hardened RX aggregate parsing: reject zero descriptor/payload lengths, invalid offsets, descriptor overruns and truncated frames before pointer arithmetic; validate aggregate alignment; handle a final aggregate member without requiring trailing padding.

Validation on Linux:
- Synthetic RX parser boundary checks passed for a single frame, a two-frame aggregate with 8-byte alignment, zero-length descriptors, out-of-range offsets and truncated payloads.
- USB endpoint/queue mapping and SuperSpeed ZLP boundary checks from the previous update remain passing.
- The Linux `wlan0` link remained associated during read-only validation.
- `git diff --check` passed.

Build limitation:
- Attempted to compile `build/rtw_usb.o` on CachyOS. Compilation stops in the pre-existing compatibility headers before reaching a useful validation of the modified translation unit: `loff_t` conflicts with glibc, errno constants are not included in the expected order, and the compatibility `pci_dev` declarations are incompatible. This Linux userspace build is not the target build anyway; the actual daemon links against Apple IOKit/CoreFoundation and must be built with the macOS SDK.
- No firmware upload, register writes, USB reset/rebind, or driver replacement was performed. The active Linux adapter remains on the in-kernel `rtw89_8852au` driver; therefore these source changes have not yet been exercised by the hardware.
