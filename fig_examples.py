"""
fig_examples.py - every recipe of docs/paper_figure_guide.md (section 6) as a runnable script, on
synthetic data. Run it to see what the figures look like, and copy from it for a new figure.

    python fig_examples.py                        # two-column layout    -> images/paper/
    python fig_examples.py --layout single        # single-column layout -> images/paper_single/
    python fig_examples.py --only fig_example_tiles,fig_example_pair
    python fig_examples.py --show                 # interactive windows instead of files

The map recipe needs seaborn (pip install seaborn); the others need only numpy and matplotlib.
The functions are the recipes of the guide, written out here so that they run as they are.
"""
import numpy as np
from matplotlib.lines import Line2D
from paper_style import *          # style, palette, labels, helpers, ARGS
from zoom_plot import zoom_plot    # inset + rectangle + connectors (recipe 6.4)


def fig_example_snapshot(name):
    """Two stacked panels on one time axis: signal on top, residual below."""
    tau = np.linspace(-1.26, 1.05, 160)                      # time from now [s]
    y_base = 70 + 25 * np.sin(3.0 * tau)                      # baseline model [a.u.]
    r = 6 * np.sin(7.0 * tau + 0.5)                          # residual [a.u.]
    y = y_base + r                                            # measured signal [a.u.]
    past, fut = tau <= 0, tau >= 0
    fig, (axy, axr) = stacked(height("snapshot"), [2.0, 1.15])
    for ax in (axy, axr):
        ax.axvspan(0, tau[-1], color=NEUTRAL, alpha=0.28, lw=0, zorder=0)    # forecast region
        ax.axvline(0, color=C_AX, lw=0.8, alpha=0.6, zorder=1)               # now
    axy.plot(tau[past], y[past], color=C_MEAS, lw=2.0, marker="o", ms=3.2, zorder=4)
    axy.plot(tau[fut], y[fut], color=C_MEAS, lw=2.0, zorder=4)
    axy.plot(tau, y_base, color=C_BASE, lw=1.4, ls=LS_BASE, zorder=3)
    axy.plot(tau[fut], y[fut] + 1.5, color=C_PROPOSED, lw=2.0, zorder=6)
    axr.axhline(0, color=MUTED, lw=0.9, zorder=1)
    axr.plot(tau[past], r[past], color=C_MEAS, lw=0, marker="o", ms=3.4, zorder=4)
    axr.plot(tau[fut], r[fut], color=C_MEAS, lw=2.0, zorder=4)
    axr.plot(tau[fut], r[fut] + 1.5, color=C_PROPOSED, lw=2.0, zorder=6)
    axy.set_xlim(tau[0], tau[-1])
    axy.set_ylabel(r"$y$ [a.u.]")
    axr.set_ylabel(r"$r$ [a.u.]")
    axr.set_xlabel(r"$\tau = t - t_k$ [s]")
    handles = [Line2D([], [], color=C_MEAS, lw=2.0, marker="o", ms=3, label=r"measured $y$"),
               Line2D([], [], color=C_BASE, lw=1.4, ls=LS_BASE, label=LAB_BASE),
               Line2D([], [], color=C_PROPOSED, lw=2.0, label=LAB_PROPOSED)]
    legend_at(axy, handles=handles, ncol=3, title=TAG_TEST)
    # in-panel tags on a patch of the local background, so no curve runs through them
    for x, s, ha, fc in ((0.012, "past", "left", "white"), (0.988, "forecast", "right", "#eeeeeb")):
        axy.text(x, 0.035, s, transform=axy.transAxes, ha=ha, fontsize=LEGEND_FS, color=INK_2,
                 zorder=10, bbox=dict(boxstyle="square,pad=0.15", fc=fc, ec="none", alpha=0.9))
    finish(fig, [axy, axr])
    save(fig, name)


def fig_example_bands(name):
    """A metric versus a parameter, with the distribution of that metric over the pieces of the data
    set: <name>_ramp (a transparency ramp) and <name>_patch (a patch: 25-75 %),
    the metric of the whole data set on top. The shaded distribution and the line must be the same
    quantity, otherwise the line does not run inside its shading."""
    h = np.arange(0, 1051, 50)                               # forecast horizon [ms]
    rng = np.random.default_rng(0)
    rows = [(C_BASE, LS_BASE, "s", LAB_BASE, 6.6 + 0.2 * (1 - np.exp(-h / 150))),
            (C_COMPARE, "-", "o", LAB_COMPARE, 2.8 + 1.8 * (1 - np.exp(-h / 150))),
            (C_PROPOSED, "-", "D", LAB_PROPOSED, 0.4 + 4.0 * (1 - np.exp(-h / 90)))]
    quantiles = []                                           # per method: quantiles over the pieces
    for c, ls, mk, lab, rmse in rows:
        # per-piece values: here 250 "cycles", each with its own level and noise
        per_piece = rmse * (1.0 + 0.35 * rng.standard_normal((250, 1))
                            + 0.10 * rng.standard_normal((250, h.size)))
        quantiles.append(np.percentile(np.maximum(per_piece, 0.0), RAMP_Q, axis=0))
    for suffix, bands in (("ramp", ramp_bands), ("patch", patch_bands)):
        fig, (ax,) = stacked(height("curve"), [1.0])
        for (c, ls, mk, lab, rmse), Q in zip(rows, quantiles):
            bands(ax, h, Q, color=c)                         # the distribution, as patches
        for c, ls, mk, lab, rmse in rows:
            ax.plot(h, rmse, color=c, ls=ls, marker=mk, ms=4.0, lw=1.8, mec="white", mew=0.6,
                    zorder=4, label=lab)
        ax.set_xlim(h[0], h[-1])                             # cut on the data: no white margin
        ax.set_ylim(0, 8)                                    # the tails above 8 are cut by the frame
        ax.set_xlabel(r"forecast horizon $h$ [ms]")
        ax.set_ylabel(r"RMSE [a.u.]")
        legend_at(ax, ncol=3, title=TAG_TEST)
        finish(fig, [ax])
        save(fig, f"{name}_{suffix}")


def fig_example_split(name):
    """Two windows of the same signal as two columns of closed tiles (same seconds per inch)."""
    t = np.arange(0, 50, 0.056)                              # time within the cycle [s]
    y_base = 90 - 45 * np.abs(np.sin(0.8 * t)) ** 6
    y = y_base + 8 * np.sin(5 * t) * np.exp(-((t % 8) - 4) ** 2)
    windows = [(4.5, 8.5, "first window"), (44.5, 48.5, "second window")]
    ratios = [1.4, 0.7]                                      # signal, residual
    fig = plt.figure(figsize=(FIG_W, height("split")))
    gs = fig.add_gridspec(len(ratios), len(windows), height_ratios=ratios, hspace=0.07,
                          wspace=0.1, width_ratios=[b - a for a, b, _ in windows],
                          bottom=0.65 / height("split"))   # 0.65 in: tick labels + the shared x label
    axes = [[None] * len(windows) for _ in ratios]
    for i in range(len(ratios)):
        for j in range(len(windows)):
            axes[i][j] = fig.add_subplot(gs[i, j], sharex=axes[0][j] if i else None,
                                         sharey=axes[i][0] if j else None)
    for j, (a, b, title) in enumerate(windows):
        axy, axr = axes[0][j], axes[1][j]
        m = (t >= a - 0.3) & (t <= b + 0.3)
        axy.plot(t[m], y_base[m], color=C_BASE, lw=1.8, ls=LS_BASE, label=LAB_BASE)
        axy.plot(t[m], y[m], color=C_MEAS, lw=2.0, marker="o", ms=3, label=r"measured $y$")
        axr.axhline(0, color=MUTED, lw=0.9)
        axr.plot(t[m], y[m] - y_base[m], color=C_MEAS, lw=1.6, marker="o", ms=3)
        axy.set_xlim(a, b)
        axy.set_title(title, fontsize=LEGEND_FS, color=C_AX, pad=4)
        axy.tick_params(labelbottom=False)
        if j:                                                # shared y: labels on the left only
            axy.tick_params(labelleft=False)
            axr.tick_params(labelleft=False)
    axes[0][0].set_ylabel(r"$y$ [a.u.]")
    axes[1][0].set_ylabel(r"$r$ [a.u.]")
    fig.supxlabel(r"time within cycle [s]", fontsize=LABEL_FS, y=0.0)
    legend_above_all(fig, axes[0], ncol=2, title=TAG_TRAIN)  # one legend above both tiles
    finish(fig, [ax for row in axes for ax in row])
    save(fig, name)


def fig_example_convergence(name):
    """Loss curves of an ordered series, one panel per method, with an inset on the converged part."""
    ns = [1, 2, 3, 4, 5]
    cols = viridis_colours(ns)
    steps = np.arange(400)
    final = {LAB_PROPOSED: {n: 3.55 - 0.01 * n for n in ns}, LAB_COMPARE: {n: 3.8 + 0.21 * n for n in ns}}
    fig = plt.figure(figsize=(FIG_W, height("tiles")))
    gs = fig.add_gridspec(1, 2, wspace=0.3)
    axc = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]
    for ax, lab in zip(axc, (LAB_PROPOSED, LAB_COMPARE)):
        for n in ns:
            loss = final[lab][n] + (7.5 - final[lab][n]) * np.exp(-steps / 40)
            ax.plot(steps, loss, color=cols[n], lw=1.9, label=rf"$N_{{\mathrm{{prev}}}} = {n}$")
        ax.set_title(lab, fontsize=LEGEND_FS + 1, color=C_AX, pad=5)
        ax.set_xlabel(r"gradient step")
        ax.set_xlim(0, steps[-1])
    # the curves coincide at full scale: zoom on the converged part. zoom_plot copies the curves
    # into the inset and marks the zoomed region on the parent axes (rectangle + two connectors)
    fin = list(final[LAB_PROPOSED].values())
    zm = zoom_plot(axc[0], xlim=(150, steps[-1]), ylim=(min(fin) - 0.02, max(fin) + 0.04),
                   position=(0.36, 0.34, 0.6, 0.56), color=C_AX, lw=0.9, tick_fs=TICK_FS - 3)
    for ln in zm.child.lines:
        ln.set_linewidth(1.6)
    axc[0].set_ylabel(r"training loss [a.u.]")
    legend_above_all(fig, axc, ncol=5, columnspacing=0.9, handlelength=1.3,
                     title="training set, same initial hyperparameters")
    finish(fig, axc)
    save(fig, name)


def fig_example_map(name):
    """A path in the plane, coloured by a value, with a vertical colour bar on the right."""
    import seaborn as sns
    from matplotlib.collections import LineCollection
    from matplotlib.colors import Normalize
    s = np.linspace(0, 2 * np.pi, 900)
    X, Y = 700 * np.cos(s), 220 * np.sin(s)                  # path of one cycle [mm]
    err = 3 + 14 * np.abs(np.sin(3 * s)) ** 6                # value along the path [a.u.]
    pts = np.column_stack([X, Y])
    segs = np.stack([pts[:-1], pts[1:]], axis=1)
    cmap = sns.color_palette("rocket_r", as_cmap=True)
    norm = Normalize(0, float(err.max()))                    # the colour bar covers the data range
    left, right, bottom, top = 1.0, 0.1, 0.8, 0.4            # margins [in]: y label, colour-bar label, x label, title
    gap, cb_w, cb_labels = 0.15, 0.22, 0.85                  # map - colour bar gap, colour bar width, its labels [in]
    map_w = FIG_W - left - gap - cb_w - cb_labels - right
    map_h = map_w * (np.ptp(Y) + 40) / (np.ptp(X) + 40)      # height from the data aspect
    W, H = FIG_W, bottom + map_h + top
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([left / W, bottom / H, map_w / W, map_h / H])
    cax = fig.add_axes([(left + map_w + gap) / W, bottom / H, cb_w / W, map_h / H])
    lc = LineCollection(segs, cmap=cmap, norm=norm, linewidth=3.4, capstyle="round")
    lc.set_array(0.5 * (err[:-1] + err[1:]))
    ax.add_collection(lc)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(X.min() - 20, X.max() + 20)
    ax.set_ylim(Y.min() - 20, Y.max() + 20)
    ax.set_xlabel(r"$x_1$ [mm]")
    ax.set_ylabel(r"$x_2$ [mm]")
    ax.set_title(TAG_TEST, loc="left", fontsize=LEGEND_FS + 1, color=C_AX, pad=5)
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)
    cb.set_label(r"absolute error [a.u.]", fontsize=LABEL_FS)
    cb.ax.tick_params(labelsize=TICK_FS, direction="in", colors=C_AX)
    finish(fig, [ax])
    save(fig, name)


def fig_example_tiles(name):
    """One tile per model, shared y axis, the distribution of the metric over the pieces of the
    data set as a transparency ramp, the metric of the whole data set on top."""
    h = np.arange(0, 1051, 50)                               # forecast horizon [ms]
    rng = np.random.default_rng(0)
    rows = [(C_BASE, "s", LAB_BASE, 6.6 + 0.2 * (1 - np.exp(-h / 150))),
            (C_COMPARE, "o", LAB_COMPARE, 2.8 + 1.8 * (1 - np.exp(-h / 150))),
            (C_PROPOSED, "D", LAB_PROPOSED, 0.4 + 4.0 * (1 - np.exp(-h / 90)))]
    fig = plt.figure(figsize=(FIG_W, height("tiles")))
    gs = fig.add_gridspec(1, len(rows), wspace=0.08)
    axes = []
    for j, (c, mk, lab, rmse) in enumerate(rows):
        ax = fig.add_subplot(gs[j], sharey=axes[0] if j else None)
        per_piece = rmse * (1.0 + 0.35 * rng.standard_normal((250, 1))
                            + 0.10 * rng.standard_normal((250, h.size)))
        Q = np.percentile(np.maximum(per_piece, 0.0), RAMP_Q, axis=0)
        ramp_bands(ax, h, Q, color=c)
        ax.plot(h, rmse, color=c, marker=mk, ms=4.0, lw=1.8, mec="white", mew=0.6, zorder=4)
        ax.set_xlim(h[0], h[-1])
        ax.set_xticks([0, 400, 800])                         # no tick at the right limit
        ax.set_xlabel(r"horizon $h$ [ms]")
        ax.set_title(lab, fontsize=LEGEND_FS + 1, color=C_AX, pad=5)
        if j:
            ax.tick_params(labelleft=False)                  # shared y: labels on the left only
        axes.append(ax)
    axes[0].set_ylim(0, 8)                                   # the tails above 8 are cut by the frame
    axes[0].set_yticks([0, 4, 8])                            # short labels: "0.0" would touch the x "0"
    axes[0].set_ylabel(r"RMSE [a.u.]")
    axes[0].text(0.05, 0.05, TAG_TEST, transform=axes[0].transAxes, fontsize=LEGEND_FS, color=INK_2,
                 zorder=10, bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none", alpha=0.9))
    finish(fig, axes)
    save(fig, name)


def fig_example_pair(name):
    """Two figures that stand side by side (written as <name>_a and <name>_b), each HALF wide."""
    w, hh = HALF * FIG_W, height("pair", HALF)
    h = np.arange(0, 1051, 50)                               # forecast horizon [ms]
    ns = np.arange(1, 6)                                     # previous cycles
    # (a) a metric versus a parameter, two models
    fig, (ax,) = stacked(hh, [1.0], width=w)
    ax.plot(h, 2.8 + 1.8 * (1 - np.exp(-h / 150)), color=C_COMPARE, marker="o", ms=4.5, lw=1.8,
            mec="white", mew=0.6, label=LAB_COMPARE)
    ax.plot(h, 0.4 + 4.0 * (1 - np.exp(-h / 90)), color=C_PROPOSED, marker="D", ms=4.5, lw=1.8,
            mec="white", mew=0.6, label=LAB_PROPOSED)
    ax.set_xlim(h[0], h[-1])
    ax.set_ylim(0, 6)
    ax.set_xlabel(r"forecast horizon $h$ [ms]")
    ax.set_ylabel(r"RMSE [a.u.]")
    legend_at(ax, ncol=2, title=TAG_TEST)
    finish(fig, [ax])
    save(fig, f"{name}_a")
    # (b) the same frame: grouped bars per number of previous cycles
    fig, (ax,) = stacked(hh, [1.0], width=w)
    x, bw = np.arange(len(ns)), 0.38
    ax.bar(x - bw / 2, 4.0 + 0.21 * ns, bw, color=C_COMPARE, label=LAB_COMPARE, zorder=3)
    ax.bar(x + bw / 2, 3.55 - 0.01 * ns, bw, color=C_PROPOSED, label=LAB_PROPOSED, zorder=3)
    ax.set_xticks(x, [str(n) for n in ns])
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_ylim(0, 6)
    ax.set_xlabel(r"previous cycles $N_{\mathrm{prev}}$")
    ax.set_ylabel(r"loss [a.u.]")
    legend_at(ax, ncol=2, title=TAG_TEST)
    finish(fig, [ax])
    save(fig, f"{name}_b")


def fig_example_legends(name):
    """The legend styles of the kit: <name>_inside, <name>_above, <name>_above_boxed (one panel each) and
    <name>_row, <name>_row_boxed (a row of tiles that share their colours, one legend above all)."""
    h = np.arange(0, 1051, 50)                               # forecast horizon [ms]
    series = [(C_BASE, LS_BASE, "s", "baseline", 6.6 + 0.2 * (1 - np.exp(-h / 150))),
              (C_COMPARE, "-", "o", "comparison", 2.8 + 1.8 * (1 - np.exp(-h / 150))),
              (C_PROPOSED, "-", "D", "proposed", 0.4 + 4.0 * (1 - np.exp(-h / 90)))]
    s, kind = (HALF, "pair") if LAYOUT == "single" else (1.0, "curve")   # one panel: rule 15

    def draw(ax, k=1.0):
        for c, ls, mk, lab, y in series:
            ax.plot(h, k * y, color=c, ls=ls, marker=mk, ms=4.0, lw=1.8, mec="white", mew=0.6, label=lab)
        ax.set_xlim(h[0], h[-1])
        ax.set_ylim(0, 8)
        ax.set_xlabel(r"horizon $h$ [ms]")

    for suffix, where, boxed in (("inside", "inside", None), ("above", "above", None),
                                 ("above_boxed", "above", True)):
        fig, (ax,) = stacked(height(kind, s), [1.0], width=s * FIG_W)
        draw(ax)
        ax.set_ylabel(r"RMSE [a.u.]")
        legend_at(ax, where, boxed)
        finish(fig, [ax])
        save(fig, f"{name}_{suffix}")

    for suffix, boxed in (("row", False), ("row_boxed", True)):
        fig = plt.figure(figsize=(FIG_W, height("tiles")))
        gs = fig.add_gridspec(1, 3, wspace=0.08)
        axes = []
        for j, (title, k) in enumerate((("training set", 0.85), ("validation set", 1.0), (TAG_TEST, 1.12))):
            ax = fig.add_subplot(gs[j], sharey=axes[0] if j else None)
            draw(ax, k)
            ax.set_xticks([0, 400, 800])                     # no tick at the right limit
            ax.set_title(title, fontsize=LEGEND_FS + 1, color=C_AX, pad=5)
            if j:
                ax.tick_params(labelleft=False)              # shared y: labels on the left only
            axes.append(ax)
        axes[0].set_ylabel(r"RMSE [a.u.]")
        legend_above_all(fig, axes, boxed=boxed)             # one legend, above everything
        finish(fig, axes)
        save(fig, f"{name}_{suffix}")


if want("fig_example_snapshot"):
    fig_example_snapshot("fig_example_snapshot")
if want("fig_example_bands"):
    fig_example_bands("fig_example_bands")
if want("fig_example_split"):
    fig_example_split("fig_example_split")
if want("fig_example_convergence"):
    fig_example_convergence("fig_example_convergence")
if want("fig_example_map"):
    fig_example_map("fig_example_map")
if want("fig_example_tiles"):
    fig_example_tiles("fig_example_tiles")
if want("fig_example_pair"):
    fig_example_pair("fig_example_pair")
if want("fig_example_legends"):
    fig_example_legends("fig_example_legends")
show_if_requested()
