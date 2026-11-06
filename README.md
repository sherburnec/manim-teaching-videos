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

Prefer to describe the video and let an AI write the code? See [Using an AI assistant](#using-an-ai-assistant-optional) below.

## Using an AI assistant (optional)

You don't need to write Python to use this toolkit. An AI coding assistant such as [Claude Code](https://claude.com/claude-code) can write the scene, render it in Docker, look at the result and fix problems while you focus on what the video should teach.

### What the assistant already knows

`CLAUDE.md` is a briefing file that Claude Code reads automatically when you open this folder. It tells the assistant:

- **Which library to use.** ManimGL (`from manimlib import *`), not the more common Manim Community Edition. Most online examples are for Manim Community, and mixing the two up is the most common cause of errors.
- **How to run things.** All rendering goes through `docker compose run ...`. Nothing gets installed on your computer.
- **Known pitfalls and their fixes.** No LaTeX, use `--config_file hd60_config.yml` instead of `--fps 60`, keep `init: true`, ManimGL has no `Star` class, how to keep things layered on top, and so on.
- **The house style.** Dark background, a step title top-left, a one-line caption at the bottom, an optional counter top-right, short text and brief pauses.
- **The workflow.** Work out the data in NumPy first, start from `templates/new_scene.py`, preview at low quality, check frames, then **stop and ask you to approve** before rendering the final 1080p version.
- **Ground rules.** Only edit files in this folder, ask before deleting anything or running anything outside Docker, and stop to ask if the same error comes back three times.

Other assistants (Cursor, Copilot, ChatGPT and so on) don't read `CLAUDE.md` by themselves, but it's plain text. Paste it in, or point the assistant at it, at the start of a session.

### Getting started

1. Finish the [Setup](#setup-once) steps above and make sure Docker Desktop is running.
2. Open a terminal in this folder and run `claude` (or open the folder in VS Code with the Claude Code extension).
3. Describe the video you want in plain language.

### Things you can ask for

**A new video from a topic**
> *"Make a 30-second video explaining linear regression, in the same style as the k-means one. Show the points, a bad first guess at the line, then the line moving to the best fit while the error shrinks."*

**A video for a specific class**
> *"My students are first-year nursing students with no maths background. Make a 1-minute video showing what a standard deviation is, using patient heart rates as the example. Avoid formulas on screen."*

**Changes to a preview**
> *"Slow down step 2, the caption at 0:12 overlaps the dots, and use orange instead of red for the outliers."*

**Turning your own data into a video**
> *"Here's a CSV of last term's quiz scores (`data/quiz.csv`). Make a short video that shows the distribution as a histogram and highlights the class average."*
>
> Copy the file into this folder first, because the container can only see files in here. Remove names or other personal information before you share it.

**Reusing an existing example**
> *"Make a version of FitScoreScene with 4 clusters instead of 3 and save it as a new scene, without changing the original."*

**Explaining the code**
> *"Walk me through `scenes/kmeans_scene.py`. Which parts would I change to show 5 clusters?"* This is useful if you want to learn ManimGL yourself.

**Fixing a problem**
> *"This render fails with a `NameError` and I don't know why. Here's the output: ..."* The assistant can read the error, check the ManimGL source inside the container, and fix the scene.

**Checking the output**
> *"Render the preview and check the frames for text that overlaps or runs off screen."* The assistant can make a contact sheet (a grid of stills from the video) with `ffmpeg` and look at it before you watch anything.

**Writing the narration**
> *"Write a 30-second voice-over script that matches the timing of each step in KMeansScene."* Useful if you plan to record narration over the video.

### What a session usually looks like

1. You describe the topic, audience, rough length and anything you want to see.
2. The assistant works out the data and steps, writes `scenes/<topic>_scene.py`, and renders a 480p preview.
3. It checks that the render worked (file exists, sensible length, no errors) and inspects stills from it.
4. It gives you the path to the preview, e.g. `media/RegressionScene.mp4`. You watch it and ask for changes.
5. When you're happy, you approve it and the assistant renders the 1080p 60 fps version and reports the resolution, length and file size.
6. It adds the new scene to the [example table](#example-videos) in this README.

### Tips for good results

- **Say who it's for and what they should take away.** "Explain gradient descent to Year 11 students who know what a slope is" works much better than "explain gradient descent".
- **Give a target length.** 30 seconds to 3 minutes suits this style. For longer topics, ask for a series of short videos.
- **Point at an example.** "Like KMeansScene" or "like the histogram part of FitScoreScene" gives the assistant a concrete style to copy.
- **Change one or two things per round.** Small, specific feedback ("the title at 0:08 is cut off") gets fixed faster than "make it better".
- **Ask for a new file** when you want a variation, so the working examples stay as they are.

### Things to check yourself

An AI assistant can write and debug the animation, but you are still the subject expert.

- **Check the content is correct.** Watch the whole video before showing it to a class. Make sure the definitions, numbers and simplifications are right for your course.
- **Check that it reads well.** Is the text big enough, and are the pauses long enough for your students?
- **Look at commands before approving them.** The assistant should only run `docker compose ...` commands for rendering. If it suggests installing software on your computer or deleting files outside this folder, say no and ask why.
- **Be careful with student data.** Only share data you are allowed to share, and remove personal information first.

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
