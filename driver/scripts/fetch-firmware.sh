#!/bin/bash
# Fetch RTL8852A/RTL8852AU firmware from the linux-firmware project.
# Firmware is kept local and is not committed or redistributed by this port.
set -euo pipefail
cd "$(dirname "$0")/../rtw89"
BASE="https://gitlab.com/kernel-firmware/linux-firmware/-/raw/main/rtw89"
for f in rtw8852a_fw.bin rtw8852a_fw-1.bin; do
  if [ ! -s "$f" ] || [ "$(wc -c < "$f")" -lt 500000 ]; then
    rm -f "$f"
    echo "fetching $f"
    curl -fL --retry 3 -o "$f" "$BASE/$f"
  fi
  size=$(wc -c < "$f")
  if [ "$size" -lt 500000 ]; then
    echo "ERROR: $f is too small ($size bytes); refusing HTML/error payload" >&2
    rm -f "$f"
    exit 1
  fi
done
echo "RTL8852A firmware ready in $(pwd)"
echo "Review linux-firmware/LICENCE.rtlwifi_firmware.txt before redistribution."
