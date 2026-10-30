#!/usr/bin/env bash
# Collect evidence for TP-Link Archer TX20U Plus (2357:013F) on Linux.
# Read-only: does not install drivers or change system configuration.
set -u
OUT="${1:-tx20u-plus-linux-evidence-$(date +%Y%m%d-%H%M%S)}"
mkdir -p "$OUT"
run() { echo "$ $*"; "$@" 2>&1 || true; }
run uname -a > "$OUT/uname.txt"
run lsusb > "$OUT/lsusb.txt"
run lsusb -t > "$OUT/lsusb-tree.txt"
run lsusb -d 2357:013f -v > "$OUT/tx20u-plus-usb-descriptor.txt"
run sh -c 'dmesg | grep -iE "2357|013f|8852|rtw|firmware|wlan|usb" | tail -n 500' > "$OUT/kernel-wireless-log.txt"
run sh -c 'lsmod | grep -iE "8852|rtw"' > "$OUT/wifi-modules.txt"
run sh -c 'iw dev; iw phy' > "$OUT/iw-wireless.txt"
run sh -c 'ip -brief link; ip route' > "$OUT/network-state.txt"
run sh -c 'modinfo 8852au' > "$OUT/modinfo-8852au.txt"
run sh -c 'find /lib/firmware/rtw89 -maxdepth 1 -type f -printf "%f %s bytes\\n" 2>/dev/null | sort' > "$OUT/rtw89-firmware.txt"
echo "Evidence saved to: $OUT"
echo "Please review for passwords/private SSIDs before sharing."
