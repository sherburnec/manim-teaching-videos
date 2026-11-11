# ManimGL scene guide (for any AI model)

Use this when your assistant cannot read the repo (a chat window, for example). Paste this file and `templates/new_scene.py` into the chat, then add your request using the prompt template at the bottom.

## Rules
- Library: **ManimGL** (`from manimlib import *`). **Not** Manim Community Edition (`from manim import *`). The two have different APIs, and most examples online are for Community Edition.
- Use `Text(...)`, never `Tex(...)` or `MathTex(...)`. There is no LaTeX in the image. Always pass `font="DejaVu Sans"`.
- Version is ManimGL 1.7.2. There is no `Star` class (build one from `Polygon`).
- Background: `self.camera.background_rgba = list(color_to_rgba("#0E0E14"))` at the top of `construct`.
- Layering: animating a mobject re-adds it on top. Use `mobj.set_z_index(10)` to keep it above others.
- Use a fixed seed (`np.random.RandomState(0)`), so every render is identical.
- Class name = output filename (`<SceneClass>.mp4`).
- Do the maths in NumPy first, then animate from the precomputed data so the visuals match the real algorithm.

## Style
- Dark background, short text only: step title top-left, one-line caption at the bottom, optional counter top-right.
- Swap title and caption together in one 0.4 s animation (`set_texts` in the template). Hold 0.5 to 1 s at key moments.
- Target 30 s to 3 min. One idea per video.

## Where to put the result and how to render it
Save the scene as `local/<topic>_scene.py` (this folder is git-ignored), then run from the project folder:

    ./render.sh local/<topic>_scene.py <SceneClass>        # preview (480p30)
    ./check.sh <SceneClass>                                # details + contact sheet
    ./render.sh local/<topic>_scene.py <SceneClass> hd     # final (1080p60), after you approve the preview

On Windows PowerShell use `.\render.ps1` and `.\check.ps1` instead.

If a render fails, paste the last 30 lines of the output back to the assistant.

## Prompt template
> You are writing a ManimGL 1.7.2 scene (`from manimlib import *`, not Manim Community). Follow the attached guide and start from the attached template.
> **Topic:** ...
> **Audience:** ...
> **Length:** ... seconds
> **What I want to see:** ...
> Return one complete Python file. Put the data/maths in NumPy with a fixed seed. Keep on-screen text short.
