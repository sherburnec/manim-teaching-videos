from manimlib import *
import numpy as np

K = 3
DATA_SEED = 9
CENTROID_SEED = 6
FONT = "DejaVu Sans"

NEUTRAL = "#9AA0A6"
CLUSTER_COLORS = ["#4FC3F7", "#FF7043", "#9CCC65"]
BLOB_CENTERS = np.array([[-4.2, -0.9], [0.3, 1.0], [4.2, -1.0]])
BLOB_SPREAD = np.array([0.85, 0.6])


def make_points():
    rng = np.random.RandomState(DATA_SEED)
    pts = np.vstack([c + rng.randn(25, 2) * BLOB_SPREAD for c in BLOB_CENTERS])
    return np.clip(pts, [-6.2, -2.5], [6.2, 2.5])


def run_kmeans(points):
    """Return (centroids, assignments), where centroids[i] is the set of
    centroids used to compute assignments[i]."""
    rng = np.random.RandomState(CENTROID_SEED)
    cent = np.c_[rng.uniform(-5.5, 5.5, K), rng.uniform(-2, 2, K)]
    cents, assigns = [], []
    prev = None
    while True:
        dist = np.linalg.norm(points[:, None] - cent[None], axis=2)
        assign = dist.argmin(axis=1)
        cents.append(cent.copy())
        assigns.append(assign)
        if prev is not None and (assign == prev).all():
            break
        prev = assign
        cent = np.array([points[assign == k].mean(axis=0) for k in range(K)])
    return cents, assigns


def to3d(p):
    return np.array([p[0], p[1], 0.0])


def make_star(color):
    pts = []
    for i in range(10):
        r = 0.32 if i % 2 == 0 else 0.14
        a = PI / 2 + i * PI / 5
        pts.append(np.array([r * np.cos(a), r * np.sin(a), 0]))
    star = Polygon(*pts)
    star.set_fill(color, opacity=1)
    star.set_stroke(WHITE, width=2.5)
    star.set_z_index(10)
    return star


class KMeansScene(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba("#0E0E14"))
        points = make_points()
        cents, assigns = run_kmeans(points)
        n_iter = len(assigns)

        dots = VGroup(*[Dot(to3d(p), radius=0.09) for p in points])
        dots.set_color(NEUTRAL)
        stars = [make_star(CLUSTER_COLORS[k]) for k in range(K)]
        for k in range(K):
            stars[k].move_to(to3d(cents[0][k]))

        # ---- persistent text -------------------------------------------
        self.title = None
        self.caption = None
        self.counter = None

        # ---- Step 1: choose k -------------------------------------------
        self.set_texts("1. Pick k", "k is a guess we make up front")
        self.play(LaggedStartMap(FadeIn, dots, lag_ratio=0.02, run_time=1.0))
        k_label = Text("k = 3", font=FONT, font_size=40, t2c={"3": YELLOW})
        k_label.to_corner(UR).shift(0.2 * LEFT + 0.1 * DOWN)
        self.play(Write(k_label), run_time=0.4)
        self.wait(0.9)

        # ---- Step 2: random centroids -----------------------------------
        self.set_texts("2. Place centroids randomly", "Drop k centroids at random positions")
        self.play(*[GrowFromCenter(s) for s in stars], run_time=0.5)
        self.play(*[Flash(s, color=CLUSTER_COLORS[k], flash_radius=0.6, run_time=0.6) for k, s in enumerate(stars)])
        self.wait(0.7)

        # ---- Step 3: assign ---------------------------------------------
        self.set_texts("3. Assign each point", "Each point joins its closest centroid", counter=(1, k_label))
        self.show_distances(points, cents[0], assigns[0], dots, stars, samples=[0, 30, 60])
        self.recolor_all(dots, assigns[0])
        self.wait(0.7)

        # ---- Steps 4 & 5, repeated until nothing changes ----------------
        for i in range(1, n_iter):
            first = i == 1
            self.set_texts("4. Update centroids", "centroid = mean of cluster points", counter=(i + 1, k_label))
            self.update_centroids(points, dots, stars, assigns[i - 1], cents[i], one_by_one=first)

            title5 = "5. Reassign points" if first else "Repeat: reassign points"
            changed = np.where(assigns[i] != assigns[i - 1])[0]
            if len(changed) == 0:
                self.set_texts(title5, "No point changed cluster")
                self.wait(0.5)
                break
            self.set_texts(title5, f"{len(changed)} point{'s' if len(changed) > 1 else ''} switch to a nearer centroid")
            self.reassign(dots, assigns[i], changed)
            self.wait(0.7 if first else 0.2)

        # ---- Converged ---------------------------------------------------
        self.set_texts("Done", "Assignments stopped changing")
        done = Text("Converged!", font=FONT, font_size=60, color=YELLOW)
        done.move_to(3.35 * UP)
        done.set_backstroke(BLACK, 8)
        self.play(Write(done), *[Indicate(s, scale_factor=1.5) for s in stars], run_time=1.0)
        self.wait(2.2)

    # ------------------------------------------------------------------
    def set_texts(self, title, caption, counter=None):
        new_title = Text(title, font=FONT, font_size=40, color=WHITE)
        new_title.to_corner(UL).shift(0.2 * RIGHT + 0.1 * DOWN)
        new_caption = Text(caption, font=FONT, font_size=30, color=GREY_B)
        new_caption.to_edge(DOWN, buff=0.5)
        anims = []
        if self.title is not None:
            anims += [FadeOut(self.title, shift=0.2 * UP), FadeOut(self.caption, shift=0.2 * DOWN)]
        anims += [FadeIn(new_title, shift=0.2 * UP), FadeIn(new_caption, shift=0.2 * DOWN)]
        if counter is not None:
            n, below = counter
            new_counter = Text(f"Iteration {n}", font=FONT, font_size=30, color=GREY_B)
            new_counter.next_to(below, DOWN, aligned_edge=RIGHT, buff=0.25)
            if self.counter is not None:
                anims.append(FadeOut(self.counter))
            anims.append(FadeIn(new_counter))
            self.counter = new_counter
        self.play(*anims, run_time=0.4)
        self.title, self.caption = new_title, new_caption

    def show_distances(self, points, cent, assign, dots, stars, samples):
        for idx_n, idx in enumerate(samples):
            first = idx_n == 0
            p = dots[idx].get_center()
            lines = VGroup(*[
                Line(p, stars[k].get_center(), stroke_width=2, color=CLUSTER_COLORS[k]).set_opacity(0.8)
                for k in range(K)
            ])
            self.play(dots[idx].animate.scale(1.8).set_color(WHITE), ShowCreation(lines, lag_ratio=0.3), run_time=0.7 if first else 0.4)
            best = assign[idx]
            others = [lines[k] for k in range(K) if k != best]
            self.play(
                *[FadeOut(l) for l in others],
                lines[best].animate.set_stroke(width=5).set_opacity(1),
                run_time=0.3 if first else 0.25,
            )
            self.wait(0.3 if first else 0.1)
            self.play(FadeOut(lines[best]), dots[idx].animate.scale(1 / 1.8), run_time=0.3 if first else 0.25)
            dots[idx].set_color(NEUTRAL)

    def recolor_all(self, dots, assign):
        self.play(
            LaggedStart(*[
                d.animate.set_color(CLUSTER_COLORS[assign[j]]) for j, d in enumerate(dots)
            ], lag_ratio=0.01, run_time=0.8)
        )

    def update_centroids(self, points, dots, stars, assign, new_cent, one_by_one):
        groups = [VGroup(*[dots[j] for j in np.where(assign == k)[0]]) for k in range(K)]
        trails = [
            DashedLine(stars[k].get_center(), to3d(new_cent[k]), color=CLUSTER_COLORS[k], stroke_width=2)
            for k in range(K)
        ]
        if one_by_one:
            for k in range(K):
                others = VGroup(*[dots[j] for j in np.where(assign != k)[0]])
                self.play(
                    others.animate.set_opacity(0.15),
                    groups[k].animate.scale(1.35),
                    Flash(groups[k], color=CLUSTER_COLORS[k], flash_radius=1.6, line_length=0.3, run_time=0.5),
                    run_time=0.5,
                )
                self.add(trails[k])
                self.play(stars[k].animate.move_to(to3d(new_cent[k])), run_time=0.6)
                self.play(
                    others.animate.set_opacity(1.0),
                    groups[k].animate.scale(1 / 1.35),
                    FadeOut(trails[k]),
                    run_time=0.3,
                )
        else:
            self.play(*[ShowCreation(t) for t in trails], run_time=0.2)
            self.play(*[stars[k].animate.move_to(to3d(new_cent[k])) for k in range(K)], run_time=0.7)
            self.play(*[FadeOut(t) for t in trails], run_time=0.2)

    def reassign(self, dots, new_assign, changed):
        self.play(
            *[Flash(dots[j], color=WHITE, flash_radius=0.4, line_length=0.15, run_time=0.8) for j in changed],
            *[dots[j].animate.set_color(CLUSTER_COLORS[new_assign[j]]) for j in changed],
            run_time=0.8,
        )
