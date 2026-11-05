# CLAUDE.md: ManimGL video pipeline

This folder holds a working, Dockerized ManimGL (3Blue1Brown's library) setup that produced the example videos in `scenes/` (`kmeans_scene.py` / `KMeansScene`, `fitscore_scene.py` / `FitScoreScene`). Reuse the setup. Do not rebuild it from scratch.

## Hard rules
- Use **ManimGL** (`pip install manimgl`, `from manimlib import *`, CLI `manimgl`). Never Manim Community Edition (`from manim import *`). The APIs differ, so check the installed source in the container before using a class, e.g. `/usr/local/lib/python3.11/site-packages/manimlib/`.
- Everything builds and renders **inside Docker**. Never install manim, ffmpeg or LaTeX on the host, and never run Python on the host.
- Prefer `Text` over `Tex` (no LaTeX in the image). Always pass `font="DejaVu Sans"`, the font installed in the image.
- Don't run a blanket `docker rm -f` over all containers. Only touch this project's containers (`docker compose ps -a`).

## Files
- `Dockerfile`: python:3.11-slim-bookworm + ffmpeg, xvfb, Mesa, pango/cairo, `pip install manimgl`.
- `docker-compose.yml`: mounts `.` at `/manim`, entrypoint `sh /manim/run.sh`, **`init: true` is required**.
- `run.sh`: `exec xvfb-run -a -s "-screen 0 1920x1080x24" manimgl "$@"`. This is the headless-OpenGL trick (xvfb plus software Mesa).
- `hd60_config.yml`: `camera: fps: 60`, used for HD renders (see gotchas).
- `smoke_test.py`: tiny scene for checking the setup.
- `scenes/`: example videos. `templates/new_scene.py`: starter scene. `README.md`: user guide. `media/` gets the output (mounted, git-ignored).

## Commands (run from this folder)
    docker compose build                       # once
    docker compose run --rm manim smoke_test.py SmokeScene -w -l --video_dir media
    docker compose run --rm manim <file>.py <SceneClass> -w -l --video_dir media                                   # low quality (480p30)
    docker compose run --rm manim <file>.py <SceneClass> -w --hd --config_file hd60_config.yml --video_dir media   # 1080p60
Check output with: `docker compose run --rm -T --entrypoint ffprobe manim -v error -show_entries stream=width,height,r_frame_rate:format=duration,size -of default=nw=1 media/<SceneClass>.mp4`
Run other tools (ffmpeg, python) in the container with `docker compose run --rm -T --entrypoint <tool> manim ...`. You can pipe a script in via stdin (`--entrypoint python manim - < script.py`).

## Gotchas already solved
- **Render hangs forever with no output:** `xvfb-run` was PID 1 and never got Xvfb's startup signal. The fix is `init: true` in compose. Keep it.
- **`--fps 60` crashes** (`TypeError: int / str`) in ManimGL 1.7.2. Use `--config_file hd60_config.yml` instead.
- `import manimlib` outside xvfb fails with `NoSuchDisplayException`. Inspect the source with grep/sed on the site-packages path instead.
- No `Star` class in 1.7.2. Build one with `Polygon` (see `make_star` in `scenes/kmeans_scene.py`).
- Default background is `#333333`. For darker, set `self.camera.background_rgba = list(color_to_rgba("#0E0E14"))` at the top of `construct`.
- **Layering:** animating a mobject re-adds it on top of others. To keep something always on top, call `mobj.set_z_index(10)` (Scene.add sorts by z_index).
- Output filename is `<SceneClass>.mp4`, so an HD render overwrites the low-quality one. Add `--file_name` if both are needed.
- Docker Desktop on Windows: use Git Bash or PowerShell with relative paths. Add `timeout` around renders so a hang can't block the session.

## Workflow that worked
1. Do the data/algorithm work in plain NumPy first (inside the container). Precompute per-step state, then animate from that data so visuals match the real algorithm. Pick a **fixed seed** and search seeds for an interesting story rather than accepting the first.
2. Write the scene in a new `scenes/<topic>_scene.py`, starting from `templates/new_scene.py`. Don't edit the example scenes for other videos. Reuse its patterns: the `set_texts` helper (title + caption + optional counter swapped in one `play`), consistent per-category color lists, `Flash`/`Indicate` for emphasis.
3. Render **low quality only** while iterating. After each render check that the mp4 exists, then check duration and size with ffprobe and read the console for `Traceback`/`Error`.
4. Inspect frames, not just metadata: `ffmpeg -i media/X.mp4 -vf "fps=1/2.2,scale=427:-1,tile=4x3" -frames:v 1 media/contact.png`, then view the PNG. This caught text overlaps, a mis-positioned title, and layering bugs.
5. **Checkpoint:** when the low-quality render looks finished, stop and ask the user to approve, and give them the file path. Only after approval render the HD version and report path, resolution, duration and size.
6. Add any new scene to the example table in `README.md`.

## Style used for the k-means video (follow unless the user says otherwise)
- Dark background, short on-screen text only: a step title (top-left), a one-line caption (bottom), and a small counter (top-right).
- Smooth transitions with brief holds. The final video was about 29s. Short pacing (0.4s text swaps) plus 0.5-1s holds at key moments worked well.
- If time is tight, show detail once (e.g. one-cluster-at-a-time on the first loop) and run later loops faster with all parts together.

## Constraints from the original brief
Only create/edit files inside this folder, ask before deleting any file or running anything outside Docker, and if the same error persists after 3 fix attempts, stop and ask rather than looping. Confirm with the user whether these still apply to the new video.
