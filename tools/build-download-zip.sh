#!/usr/bin/env bash
# Rebuilds downloads/Vigil.zip entirely from files tracked in this repo.
#
#   bash tools/build-download-zip.sh
#
# Sources:
#   fonts/ttf/*.ttf     16 statics + 2 variable + 2 outline
#   fonts/otf/*.otf     16 statics + 2 outline
#   fonts/*.woff2       the same faces for the web
#   downloads/src/      README.md and Vigil-specimen.html
#   OFL.txt
#
# Desktop and web formats go into separate folders on purpose. When .ttf and
# .woff2 shared a folder, anyone selecting everything in it handed Font Book
# sixteen web fonts it cannot install, which reads as a broken download rather
# than as user error. The check at the bottom refuses to build if that regresses.
#
# The variable files are named Vigil-wght-.woff2 in the repo because square
# brackets are awkward in URLs, and Vigil[wght].woff2 in the zip because that is
# the convention desktop apps expect. The rename happens here.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
out="downloads/Vigil.zip"
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT

mkdir -p "$stage"/{ttf,woff2,otf,variable/ttf,variable/woff2,outline/ttf,outline/woff2}

is_special() { case "$1" in *'[wght]'*|VigilOutline-*) return 0;; *) return 1;; esac; }

for f in fonts/ttf/*.ttf; do
  b=$(basename "$f")
  case "$b" in
    *'[wght]'*)      cp "$f" "$stage/variable/ttf/$b" ;;
    VigilOutline-*)  cp "$f" "$stage/outline/ttf/$b" ;;
    *)               cp "$f" "$stage/ttf/$b" ;;
  esac
done
for f in fonts/otf/*.otf; do cp "$f" "$stage/otf/$(basename "$f")"; done
for f in fonts/*.woff2; do
  b=$(basename "$f")
  case "$b" in
    Vigil-wght-.woff2)        cp "$f" "$stage/variable/woff2/Vigil[wght].woff2" ;;
    Vigil-Italic-wght-.woff2) cp "$f" "$stage/variable/woff2/Vigil-Italic[wght].woff2" ;;
    VigilOutline-*)           cp "$f" "$stage/outline/woff2/$b" ;;
    *)                        cp "$f" "$stage/woff2/$b" ;;
  esac
done
cp downloads/src/README.md downloads/src/Vigil-specimen.html OFL.txt "$stage/"

# no folder may contain more than one format
while IFS= read -r d; do
  n=$(find "$d" -maxdepth 1 -type f -name '*.*' | sed 's/.*\.//' | sort -u | wc -l | tr -d ' ')
  [ "$n" -le 1 ] || { echo "mixed formats in ${d#$stage/}" >&2; exit 1; }
done < <(find "$stage" -mindepth 1 -type d)

rm -f "$out"
( cd "$stage" && zip -qr "$root/$out" . -x '.DS_Store' )
unzip -t "$out" >/dev/null
printf 'built %s  (%s KB)  ttf:%s otf:%s woff2:%s\n' "$out" \
  "$(( $(wc -c < "$out") / 1024 ))" \
  "$(unzip -l "$out" | grep -c '\.ttf$')" \
  "$(unzip -l "$out" | grep -c '\.otf$')" \
  "$(unzip -l "$out" | grep -c '\.woff2$')"
