#!/bin/bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get -o Acquire::Retries=3 update
apt-get -o Acquire::Retries=3 install -y python3 python3-tk python3-psutil ca-certificates curl
BASE="https://raw.githubusercontent.com/chaukentsakiso55-a11y/obsidian-desk/main/essentials/apps/ember"
DEST="/root/Applications/Ember"
mkdir -p "$DEST/modules"
fetch() {
  curl --fail --location --retry 4 --retry-delay 2 --connect-timeout 15 --max-time 120 "$BASE/$1" -o "$DEST/$1"
}
fetch main.py
fetch requirements.txt
fetch modules/__init__.py
fetch modules/chat.py
fetch modules/evolution.py
fetch modules/pulsa.py
fetch modules/security.py
fetch modules/system_intel.py
test -s "$DEST/main.py"
echo "Ember Linux bundle installed."
