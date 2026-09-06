#!/usr/bin/env bash
# Rebuilds downloads/Vigil.zip from a staging tree.
#
# Desktop and web formats live in separate folders on purpose: every leaf folder
# holds exactly one format, so "select all" inside any of them is always safe.
# Mixing .ttf and .woff2 in one folder makes Font Book throw errors on the web
# files, which reads to a non-technical user like a broken download.
#
# Note: the .ttf and .otf binaries are NOT in this repo — only fonts/*.woff2 is.
# The staging tree must come from an existing zip or your font build output.
#   unzip downloads/Vigil.zip -d /tmp/vigil-stage
#   bash tools/build-download-zip.sh /tmp/vigil-stage
set -euo pipefail
src="${1:?usage: build-download-zip.sh <staging-dir>}"
root="$(cd "$(dirname "$0")/.." && pwd)"
out="$root/downloads/Vigil.zip"
for d in ttf woff2 otf variable/ttf variable/woff2 outline/ttf outline/woff2; do
  [ -d "$src/$d" ] || { echo "missing $d in staging tree" >&2; exit 1; }
done
# refuse to ship a folder containing more than one format
while IFS= read -r d; do
  n=$(find "$d" -maxdepth 1 -type f -name '*.*' | sed 's/.*\.//' | sort -u | wc -l | tr -d ' ')
  [ "$n" -le 1 ] || { echo "mixed formats in ${d#$src/}" >&2; exit 1; }
done < <(find "$src" -mindepth 1 -type d)
rm -f "$out"
( cd "$src" && zip -qr "$out" . -x '.DS_Store' )
unzip -t "$out" >/dev/null
echo "built $out  ($(( $(wc -c < "$out") / 1024 )) KB)"
