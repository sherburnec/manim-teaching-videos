# Manim Teaching Videos

Make short, clean animated explainer videos for your classes. Everything runs inside Docker, so you don't need to install Python or anything else on your computer.

Built on [ManimGL](https://github.com/3b1b/manim), the animation library behind 3Blue1Brown.

## Example videos

| File | Scene | What it teaches | Length |
|---|---|---|---|
| `scenes/kmeans_scene.py` | `KMeansScene` | How k-means clustering works, step by step | ~30 s |
| `scenes/fitscore_scene.py` | `FitScoreScene` | Using distance to the centroid as a "fit score" to flag outliers | ~3 min |

Finished renders are attached to this repo's **Releases** page (if the maintainer uploaded them).

## Setup (once)

1. Install and start [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. Download this repo (green **Code** button → *Download ZIP*, or `git clone`), then open a terminal (PowerShell, Terminal or Git Bash) in the folder.
3. Build the image (takes about 5 minutes the first time):

       docker compose build

4. Check that it works:

       docker compose run --rm manim smoke_test.py SmokeScene -w -l --video_dir media

   You should now have `media/SmokeScene.mp4`.

## Render a video

Quick preview (480p, 30 fps):

    docker compose run --rm manim scenes/kmeans_scene.py KMeansScene -w -l --video_dir media

Final quality (1080p, 60 fps):

    docker compose run --rm manim scenes/kmeans_scene.py KMeansScene -w --hd --config_file hd60_config.yml --video_dir media

The video is saved as `media/<SceneName>.mp4`. The pattern is always `<file> <SceneName>`, so swap in `scenes/fitscore_scene.py FitScoreScene` for the other example.

## Make your own video

1. **Copy the template:** copy `templates/new_scene.py` to `scenes/<topic>_scene.py`, e.g. `scenes/regression_scene.py`.
2. **Rename the class:** change `class MyScene` to a name like `class RegressionScene`.
3. **Edit the steps:** replace the sections marked `CHANGE THIS`. Each step calls `self.set_texts("Title", "Caption")` and then animates something.
4. **Preview and repeat:**

       docker compose run --rm manim scenes/regression_scene.py RegressionScene -w -l --video_dir media

5. **Render the final version** with the 1080p command above.

You can borrow patterns from the examples:
- `kmeans_scene.py`: dots, moving markers, step titles, an iteration counter.
- `fitscore_scene.py`: data in a separate file (`fitscore_data.py`), histograms, thresholds, labels.

The [ManimGL docs](https://3b1b.github.io/manim/) list every shape and animation.

### Using an AI assistant (optional)

`CLAUDE.md` describes this setup for [Claude Code](https://claude.com/claude-code). Open the folder with it and describe the video you want, for example: *"Make a 30-second video explaining linear regression, in the same style as the k-means one."*

## Tips

- Use `Text(...)`, not `Tex(...)`. LaTeX isn't installed in the image. Always pass `font="DejaVu Sans"`.
- Keep on-screen text short: a step title, a one-line caption and brief pauses (`self.wait(0.8)`).
- The final render overwrites the preview, because both are named after the scene. Add `--file_name MyName` to keep both.
- Use a fixed random seed (`np.random.RandomState(0)`) so every render looks the same.

## Troubleshooting

| Problem | Fix |
|---|---|
| `error during connect ... docker daemon is not running` | Start Docker Desktop and wait until it says *Running*. |
| `sh: ... not found` or `$'\r'` errors | `run.sh` got Windows line endings. Re-download the repo, or save `run.sh` with LF endings. |
| Render seems to hang with no output | Make sure `init: true` is still in `docker-compose.yml`. |
| `TypeError` when using `--fps 60` | That flag is broken in ManimGL 1.7.2. Use `--config_file hd60_config.yml` instead. |
| `NameError` for a class like `Star` | ManimGL's names differ from Manim Community. Check the [ManimGL docs](https://3b1b.github.io/manim/). |

## License

MIT. See [LICENSE](LICENSE).
