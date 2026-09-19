#!/usr/bin/env bash
# Assembles the npm package from the site's canonical files, so the fonts have
# one source of truth and are not duplicated in git. Run from the repo root:
#   bash package/build.sh && npm publish ./package
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"; root="$(dirname "$here")"
rm -rf "$here/fonts"; mkdir -p "$here/fonts"
cp "$root"/fonts/*.woff2 "$here/fonts/"
cp "$root/vigil.css" "$here/"
# The package carries both families, so its licence file has to name both
# upstreams. The site's own OFL.txt covers Figtree only; the serif's files are
# derived from Vollkorn, and OFL 1.1 condition 2 wants the copyright notice and
# the licence travelling with every copy. Each font carries its own notice in
# nameID 0 already; this makes the accompanying file agree with them.
{
  echo "Copyright 2026 Joaquin Keno Vigil (https://www.vigilfont.com)"
  echo
  echo "Vigil and Vigil Outline are derived from Figtree:"
  echo "Copyright 2022 The Figtree Project Authors (https://github.com/erikdkennedy/figtree)"
  echo
  echo "Vigil Serif is derived from Vollkorn:"
  echo "Copyright 2017 The Vollkorn Project Authors (https://github.com/FAlthausen/Vollkorn-Typeface)"
  echo
  tail -n +4 "$root/OFL.txt"
} > "$here/OFL.txt"
# rewrite absolute URLs to package-relative paths for the npm build
sed -i '' 's#https://www.vigilfont.com/fonts/#./fonts/#g' "$here/vigil.css"
echo "package assembled: $(ls "$here/fonts" | wc -l | tr -d ' ') font files"
