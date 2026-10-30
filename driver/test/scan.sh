#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
ARCH="$(uname -m)"
if [ "$ARCH" != "x86_64" ]; then
  echo "This build is x86_64; current architecture is $ARCH." >&2
  exit 2
fi
if [ ! -x ./rtw89d ]; then
  echo "rtw89d is missing or not executable." >&2
  exit 2
fi
bash ./scripts/fetch-firmware.sh
echo "Starting RTL8852AU scan. Keep the adapter connected directly to the Mac."
exec env RTW89_FW_DIR="$ROOT/rtw89" ./rtw89d scan
