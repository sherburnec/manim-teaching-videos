"""Pure-NumPy data + k-means for the fit-score video (no manimlib import)."""
import numpy as np

K = 3
N_SIGMA = 2.5
BLOB_CENTERS = np.array([[-4.3, -0.8], [0.1, 1.1], [4.2, -0.9]])
BLOB_SIGMA = np.array([0.55, 0.5])
BLOB_N = 50
BLOB_TRUNC = 2.0  # blob points are rejected beyond this many sigmas
STRAYS = np.array([
    [-6.0, 2.3],    # far
    [6.1, 2.2],     # far
    [0.3, -2.7],    # far
    [5.9, -2.6],    # far-ish
    [-2.1, 0.05],   # gap A-B
    [2.15, 0.05],   # gap B-C
])
N_STRAY = len(STRAYS)


def make_points(seed):
    rng = np.random.RandomState(seed)
    blobs = []
    for c in BLOB_CENTERS:
        pts = []
        while len(pts) < BLOB_N:
            z = rng.randn(2)
            if np.linalg.norm(z) <= BLOB_TRUNC:
                pts.append(c + z * BLOB_SIGMA)
        blobs.append(np.array(pts))
    return np.vstack(blobs + [STRAYS])


def run_kmeans(points, cent_seed):
    """cents[i] are the centroids used to compute assigns[i]."""
    rng = np.random.RandomState(cent_seed)
    cent = np.c_[rng.uniform(-5.5, 5.5, K), rng.uniform(-2.2, 2.2, K)]
    cents, assigns, prev = [], [], None
    while True:
        d = np.linalg.norm(points[:, None] - cent[None], axis=2)
        a = d.argmin(axis=1)
        cents.append(cent.copy())
        assigns.append(a)
        if prev is not None and (a == prev).all():
            break
        prev = a
        cent = np.array([points[a == k].mean(axis=0) if (a == k).any() else cent[k] for k in range(K)])
    return cents, assigns


def fit_scores(points, cent, assign):
    return np.linalg.norm(points - cent[assign], axis=1)


def threshold(dist):
    return dist.mean() + N_SIGMA * dist.std()


if __name__ == "__main__":
    n_pts = BLOB_N * K
    for ds in range(40):
        pts = make_points(ds)
        for cs in range(60):
            cents, assigns = run_kmeans(pts, cs)
            a, c = assigns[-1], cents[-1]
            # clusters must be the three blobs
            if any(len(set(a[i * BLOB_N:(i + 1) * BLOB_N])) != 1 for i in range(K)):
                continue
            if len(set(a[::BLOB_N][:3])) != 3:
                continue
            d = fit_scores(pts, c, a)
            t = threshold(d)
            flagged = set(np.where(d > t)[0])
            want = set(range(n_pts, n_pts + N_STRAY))
            n_it = len(assigns)
            if flagged == want and 5 <= n_it <= 7:
                margin_lo = d[:n_pts].max()
                margin_hi = d[n_pts:].min()
                print(f"data={ds} cent={cs} iters={n_it} thr={t:.2f} blobmax={margin_lo:.2f} straymin={margin_hi:.2f}")
