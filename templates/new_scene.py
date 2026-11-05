"""Starter scene. Copy this file to scenes/<topic>_scene.py and edit the
sections marked CHANGE THIS.

Preview (fast, 480p):
    docker compose run --rm manim scenes/<topic>_scene.py MyScene -w -l --video_dir media
"""
from manimlib import *  # ManimGL, not Manim Community ("from manim import *")
import numpy as np

FONT = "DejaVu Sans"          # the font installed in the Docker image
BACKGROUND = "#0E0E14"        # dark background
COLORS = ["#4FC3F7", "#FF7043", "#9CCC65"]  # one color per group


class MyScene(Scene):  # CHANGE THIS: rename the class (it becomes the video filename)
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BACKGROUND))
        self.title = None
        self.caption = None

        # ---- CHANGE THIS: step 1 -------------------------------------------
        self.set_texts("1. The data", "Each dot is one observation")
        rng = np.random.RandomState(0)  # fixed seed: same video every render
        points = rng.randn(30, 2) * [2.5, 1.2]
        dots = VGroup(*[Dot([x, y, 0], radius=0.09, color=GREY_B) for x, y in points])
        self.play(LaggedStartMap(FadeIn, dots, lag_ratio=0.03, run_time=1.0))
        self.wait(0.8)

        # ---- CHANGE THIS: step 2 -------------------------------------------
        self.set_texts("2. Split into groups", "Left, middle and right of the plot")
        groups = np.digitize(points[:, 0], [-1.0, 1.0])  # 0, 1 or 2
        self.play(*[d.animate.set_color(COLORS[g]) for d, g in zip(dots, groups)], run_time=0.8)
        self.wait(0.8)

        # ---- CHANGE THIS: step 3 (emphasis) --------------------------------
        self.set_texts("3. Highlight one point", "Indicate draws attention to a single object")
        self.play(Indicate(dots[0], scale_factor=2.0, color=WHITE), run_time=1.0)
        self.wait(0.5)

        # ---- Ending ---------------------------------------------------------
        self.set_texts("Done", "Replace these steps with your own")
        self.wait(1.5)

    # Swaps the step title (top-left) and caption (bottom) in one animation.
    def set_texts(self, title, caption):
        new_title = Text(title, font=FONT, font_size=40, color=WHITE)
        new_title.to_corner(UL).shift(0.2 * RIGHT + 0.1 * DOWN)
        new_caption = Text(caption, font=FONT, font_size=30, color=GREY_B)
        new_caption.to_edge(DOWN, buff=0.5)
        anims = [FadeIn(new_title, shift=0.2 * UP), FadeIn(new_caption, shift=0.2 * DOWN)]
        if self.title is not None:
            anims += [FadeOut(self.title, shift=0.2 * UP), FadeOut(self.caption, shift=0.2 * DOWN)]
        self.play(*anims, run_time=0.4)
        self.title, self.caption = new_title, new_caption
