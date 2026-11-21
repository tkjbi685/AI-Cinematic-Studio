#!/usr/bin/env bash
set -euo pipefail

QUALITY="${1:-standard}"
TITLE="${2:-NEON RUN}"
case "$QUALITY" in draft) SOURCE_FPS=8 ;; standard) SOURCE_FPS=10 ;; high) SOURCE_FPS=12 ;; *) echo "Quality must be draft, standard, or high" >&2; exit 2 ;; esac

mkdir -p renders
blender --background --python scripts/create_scene.py -- \
  --output "$PWD/renders" --quality "$QUALITY" --title "$TITLE"
blender --background renders/cinematic.blend --render-output "$PWD/renders/frame_" --render-format PNG --render-anim
ffmpeg -y -framerate "$SOURCE_FPS" -i renders/frame_%04d.png \
  -vf "fps=24,format=yuv420p" -c:v libx264 -preset medium -crf 19 \
  -movflags +faststart -t 60 renders/cinematic.mp4
echo "Created: renders/cinematic.mp4"
