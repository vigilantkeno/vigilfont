#!/usr/bin/env bash
# Re-pull the homepage icons from vigilicons.com, which is the source of truth.
# These local copies exist so the homepage doesn't depend on another origin at
# render time — but that means they drift when the icon set is re-exported.
# Run this after any icon update:  bash icons/sync.sh
set -euo pipefail
cd "$(dirname "$0")"
for s in gaslighting narcissist mansplaining helicopter-parent deepfake people-pleaser; do
  curl -fsS "https://www.vigilicons.com/icons/svg/$s.svg" -o "$s.svg"
  printf '  %-20s %sB\n' "$s" "$(wc -c < "$s.svg" | tr -d ' ')"
done
echo "synced from vigilicons.com"
