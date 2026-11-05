from manimlib import *
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fitscore_data import (
    K, N_SIGMA, BLOB_N, N_STRAY, make_points, run_kmeans, fit_scores, threshold,
)

DATA_SEED = 38
CENTROID_SEED = 15
FONT = "DejaVu Sans"

BG = "#0E0E14"
NEUTRAL = "#9AA0A6"
CLUSTER_COLORS = ["#4FC3F7", "#FFB74D", "#9CCC65"]
FLAG = "#FF3B3B"

N_BLOB_PTS = BLOB_N * K
N_BINS = 14
BIN_MAX = 3.5  # histogram x-range (distance units)


def to3d(p):
    return np.array([p[0], p[1], 0.0])


def make_star(color):
    pts = []
    for i in range(10):
        r = 0.30 if i % 2 == 0 else 0.13
        a = PI / 2 + i * PI / 5
        pts.append(np.array([r * np.cos(a), r * np.sin(a), 0]))
    star = Polygon(*pts)
    star.set_fill(color, opacity=1)
    star.set_stroke(WHITE, width=2.5)
    star.set_z_index(10)
    return star


def txt(s, size=30, color=WHITE, **kw):
    return Text(s, font=FONT, font_size=size, color=color, **kw)


def dist_color(d, thr):
    """Cool-to-hot colour for a fit score: near 0 is calm, near thr is warm."""
    return interpolate_color("#6FA8DC", "#FFD166", min(d / thr, 1.0))


class FitScoreScene(Scene):
    # ------------------------------------------------------------ setup --
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BG))
        self.points = make_points(DATA_SEED)
        self.cents, self.assigns = run_kmeans(self.points, CENTROID_SEED)
        self.final_c, self.final_a = self.cents[-1], self.assigns[-1]
        self.dist = fit_scores(self.points, self.final_c, self.final_a)
        self.thr = threshold(self.dist)
        self.flagged = np.where(self.dist > self.thr)[0]
        self.title = self.caption = self.counter = None
        # world -> screen: pos = origin + sc * data
        self.origin = np.zeros(3)
        self.sc = 1.0

        self.intro()
        self.kmeans_section()
        self.fit_score_section()
        self.real_world_section()

    def P(self, p):
        return self.origin + self.sc * to3d(p)

    # ---------------------------------------------------- text helpers --
    def set_texts(self, title, caption, run_time=0.5):
        new_title = txt(title, 38)
        new_title.to_corner(UL).shift(0.2 * RIGHT + 0.1 * DOWN)
        new_caption = txt(caption, 28, GREY_B)
        new_caption.to_edge(DOWN, buff=0.45)
        anims = [FadeIn(new_title, shift=0.2 * UP), FadeIn(new_caption, shift=0.2 * DOWN)]
        if self.title is not None:
            anims += [FadeOut(self.title, shift=0.2 * UP), FadeOut(self.caption, shift=0.2 * DOWN)]
        self.play(*anims, run_time=run_time)
        self.title, self.caption = new_title, new_caption

    def set_counter(self, n):
        new = txt(f"Iteration {n}", 30, GREY_B)
        new.to_corner(UR).shift(0.2 * LEFT + 0.1 * DOWN)
        anims = [FadeIn(new)]
        if self.counter is not None:
            anims.append(FadeOut(self.counter))
        self.play(*anims, run_time=0.3)
        self.counter = new

    def set_caption(self, caption, run_time=0.4):
        new_caption = txt(caption, 28, GREY_B)
        new_caption.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(new_caption, shift=0.2 * DOWN), FadeOut(self.caption, shift=0.2 * DOWN), run_time=run_time)
        self.caption = new_caption

    # ======================================================= 1. INTRO ===
    def intro(self):
        card = txt("k-means finds categories.", 46)
        card2 = txt("But it can also find what belongs to none.", 36, GREY_B)
        card2.next_to(card, DOWN, buff=0.45)
        self.play(FadeIn(card, shift=0.3 * UP), run_time=1.0)
        self.wait(1.2)
        self.play(FadeIn(card2, shift=0.3 * UP), run_time=1.0)
        self.wait(2.0)
        self.play(FadeOut(card), FadeOut(card2), run_time=0.8)

        pts = self.points
        self.dots = VGroup(*[Dot(self.P(p), radius=0.085) for p in pts])
        self.dots.set_color(NEUTRAL)
        self.play(LaggedStartMap(FadeIn, self.dots[:N_BLOB_PTS], lag_ratio=0.015, run_time=3.0))
        self.wait(0.8)
        self.play(*[FadeIn(d, scale=3) for d in self.dots[N_BLOB_PTS:]], run_time=1.2)
        self.wait(0.6)

        q = txt("Which of these don't fit?", 54, YELLOW)
        q.to_edge(UP, buff=0.4)
        q.set_backstroke(BLACK, 8)
        self.play(Write(q), run_time=1.8)
        self.wait(2.5)
        guess = txt("Take a guess before we run anything.", 28, GREY_B)
        guess.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(guess, shift=0.2 * DOWN), run_time=0.6)
        self.wait(5.0)
        self.play(FadeOut(guess), run_time=0.4)
        self.wait(0.8)
        self.question = q

    # ================================================ 2. K-MEANS (brisk) ==
    def kmeans_section(self):
        old_q = self.question
        title = txt("Step 1: run k-means (k = 3)", 38)
        title.to_corner(UL).shift(0.2 * RIGHT + 0.1 * DOWN)
        cap = txt("The clustering is just the setup", 28, GREY_B)
        cap.to_edge(DOWN, buff=0.45)
        self.play(FadeOut(old_q, shift=0.3 * UP), FadeIn(title, shift=0.2 * UP), FadeIn(cap, shift=0.2 * DOWN), run_time=0.8)
        self.title, self.caption = title, cap

        self.stars = [make_star(CLUSTER_COLORS[k]) for k in range(K)]
        for k in range(K):
            self.stars[k].move_to(self.P(self.cents[0][k]))
        self.set_caption("Drop 3 centroids at random")
        self.play(*[GrowFromCenter(s) for s in self.stars], run_time=0.6)
        self.play(*[Flash(s, color=CLUSTER_COLORS[k], flash_radius=0.6, run_time=0.7) for k, s in enumerate(self.stars)])
        self.wait(0.8)

        self.set_counter(1)
        self.set_caption("Color each point by its nearest centroid")
        self.link_lines = VGroup()
        for n, idx in enumerate([60, N_BLOB_PTS + 4]):
            ls = VGroup(*[Line(self.dots[idx].get_center(), self.stars[k].get_center(), stroke_width=2.5,
                               color=CLUSTER_COLORS[k]) for k in range(K)])
            ls.set_z_index(3)
            self.play(self.dots[idx].animate.scale(1.8).set_color(WHITE), ShowCreation(ls, lag_ratio=0.3), run_time=0.9)
            self.wait(0.8)
            best = int(np.argmin([np.linalg.norm(self.points[idx] - self.cents[0][k]) for k in range(K)]))
            self.play(*[FadeOut(ls[k]) for k in range(K) if k != best],
                      ls[best].animate.set_stroke(width=5), run_time=0.5)
            self.wait(0.8)
            self.play(FadeOut(ls[best]), self.dots[idx].animate.scale(1 / 1.8).set_color(NEUTRAL), run_time=0.4)
        self.assign_phase(0, first=True)
        n_iter = len(self.assigns)
        for i in range(1, n_iter):
            first = i == 1
            self.set_counter(i + 1)
            self.set_caption("Move each centroid to its cluster's mean" if first else "Update centroids", run_time=0.3)
            self.move_phase(i, slow=first)
            changed = np.where(self.assigns[i] != self.assigns[i - 1])[0]
            if len(changed) == 0:
                self.set_caption("Nothing changed: converged", run_time=0.3)
                self.play(*[Indicate(s, scale_factor=1.5) for s in self.stars], run_time=1.0)
                self.wait(1.2)
                break
            self.set_caption(f"{len(changed)} point{'s' if len(changed) > 1 else ''} switch to a nearer centroid" if first
                             else "Reassign points", run_time=0.3)
            self.assign_phase(i, first=False, changed=changed)
            self.wait(0.4 if first else 0.2)

    def build_links(self, assign, cent_screen):
        """Faint line from every point to its centroid."""
        links = VGroup()
        for j, d in enumerate(self.dots):
            k = assign[j]
            links.add(Line(d.get_center(), cent_screen[k], stroke_width=1.2,
                           color=CLUSTER_COLORS[k]).set_opacity(0.28))
        links.set_z_index(0)
        return links

    def assign_phase(self, i, first, changed=None):
        assign = self.assigns[i]
        cent_screen = [s.get_center() for s in self.stars]
        new_links = self.build_links(assign, cent_screen)
        recolor = [d.animate.set_color(CLUSTER_COLORS[assign[j]]) for j, d in enumerate(self.dots)
                   if first or j in changed]
        if first:
            self.play(LaggedStart(*recolor, lag_ratio=0.01, run_time=1.4),
                      FadeIn(new_links, run_time=1.4))
            self.wait(0.6)
        else:
            self.play(*recolor,
                      *[Flash(self.dots[j], color=WHITE, flash_radius=0.35, line_length=0.12, run_time=0.7) for j in changed],
                      FadeOut(self.link_lines), FadeIn(new_links), run_time=0.8)
            self.remove(self.link_lines)
        if first:
            pass
        self.link_lines = new_links

    def move_phase(self, i, slow):
        new_c = self.cents[i]
        trails = [DashedLine(self.stars[k].get_center(), self.P(new_c[k]), color=CLUSTER_COLORS[k], stroke_width=2)
                  for k in range(K)]
        self.play(*[ShowCreation(t) for t in trails], run_time=0.3 if not slow else 0.6)
        cent_screen = [self.P(new_c[k]) for k in range(K)]
        old_assign = self.assigns[i - 1]
        # links follow their centroids as they move
        moving = []
        for j, ln in enumerate(self.link_lines):
            k = old_assign[j]
            moving.append(ln.animate.put_start_and_end_on(self.dots[j].get_center(), cent_screen[k]))
        self.play(*[self.stars[k].animate.move_to(cent_screen[k]) for k in range(K)],
                  *moving, run_time=1.2 if slow else 0.8)
        self.play(*[FadeOut(t) for t in trails], run_time=0.2)

    # ============================================== 3. THE FIT SCORE ======
    def fit_score_section(self):
        dots, stars = self.dots, self.stars
        self.play(FadeOut(self.counter), run_time=0.3)
        self.counter = None
        self.set_texts("Step 2: the fit score", "Converged. Now look at each point's distance to its centroid", run_time=0.6)
        self.wait(1.8)

        # (a) isolate the question: how far is each point from its own centroid?
        self.set_caption("Distance to nearest centroid = how well a point fits its category")
        sample = [10, N_BLOB_PTS + 4, N_BLOB_PTS]  # a typical point, a gap point, a far stray
        for idx in sample:
            ln = Line(dots[idx].get_center(), stars[self.final_a[idx]].get_center(), stroke_width=5, color=YELLOW)
            ln.set_z_index(3)
            lab = txt(f"{self.dist[idx]:.1f}", 28, YELLOW)
            lab.set_backstroke(BLACK, 6)
            lab.move_to(ln.get_center() + 0.35 * normalize(rotate_vector(ln.get_vector(), PI / 2)))
            self.play(ShowCreation(ln), dots[idx].animate.scale(1.8), run_time=0.7)
            self.play(FadeIn(lab, scale=0.7), run_time=0.4)
            self.wait(2.0)
            self.play(FadeOut(ln), FadeOut(lab), dots[idx].animate.scale(1 / 1.8), run_time=0.5)

        # (b) scale links by distance: short = calm, long = hot
        self.set_caption("Let each line show its length: short = calm, long = hot")
        cent_screen = [s.get_center() for s in stars]
        new_links = VGroup()
        for j, d in enumerate(dots):
            c = dist_color(self.dist[j], self.thr)
            w = 1.0 + 3.2 * min(self.dist[j] / self.thr, 1.3) ** 2
            op = 0.25 + 0.6 * min(self.dist[j] / self.thr, 1.0)
            ln = Line(d.get_center(), cent_screen[self.final_a[j]], stroke_width=w, color=c).set_opacity(op)
            new_links.add(ln)
        self.play(FadeOut(self.link_lines), FadeIn(new_links), run_time=1.5)
        self.link_lines = new_links
        self.wait(3.5)

        # (c) move the plot left and make room for a histogram
        self.set_caption("Collect every point's fit score in a histogram")
        shift, s = 2.9 * LEFT, 0.66
        self.plot_shift = shift
        world = VGroup(dots, *stars, self.link_lines)
        self.play(world.animate.scale(s, about_point=ORIGIN).shift(shift), run_time=1.6)
        self.origin = s * self.origin + shift
        self.sc *= s
        # dot sizes scale with world, which is fine

        self.build_histogram()
        self.wait(2.5)

        # (d) tail callout
        brace_txt = txt("most points:\ntiny distance", 22, "#6FA8DC")
        brace_txt.move_to(self.hx(2.0, 2.1))
        tail_txt = txt("a few stragglers", 22, YELLOW)
        tail_txt.move_to(self.hx(2.55, 1.2))
        arr = Arrow(tail_txt.get_bottom(), self.hx(2.75, 0.2), buff=0.1, color=YELLOW, stroke_width=4)
        self.play(FadeIn(brace_txt, shift=0.2 * UP), run_time=0.6)
        self.wait(2.5)
        self.play(FadeIn(tail_txt, shift=0.2 * UP), ShowCreation(arr), run_time=0.8)
        self.wait(3.5)
        self.play(FadeOut(brace_txt), FadeOut(tail_txt), FadeOut(arr), run_time=0.5)

        # (e) threshold
        mu, sd = self.dist.mean(), self.dist.std()
        self.set_caption(f"Cutoff = mean + {N_SIGMA:g} standard deviations")
        stats = txt(f"mean = {mu:.2f}     std = {sd:.2f}", 26, GREY_B)
        stats.next_to(self.hist_frame, UP, buff=0.25)
        self.play(FadeIn(stats, shift=0.2 * DOWN), run_time=0.6)
        mean_line = DashedLine(self.hx(mu, 0), self.hx(mu, 2.55), color=GREY_B, stroke_width=3)
        mean_lab = txt("mean", 22, GREY_B).next_to(mean_line, UP, buff=0.08)
        self.play(ShowCreation(mean_line), FadeIn(mean_lab), run_time=0.8)
        self.wait(2.0)
        thr_line = Line(self.hx(self.thr, 0), self.hx(self.thr, 2.55), color=FLAG, stroke_width=5)
        thr_lab = txt("cutoff", 24, FLAG).next_to(thr_line, UP, buff=0.08)
        thr_lab.shift(0.0 * UP)
        self.play(ShowCreation(thr_line), FadeIn(thr_lab, shift=0.2 * DOWN), run_time=1.0)
        self.wait(2.5)
        # shade the tail region
        tail_rect = Rectangle(width=self.hx(BIN_MAX, 0)[0] - self.hx(self.thr, 0)[0], height=2.55)
        tail_rect.set_fill(FLAG, 0.12).set_stroke(width=0)
        tail_rect.move_to(0.5 * (self.hx(self.thr, 0) + self.hx(BIN_MAX, 2.55)))
        self.play(FadeIn(tail_rect), run_time=0.6)
        self.hist_extras = VGroup(mean_line, mean_lab, thr_line, thr_lab, stats, tail_rect)

        # (f) rings on the plot
        self.set_caption("The same cutoff is a ring around each centroid")
        rings = VGroup()
        for k in range(K):
            c = Circle(radius=self.thr * self.sc, color=CLUSTER_COLORS[k])
            c.move_to(stars[k].get_center())
            r = DashedVMobject(c, num_dashes=48, positive_space_ratio=0.55)
            r.set_stroke(CLUSTER_COLORS[k], 3, 0.95)
            rings.add(r)
        rings.set_z_index(2)
        self.play(LaggedStartMap(ShowCreation, rings, lag_ratio=0.25, run_time=2.0))
        self.rings = rings
        self.wait(3.5)

        # (g) flag outliers
        self.set_caption("Beyond the ring? That point fits no category")
        flagged = self.flagged
        fl_dots = [dots[i] for i in flagged]
        self.play(*[Indicate(d, scale_factor=2.2, color=YELLOW) for d in fl_dots], run_time=1.2)
        # their histogram bars pulse as well
        pulse_anims = []
        for _ in range(2):
            pulse_anims.append(AnimationGroup(*[d.animate.scale(1.9) for d in fl_dots], run_time=0.35))
            pulse_anims.append(AnimationGroup(*[d.animate.scale(1 / 1.9) for d in fl_dots], run_time=0.35))
        for a in pulse_anims:
            self.play(a)
        # lose cluster colour -> red, drop their links, remove from cluster
        to_remove = VGroup(*[self.link_lines[i] for i in flagged])
        self.play(*[d.animate.set_color(FLAG) for d in fl_dots],
                  *[FadeOut(self.link_lines[i]) for i in flagged],
                  *[Flash(d, color=FLAG, flash_radius=0.55, line_length=0.2, num_lines=10, run_time=1.0) for d in fl_dots],
                  run_time=1.0)
        self.remove(to_remove)
        # histogram: red bars for the flagged scores
        self.recolor_hist_tail()
        labels = VGroup()
        for i in flagged:
            lab = txt("Uncategorized", 20, FLAG)
            lab.set_backstroke(BLACK, 6)
            self.place_label(lab, dots[i].get_center())
            labels.add(lab)
        self.play(LaggedStartMap(FadeIn, labels, lag_ratio=0.2, run_time=1.8))
        self.uncat_labels = labels
        self.wait(1.5)
        n_total = len(self.points)
        summary = txt(f"{len(flagged)} of {n_total} points flagged", 28, FLAG)
        summary.move_to(stats.get_center())
        self.play(FadeOut(stats), FadeIn(summary, shift=0.2 * DOWN), run_time=0.6)
        self.hist_extras.remove(stats)
        self.hist_extras.add(summary)
        self.wait(2.5)
        self.set_caption("Includes the in-between points no cluster claims cleanly")
        gap_ids = [N_BLOB_PTS + 4, N_BLOB_PTS + 5]
        self.play(*[FlashAround(dots[i], color=YELLOW, run_time=1.5) for i in gap_ids])
        self.wait(1.5)
        self.set_caption("Sitting between clusters means far from every centroid")
        self.wait(4.0)

    def place_label(self, lab, pos):
        """Put a label near a point, pushing away from the plot centre / frame edges."""
        offset = 0.42 * UP
        if pos[1] > 2.3:
            offset = 0.42 * DOWN
        lab.move_to(pos + offset)
        # keep label inside frame horizontally
        half = FRAME_WIDTH / 2 - 0.15
        if lab.get_left()[0] < -half:
            lab.shift((-half - lab.get_left()[0]) * RIGHT)
        if lab.get_right()[0] > half:
            lab.shift((half - lab.get_right()[0]) * RIGHT)

    # -------------------------------------------------------- histogram --
    HX_LEFT = 1.95
    HX_W = 4.9
    HY_BOT = -1.9
    HY_H = 2.9  # height of the tallest bar available

    def hx(self, x, h):
        """Histogram-space (distance x, bar height in scene units) -> screen."""
        return np.array([self.HX_LEFT + self.HX_W * x / BIN_MAX, self.HY_BOT + h, 0.0])

    def build_histogram(self):
        edges = np.linspace(0, BIN_MAX, N_BINS + 1)
        counts, _ = np.histogram(self.dist, bins=edges)
        self.counts, self.edges = counts, edges
        self.hy_scale = 2.55 / counts.max()

        frame = Rectangle(width=self.HX_W + 0.3, height=3.75)
        frame.move_to([self.HX_LEFT + self.HX_W / 2, self.HY_BOT + 1.55, 0])
        frame.set_stroke(GREY_D, 2).set_fill(opacity=0)
        self.hist_frame = frame
        axis = Line(self.hx(0, 0), self.hx(BIN_MAX, 0), stroke_width=3, color=GREY_B)
        self.hist_axis_left = axis
        ticks = VGroup()
        for v in [0, 1, 2, 3]:
            t = Line(self.hx(v, 0), self.hx(v, -0.1), stroke_width=2, color=GREY_B)
            n = txt(str(v), 20, GREY_B).next_to(t, DOWN, buff=0.06)
            ticks.add(t, n)
        xlab = txt("distance to own centroid  (fit score)", 22, GREY_B).next_to(ticks, DOWN, buff=0.15)
        ylab = txt("# points", 22, GREY_B).rotate(PI / 2).next_to(axis, LEFT, buff=0.15).shift(1.4 * UP)
        ylab.set_x(self.HX_LEFT - 0.55)
        self.play(FadeIn(frame), ShowCreation(axis), FadeIn(ticks), FadeIn(xlab), FadeIn(ylab), run_time=1.2)
        self.hist_static = VGroup(frame, axis, ticks, xlab, ylab)

        # bars grow while dots "drop" in: build in order of distance
        bars = VGroup()
        for b in range(N_BINS):
            h = counts[b] * self.hy_scale
            if counts[b] > 0:
                h = max(h, 0.14)  # keep the lone tail bars visible
            w = self.HX_W / N_BINS
            bar = Rectangle(width=w * 0.92, height=max(h, 0.001))
            bar.set_fill(dist_color(0.5 * (edges[b] + edges[b + 1]), self.thr), 0.9).set_stroke(width=0)
            bar.move_to(self.hx(0.5 * (edges[b] + edges[b + 1]), 0) + 0.5 * max(h, 0.001) * UP)
            bars.add(bar)
        self.bars = bars
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.12, run_time=3.2))

    def recolor_hist_tail(self):
        anims = []
        for b in range(N_BINS):
            lo = self.edges[b]
            if lo >= self.thr:
                anims.append(self.bars[b].animate.set_fill(FLAG, 0.95))
        # straddling bin (contains thr) -> split by recolouring just bins fully beyond the cutoff
        self.play(*anims, run_time=0.8)

    # ===================================== 4. REAL-WORLD RELABEL =========
    def real_world_section(self):
        dots, stars = self.dots, self.stars
        # clear the histogram side, bring the plot back to centre, drop rings
        clear = VGroup(self.hist_static, self.bars, self.hist_extras)
        self.set_texts("Same plot, real data", "Each dot is a product listing", run_time=0.6)
        self.play(FadeOut(clear), FadeOut(self.rings), FadeOut(self.uncat_labels), run_time=0.9)
        # undo the earlier scale(0.66) + shift, ending at scale 0.88 centred slightly high
        world = VGroup(dots, *stars, self.link_lines)
        self.play(world.animate.shift(-self.plot_shift).scale(0.88 / 0.66, about_point=ORIGIN).shift(0.1 * UP),
                  run_time=1.6)
        self.origin = np.array([0.0, 0.1, 0.0])
        self.sc = 0.88

        # axes (drawn by hand)
        x_axis = Arrow(self.P([-6.7, -3.0]), self.P([6.9, -3.0]), buff=0, stroke_width=3, color=GREY_B)
        y_axis = Arrow(self.P([-6.7, -3.0]), self.P([-6.7, 3.0]), buff=0, stroke_width=3, color=GREY_B)
        x_lab = txt("order size  (units per order)", 24, GREY_B).next_to(x_axis, DOWN, buff=0.1)
        y_lab = txt("price", 24, GREY_B).rotate(PI / 2).next_to(y_axis, LEFT, buff=0.12)
        self.play(ShowCreation(x_axis), ShowCreation(y_axis), run_time=1.0)
        self.play(FadeIn(x_lab), FadeIn(y_lab), run_time=0.8)
        self.wait(3.0)
        self.set_caption("Axes become two features: price and order size")
        self.wait(3.0)

        # category names
        names = ["Budget\nbulk goods", "Mid-range\nhousehold", "Premium\nsingles"]
        # which final cluster sits where
        order = np.argsort([c[0] for c in self.final_c])  # left to right
        # name by left-to-right position, but keyed to centroid index
        name_for = {}
        for rank, k in enumerate(order):
            name_for[k] = names[rank]
        cat_labels = VGroup()
        for k in range(K):
            lab = txt(name_for[k].replace("\n", " "), 24, CLUSTER_COLORS[k])
            lab.set_backstroke(BLACK, 6)
            lab.next_to(stars[k], UP, buff=1.05 if k != order[1] else 0.9)
            cat_labels.add(lab)
        self.set_caption("The three clusters become named categories")
        self.play(LaggedStartMap(FadeIn, cat_labels, shift=0.2 * UP, lag_ratio=0.3, run_time=2.0),
                  *[Indicate(s, scale_factor=1.4) for s in stars])
        self.wait(3.5)

        # fade the fit-score link lines so the picture stays readable
        self.set_caption("Dots that fit a category stay quietly in it")
        self.play(FadeOut(self.link_lines), run_time=0.8)
        self.wait(3.0)

        # flagged points get review labels
        self.set_caption("Poor fit to every category: send them to a person")
        reviews = [
            ("Possible mislabel", 0, 1.35 * RIGHT),
            ("Needs human review", 1, 1.55 * LEFT),
            ("Possible duplicate listing", 2, 0.45 * UP),
            ("Data entry error?", 3, 0.45 * UP + 0.5 * LEFT),
            ("Between\ncategories", 4, 0.62 * DOWN),
            ("Between\ncategories", 5, 0.62 * DOWN),
        ]
        review_labels = VGroup()
        for text, j, offset in reviews:
            lab = txt(text, 22, FLAG)
            lab.set_backstroke(BLACK, 6)
            lab.move_to(dots[N_BLOB_PTS + j].get_center() + offset)
            review_labels.add(lab)
        reviews = [(t, j) for t, j, _ in reviews]
        for lab, (text, j) in zip(review_labels, reviews):
            d = dots[N_BLOB_PTS + j]
            self.play(Flash(d, color=FLAG, flash_radius=0.5, line_length=0.18, run_time=0.7),
                      FadeIn(lab, shift=0.15 * UP), d.animate.scale(1.5), run_time=0.7)
            self.wait(1.8)
        self.wait(3.0)
        self.set_caption("The model handles the routine; people review the few red dots")
        self.wait(4.0)

        # takeaway
        dim = VGroup(dots, *stars, cat_labels, review_labels, x_axis, y_axis, x_lab, y_lab)
        take = txt("Poor fit to every category = worth a closer look", 42, WHITE)
        take.set_backstroke(BLACK, 10)
        take_grp = VGroup(take)
        take_grp.move_to(ORIGIN)
        self.play(dim.animate.set_opacity(0.1), FadeOut(self.caption), FadeOut(self.title), run_time=0.8)
        self.play(Write(take), run_time=2.4)
        self.play(Flash(take, color=FLAG, flash_radius=1.0, line_length=0.3, run_time=1.2))
        self.wait(6.0)
        self.play(FadeOut(take_grp), FadeOut(dim), run_time=1.2)
        self.wait(0.5)
