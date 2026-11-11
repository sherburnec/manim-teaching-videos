# AGENTS.md: ManimGL video pipeline

Instructions for any AI coding assistant (Claude Code, Gemini CLI, GitHub Copilot, Codex, Cursor, ...). `CLAUDE.md`, `GEMINI.md` and `.github/copilot-instructions.md` all point here, so edit this file only.

This folder holds a working, Dockerized ManimGL (3Blue1Brown's library) setup that produced the example videos in `scenes/` (`kmeans_scene.py` / `KMeansScene`, `fitscore_scene.py` / `FitScoreScene`). Reuse the setup. Do not rebuild it from scratch.

## Hard rules
- Use **ManimGL** (`pip install manimgl`, `from manimlib import *`, CLI `manimgl`). **Never Manim Community Edition** (`from manim import *`). Most online examples and most model training data are Community Edition, so this is the most common mistake. The APIs differ, so check the installed source in the container before using a class, e.g. `/usr/local/lib/python3.11/site-packages/manimlib/`.
- Everything builds and renders **inside Docker**. Never install manim, ffmpeg or LaTeX on the host, and never run Python on the host.
- Prefer `Text` over `Tex` (no LaTeX in the image). Always pass `font="DejaVu Sans"`, the font installed in the image.
- Don't run a blanket `docker rm -f` over all containers. Only touch this project's containers (`docker compose ps -a`).
- Making a video must never create or modify tracked files. New scenes go in `local/` (git-ignored). Don't touch `scenes/` or `README.md` unless the user explicitly asks to publish a scene.

## Files
- `Dockerfile`: python:3.11-slim-bookworm + ffmpeg, xvfb, Mesa, pango/cairo, `pip install manimgl`.
- `docker-compose.yml`: mounts `.` at `/manim`, entrypoint `sh /manim/run.sh`, **`init: true` is required**.
- `run.sh`: container entrypoint. `exec xvfb-run -a -s "-screen 0 1920x1080x24" manimgl "$@"`. This is the headless-OpenGL trick (xvfb plus software Mesa).
- `render.sh` / `render.ps1`: host helpers that wrap the Docker render commands (see Commands).
- `check.sh` / `check.ps1`: host helpers that run ffprobe and build a contact sheet.
- `hd60_config.yml`: `camera: fps: 60`, used for HD renders (see gotchas).
- `smoke_test.py`: tiny scene for checking the setup.
- `scenes/`: tracked example videos only. `local/`: git-ignored, where new scenes go. `templates/new_scene.py`: starter scene. `docs/scene-guide.md`: tool-neutral ManimGL guide and prompt template. `README.md`: user guide. `media/` gets the output (mounted, git-ignored).

## Commands (run from this folder)
Use the helper scripts. Bash / Git Bash / macOS / Linux use `./render.sh`, Windows PowerShell uses `.\render.ps1`.

    docker compose build                                   # once
    ./render.sh smoke_test.py SmokeScene                   # check the setup
    ./render.sh local/<topic>_scene.py <SceneClass>        # low quality (480p30), the default
    ./render.sh local/<topic>_scene.py <SceneClass> hd     # 1080p60
    ./check.sh <SceneClass>                                # ffprobe + media/<SceneClass>_contact.png

The scripts expand to this (use it directly if scripts can't run):

    docker compose run --rm manim <file>.py <SceneClass> -w -l --video_dir media
    docker compose run --rm manim <file>.py <SceneClass> -w --hd --config_file hd60_config.yml --video_dir media

Run other tools (ffmpeg, python) in the container with `docker compose run --rm -T --entrypoint <tool> manim ...`. You can pipe a script in via stdin (`--entrypoint python manim - < script.py`).

## Gotchas already solved
- **Render hangs forever with no output:** `xvfb-run` was PID 1 and never got Xvfb's startup signal. The fix is `init: true` in compose. Keep it.
- **`--fps 60` crashes** (`TypeError: int / str`) in ManimGL 1.7.2. Use `--config_file hd60_config.yml` instead.
- `import manimlib` outside xvfb fails with `NoSuchDisplayException`. Inspect the source with grep/sed on the site-packages path instead.
- No `Star` class in 1.7.2. Build one with `Polygon` (see `make_star` in `scenes/kmeans_scene.py`).
- Default background is `#333333`. For darker, set `self.camera.background_rgba = list(color_to_rgba("#0E0E14"))` at the top of `construct`.
- **Layering:** animating a mobject re-adds it on top of others. To keep something always on top, call `mobj.set_z_index(10)` (Scene.add sorts by z_index).
- Output filename is `<SceneClass>.mp4`, so an HD render overwrites the low-quality one. Add `--file_name` if both are needed.
- Docker Desktop on Windows: use Git Bash or PowerShell with relative paths. Wrap renders in a timeout so a hang can't block the session (`render.sh` does this).

## Capability tiers
Adapt to what you can do in this session:
1. **Shell access:** run the whole workflow below yourself.
2. **No shell (chat only):** write the scene to `local/<topic>_scene.py` (or as a code block), then give the user the exact `./render.sh` / `.\render.ps1` command. Ask them to paste back any error output or describe what they see.
3. **No repo access:** the user pastes `docs/scene-guide.md` plus `templates/new_scene.py` into the chat. Follow it, and return one complete scene file.

## Workflow that worked
1. Do the data/algorithm work in plain NumPy first (inside the container). Precompute per-step state, then animate from that data so visuals match the real algorithm. Pick a **fixed seed** and search seeds for an interesting story rather than accepting the first.
2. Write the scene in a new `local/<topic>_scene.py` (create the folder if missing), starting from `templates/new_scene.py`. Don't edit the example scenes for other videos. Reuse its patterns: the `set_texts` helper (title + caption + optional counter swapped in one `play`), consistent per-category color lists, `Flash`/`Indicate` for emphasis.
3. Render **low quality only** while iterating. After each render run `./check.sh <SceneClass>` and read the console for `Traceback`/`Error`. Confirm the mp4 exists and the duration and size are sensible.
4. Inspect frames, not just metadata: view `media/<SceneClass>_contact.png`. This catches text overlaps, a mis-positioned title, and layering bugs. If you cannot view images, skip this and ask the user to open the contact sheet or watch the preview and report problems.
5. **Checkpoint:** when the low-quality render looks finished, stop and ask the user to approve, and give them the file path. Only after approval render the HD version and report path, resolution, duration and size.
6. Do NOT touch `README.md` or `scenes/` as part of making a video. Only if the user asks to publish a scene: move it from `local/` to `scenes/` and add it to the README example table.

## Style used for the k-means video (follow unless the user says otherwise)
- Dark background, short on-screen text only: a step title (top-left), a one-line caption (bottom), and a small counter (top-right).
- Smooth transitions with brief holds. The final video was about 29s. Short pacing (0.4s text swaps) plus 0.5-1s holds at key moments worked well.
- If time is tight, show detail once (e.g. one-cluster-at-a-time on the first loop) and run later loops faster with all parts together.

## Constraints from the original brief
Only create/edit files inside this folder, ask before deleting any file or running anything outside Docker, and if the same error persists after 3 fix attempts, stop and ask rather than looping. Confirm with the user whether these still apply to the new video.
