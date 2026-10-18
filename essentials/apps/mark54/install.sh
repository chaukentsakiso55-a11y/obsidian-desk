#!/bin/bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get -o Acquire::Retries=3 update
apt-get -o Acquire::Retries=3 install -y python3 python3-tk python3-psutil ca-certificates curl
BASE="https://raw.githubusercontent.com/chaukentsakiso55-a11y/obsidian-desk/main/essentials/apps/mark54"
DEST="/root/Applications/MarkLIV"
mkdir -p "$DEST"
curl --fail --location --retry 4 --retry-delay 2 --connect-timeout 15 --max-time 120 "$BASE/main.py" -o "$DEST/main.py"
test -s "$DEST/main.py"
echo "Mark LIV legacy Linux port installed."
