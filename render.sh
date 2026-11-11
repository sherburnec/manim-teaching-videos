#!/usr/bin/env bash
# Render a scene inside Docker. Works in Git Bash, macOS and Linux.
#   ./render.sh <file.py> <SceneClass> [low|hd]
# low (default) = 480p30 preview, hd = 1080p60. Output: media/<SceneClass>.mp4
set -euo pipefail
cd "$(dirname "$0")"

if [ $# -lt 2 ]; then
  echo "usage: ./render.sh <file.py> <SceneClass> [low|hd]" >&2
  exit 2
fi
file=$1; cls=$2; quality=${3:-low}

case "$quality" in
  low) qargs=(-w -l) ;;
  hd)  qargs=(-w --hd --config_file hd60_config.yml) ;;
  *)   echo "quality must be low or hd" >&2; exit 2 ;;
esac

# A timeout stops a hung render from blocking forever.
wrap=()
if command -v timeout >/dev/null 2>&1; then wrap=(timeout 1800); fi

"${wrap[@]}" docker compose run --rm manim "$file" "$cls" "${qargs[@]}" --video_dir media

if [ ! -s "media/$cls.mp4" ]; then
  echo "ERROR: media/$cls.mp4 was not created" >&2
  exit 1
fi
echo "OK: media/$cls.mp4"
