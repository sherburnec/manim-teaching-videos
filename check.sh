#!/usr/bin/env bash
# Inspect a rendered video: prints resolution, fps, duration, size, and writes
# a contact sheet (grid of stills) to media/<SceneClass>_contact.png.
#   ./check.sh <SceneClass>
set -euo pipefail
cd "$(dirname "$0")"

if [ $# -lt 1 ]; then
  echo "usage: ./check.sh <SceneClass>" >&2
  exit 2
fi
cls=$1
video="media/$cls.mp4"
[ -s "$video" ] || { echo "ERROR: $video not found" >&2; exit 1; }

docker compose run --rm -T --entrypoint ffprobe manim -v error \
  -show_entries stream=width,height,r_frame_rate:format=duration,size \
  -of default=nw=1 "$video"

docker compose run --rm -T --entrypoint ffmpeg manim -y -v error -i "$video" \
  -vf "fps=1/2.2,scale=427:-1,tile=4x3" -frames:v 1 "media/${cls}_contact.png"
echo "Contact sheet: media/${cls}_contact.png"
