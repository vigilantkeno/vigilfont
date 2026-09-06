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

mkdir -p "$stage"/{"Variable font","Web fonts","Extras/OTF","Extras/Outline"}

# The 16 statics sit at the ROOT. A non-technical person unzips, sees font
# files, double-clicks. Nothing to navigate. This is the Inter/rsms layout and
# it is why their package installs cleanly for people who have never installed
# a font before. Everything else is demoted.
for f in fonts/ttf/*.ttf; do
  b=$(basename "$f")
  case "$b" in
    *'[wght]'*)     : ;;                      # handled below, renamed
    VigilOutline-*) cp "$f" "$stage/Extras/Outline/$b" ;;
    *)              cp "$f" "$stage/$b" ;;
  esac
done
# Square brackets read as machine output. "Vigil Variable.ttf" reads as a font.
cp "fonts/ttf/Vigil[wght].ttf"        "$stage/Variable font/Vigil Variable.ttf"
cp "fonts/ttf/Vigil-Italic[wght].ttf" "$stage/Variable font/Vigil Variable Italic.ttf"
for f in fonts/otf/*.otf; do cp "$f" "$stage/Extras/OTF/$(basename "$f")"; done
for f in fonts/*.woff2; do
  b=$(basename "$f")
  case "$b" in
    Vigil-wght-.woff2)        cp "$f" "$stage/Web fonts/Vigil-Variable.woff2" ;;
    Vigil-Italic-wght-.woff2) cp "$f" "$stage/Web fonts/Vigil-Variable-Italic.woff2" ;;
    *)                        cp "$f" "$stage/Web fonts/$b" ;;
  esac
done
cp "downloads/src/Read me first.txt" "$stage/"
cp downloads/src/Vigil-specimen.html "$stage/Vigil specimen.html"
cp OFL.txt "$stage/"

# no folder may contain more than one format
while IFS= read -r d; do
  [ "$d" = "$stage" ] && continue
  n=$(find "$d" -maxdepth 1 -type f -name '*.*' | sed 's/.*\.//' | sort -u | wc -l | tr -d ' ')
  [ "$n" -le 1 ] || { echo "mixed formats in ${d#$stage/}" >&2; exit 1; }
done < <(find "$stage" -mindepth 1 -type d)

# Deterministic output: zip records each entry's mtime, so without this the
# archive differs on every run and shows up as a modified binary in git even
# when nothing changed. Pin mtimes and sort the entry order; -X drops extra
# platform attributes.
find "$stage" -exec touch -t 202609040000 {} +
rm -f "$out"
( cd "$stage" && find . -type f ! -name '.DS_Store' | LC_ALL=C sort | zip -qX "$root/$out" -@ )
unzip -t "$out" >/dev/null
printf 'built %s  (%s KB)  ttf:%s otf:%s woff2:%s\n' "$out" \
  "$(( $(wc -c < "$out") / 1024 ))" \
  "$(unzip -l "$out" | grep -c '\.ttf$')" \
  "$(unzip -l "$out" | grep -c '\.otf$')" \
  "$(unzip -l "$out" | grep -c '\.woff2$')"
