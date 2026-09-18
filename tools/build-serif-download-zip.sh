#!/usr/bin/env bash
# Rebuilds downloads/VigilSerif.zip entirely from files tracked in this repo,
# the way tools/build-download-zip.sh builds the sans's package.
#
#   bash tools/build-serif-download-zip.sh
#
# Sources:
#   fonts/serif/ttf/*.ttf      14 hinted statics + 2 variable
#   fonts/serif/woff2/*.woff2  the 14 statics for the web
#   fonts/VigilSerif-*-wght-.woff2   the two variable web fonts the site serves
#   downloads/src/serif/       Read me first.txt, OFL.txt, FONTLOG.txt
#
# The serif's OFL.txt and FONTLOG.txt are the serif repo's, not the sans's:
# they carry Vollkorn's copyright notice, which the license requires to
# travel with every copy. Never substitute the sans's OFL (Figtree) here.
#
# Same layout rules as the sans: the statics sit at the root so a non-technical
# person unzips, sees font files and double-clicks; everything else is demoted
# into folders, and no folder may mix formats (a folder of .ttf and .woff2
# handed Font Book web fonts it cannot install). Deterministic output: mtimes
# pinned, entries sorted, so the archive only changes when a file does.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
out="downloads/VigilSerif.zip"
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT

mkdir -p "$stage"/{"Variable font","Web fonts"}

for f in fonts/serif/ttf/*.ttf; do
  b=$(basename "$f")
  case "$b" in
    *'[wght]'*) : ;;                              # renamed below
    *)          cp "$f" "$stage/$b" ;;
  esac
done
cp "fonts/serif/ttf/VigilSerif[wght].ttf"        "$stage/Variable font/Vigil Serif Variable.ttf"
cp "fonts/serif/ttf/VigilSerif-Italic[wght].ttf" "$stage/Variable font/Vigil Serif Variable Italic.ttf"
for f in fonts/serif/woff2/*.woff2; do cp "$f" "$stage/Web fonts/$(basename "$f")"; done
cp fonts/VigilSerif-wght-.woff2        "$stage/Web fonts/VigilSerif-Variable.woff2"
cp fonts/VigilSerif-Italic-wght-.woff2 "$stage/Web fonts/VigilSerif-Variable-Italic.woff2"
cp "downloads/src/serif/Read me first.txt" downloads/src/serif/OFL.txt downloads/src/serif/FONTLOG.txt "$stage/"

# the license must be the serif's: refuse to build with the sans's OFL
grep -q 'Vollkorn' "$stage/OFL.txt" || { echo "OFL.txt is not the serif's (no Vollkorn notice)" >&2; exit 1; }
grep -q 'Figtree' "$stage/OFL.txt" && { echo "OFL.txt is the sans's (Figtree notice)" >&2; exit 1; }

# no folder may contain more than one format
while IFS= read -r d; do
  [ "$d" = "$stage" ] && continue
  n=$(find "$d" -maxdepth 1 -type f -name '*.*' | sed 's/.*\.//' | sort -u | wc -l | tr -d ' ')
  [ "$n" -le 1 ] || { echo "mixed formats in ${d#$stage/}" >&2; exit 1; }
done < <(find "$stage" -mindepth 1 -type d)

find "$stage" -exec touch -t 202609180000 {} +
rm -f "$out"
( cd "$stage" && find . -type f ! -name '.DS_Store' | LC_ALL=C sort | zip -qX "$root/$out" -@ )
unzip -t "$out" >/dev/null
printf 'built %s  (%s KB)  ttf:%s woff2:%s\n' "$out" \
  "$(( $(wc -c < "$out") / 1024 ))" \
  "$(unzip -l "$out" | grep -c '\.ttf$')" \
  "$(unzip -l "$out" | grep -c '\.woff2$')"
