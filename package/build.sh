#!/usr/bin/env bash
# Assembles the npm package from the site's canonical files, so the fonts have
# one source of truth and are not duplicated in git. Run from the repo root:
#   bash package/build.sh && npm publish ./package
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"; root="$(dirname "$here")"
rm -rf "$here/fonts"; mkdir -p "$here/fonts"
cp "$root"/fonts/*.woff2 "$here/fonts/"
cp "$root/vigil.css" "$root/OFL.txt" "$here/"
# rewrite absolute URLs to package-relative paths for the npm build
sed -i '' 's#https://www.vigilfont.com/fonts/#./fonts/#g' "$here/vigil.css"
echo "package assembled: $(ls "$here/fonts" | wc -l | tr -d ' ') font files"
