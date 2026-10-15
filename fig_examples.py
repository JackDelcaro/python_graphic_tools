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
from matplotlib.patches import Rectangle
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
    legend_top(axy, handles, ncol=3, title=TAG_TEST)
    # in-panel tags on a patch of the local background, so no curve runs through them
    for x, s, ha, fc in ((0.012, "past", "left", "white"), (0.988, "forecast", "right", "#eeeeeb")):
        axy.text(x, 0.035, s, transform=axy.transAxes, ha=ha, fontsize=LEGEND_FS, color=INK_2,
                 zorder=10, bbox=dict(boxstyle="square,pad=0.15", fc=fc, ec="none", alpha=0.9))
    finish(fig, [axy, axr])
    save(fig, name)


def fig_example_bands(name):
    """A metric versus a parameter, with the distribution of that metric over the pieces of the
    data set as a transparency ramp: one connected surface per model (nested filled bands,
    opaque at the median piece, fading towards the extreme ones), the metric of the whole data
    set on top. The shaded distribution and the line must be the same quantity, otherwise the
    line does not run inside its shading."""
    h = np.arange(0, 1051, 50)                               # forecast horizon [ms]
    rng = np.random.default_rng(0)
    rows = [(C_BASE, LS_BASE, "s", LAB_BASE, 6.6 + 0.2 * (1 - np.exp(-h / 150))),
            (C_COMPARE, "-", "o", LAB_COMPARE, 2.8 + 1.8 * (1 - np.exp(-h / 150))),
            (C_PROPOSED, "-", "D", LAB_PROPOSED, 0.4 + 4.0 * (1 - np.exp(-h / 90)))]
    fig, (ax,) = stacked(height("curve"), [1.0])
    y_max = 0.0
    for c, ls, mk, lab, rmse in rows:
        # per-piece values: here 250 "cycles", each with its own level and noise
        per_piece = rmse * (1.0 + 0.35 * rng.standard_normal((250, 1))
                            + 0.10 * rng.standard_normal((250, h.size)))
        Q = np.percentile(np.maximum(per_piece, 0.0), RAMP_Q, axis=0)
        ramp_bands(ax, h, Q, color=c)                        # the distribution, as patches
        y_max = max(y_max, Q[int(np.argmin(np.abs(RAMP_Q - 97.0)))].max())
    for c, ls, mk, lab, rmse in rows:
        ax.plot(h, rmse, color=c, ls=ls, marker=mk, ms=4.0, lw=1.8, mec="white", mew=0.6,
                zorder=4, label=lab)
    ax.set_xlim(h[0], h[-1])                                 # cut on the data: no white margin
    ax.set_ylim(0, 1.02 * y_max)
    ax.set_xlabel(r"forecast horizon $h$ [ms]")
    ax.set_ylabel(r"RMSE [a.u.]")
    legend_top(ax, ncol=3, title=TAG_TEST)
    finish(fig, [ax])
    save(fig, name)


def fig_example_split(name):
    """Two windows of the same signal as two columns of closed tiles (same seconds per inch)."""
    t = np.arange(0, 50, 0.056)                              # time within the cycle [s]
    y_base = 90 - 45 * np.abs(np.sin(0.8 * t)) ** 6
    y = y_base + 8 * np.sin(5 * t) * np.exp(-((t % 8) - 4) ** 2)
    windows = [(4.5, 8.5, "first window"), (44.5, 48.5, "second window")]
    ratios = [1.4, 0.7]                                      # signal, residual
    fig = plt.figure(figsize=(FIG_W, height("split")))
    gs = fig.add_gridspec(len(ratios), len(windows), height_ratios=ratios, hspace=0.07,
                          wspace=0.1, width_ratios=[b - a for a, b, _ in windows])
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
    h, l = axes[0][0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", bbox_to_anchor=(0.5, 0.9), ncol=2, frameon=False,
               fontsize=LEGEND_FS, title=TAG_TRAIN, title_fontsize=LEGEND_FS + 1)
    finish(fig, [ax for row in axes for ax in row])
    save(fig, name)


def fig_example_convergence(name):
    """Top: loss curves of an ordered series, with an inset on the converged part.
    Bottom: grouped bars of one number per order and model."""
    ns = [1, 2, 3, 4, 5]
    cols = viridis_colours(ns)
    steps = np.arange(400)
    final = {LAB_PROPOSED: {n: 3.55 - 0.01 * n for n in ns}, LAB_COMPARE: {n: 3.8 + 0.21 * n for n in ns}}
    fig = plt.figure(figsize=(FIG_W, height("grid")))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 0.95], hspace=0.62, wspace=0.3)
    axc = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]
    axb = [fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])]
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
    up = 0.34 / fig.get_figheight()               # 0.34 in above a panel: clear of its title
    h, l = axc[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", bbox_to_anchor=(0.5, axc[0].get_position().y1 + up),
               ncol=5, frameon=False, fontsize=LEGEND_FS, columnspacing=0.9, handlelength=1.3,
               title="training set, same initial hyperparameters", title_fontsize=LEGEND_FS + 1)
    x, w = np.arange(len(ns)), 0.38
    for ax, tag in zip(axb, (TAG_TRAIN, TAG_TEST)):
        comp = np.array([final[LAB_COMPARE][n] for n in ns])
        prop = np.array([final[LAB_PROPOSED][n] for n in ns])
        ax.bar(x - w / 2, comp, w, color=C_COMPARE, label=LAB_COMPARE, zorder=3)
        ax.bar(x + w / 2, prop, w, color=C_PROPOSED, label=LAB_PROPOSED, zorder=3)
        ax.set_xticks(x, [str(n) for n in ns])
        ax.tick_params(axis="x", which="minor", bottom=False, top=False)
        ax.set_xlabel(r"previous cycles $N_{\mathrm{prev}}$")
        ax.set_ylabel(r"loss [a.u.]")
        ax.set_ylim(0, 1.18 * max(comp.max(), prop.max()))  # bars start at zero
        ax.set_title(tag, fontsize=LEGEND_FS + 1, color=C_AX, pad=5)
    h, l = axb[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", bbox_to_anchor=(0.5, axb[0].get_position().y1 + up),
               ncol=2, frameon=False, fontsize=LEGEND_FS)
    finish(fig, axc + axb)
    save(fig, name)


def fig_example_map(name, boxes=((1.0, 2.2, "fig:window", "north"),)):
    """A path in the plane, coloured by a value, with a colour bar. `boxes` are
    windows of the path (here in the parameter s) marked by a rectangle; their labels are
    written by LaTeX from <name>_labels.tex, so they follow the numbering of the document."""
    import seaborn as sns
    from matplotlib.collections import LineCollection
    from matplotlib.colors import Normalize
    s = np.linspace(0, 2 * np.pi, 900)
    X, Y = 700 * np.cos(s), 220 * np.sin(s)                  # path of one cycle [mm]
    err = 3 + 14 * np.abs(np.sin(3 * s)) ** 6                # value along the path [a.u.]
    pts = np.column_stack([X, Y])
    segs = np.stack([pts[:-1], pts[1:]], axis=1)
    cmap = sns.color_palette("rocket_r", as_cmap=True)
    norm = Normalize(0, float(np.percentile(err, 98)))       # cap at p98: colour bar "extend"
    panel_h = (FIG_W - 1.0) * (np.ptp(Y) + 40) / (np.ptp(X) + 40)   # height from the data aspect
    fig = plt.figure(figsize=(FIG_W, panel_h + 1.3))         # FIG_W - 1 in: the width of the panel
    gs = fig.add_gridspec(2, 1, height_ratios=[panel_h, 0.16], hspace=0.5)
    ax, cax = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    lc = LineCollection(segs, cmap=cmap, norm=norm, linewidth=3.4, capstyle="round")
    lc.set_array(0.5 * (err[:-1] + err[1:]))
    ax.add_collection(lc)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(X.min() - 20, X.max() + 20)
    ax.set_ylim(Y.min() - 20, Y.max() + 20)
    ax.set_xlabel(r"$x_1$ [mm]")
    ax.set_ylabel(r"$x_2$ [mm]")
    ax.set_title(TAG_TEST, loc="left", fontsize=LEGEND_FS + 1, color=C_AX, pad=5)
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax,
                      orientation="horizontal", extend="max")
    cb.set_label(r"absolute error [a.u.]", fontsize=LABEL_FS)
    cb.ax.tick_params(labelsize=TICK_FS, direction="in", colors=C_AX)
    tags, pad = [], 12.0                                     # [mm] around the marked path
    for j, (s_a, s_b, ref, anchor) in enumerate(boxes):
        m = (s >= s_a) & (s <= s_b)
        x0, x1 = X[m].min() - pad, X[m].max() + pad
        y0, y1 = Y[m].min() - pad, Y[m].max() + pad
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, edgecolor=C_AX, lw=1.1,
                               ls="-" if j == 0 else (0, (4, 2)), zorder=6))
        off = 6.0                                            # label clear of the box
        y_top, y_bot = (y0, y1) if ax.yaxis_inverted() else (y1, y0)
        up, down = (-off, off) if ax.yaxis_inverted() else (off, -off)
        cx, cy = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
        pt = {"south": (cx, y_top + up), "north": (cx, y_bot + down),
              "west": (x1 + off, cy), "east": (x0 - off, cy)}[anchor]
        tags.append((ax, pt[0], pt[1], ref, anchor))
    finish(fig, [ax])
    save_labels(fig, name, tags)
    save(fig, name)


def fig_example_topviews(name, w_rel=0.6):
    """Top views of two objects of different shape, equal axes, tiles of the same width. Drawn at
    w_rel * FIG_W and included at w_rel * \\linewidth (rule 15), 0.6 here."""
    s = np.linspace(0, 2 * np.pi, 600)
    shapes = [("training set", 800 * np.cos(s), 300 * np.sin(s)),
              ("test set", 480 * np.cos(s), 230 * np.sin(s))]
    pad = 30.0
    lims = [((X.min() - pad, X.max() + pad), (Y.min() - pad, Y.max() + pad)) for _, X, Y in shapes]
    ratios = [(lv[1] - lv[0]) / (lh[1] - lh[0]) for lh, lv in lims]   # height / width of the data
    hspace, left, right, bottom, top = 0.3, 0.14, 0.98, 0.1, 0.94
    W = w_rel * FIG_W
    fig_h = W * (right - left) * (sum(ratios) + hspace * np.mean(ratios)) / (top - bottom)
    fig = plt.figure(figsize=(W, fig_h))
    gs = fig.add_gridspec(len(shapes), 1, height_ratios=ratios, hspace=hspace, left=left,
                          right=right, bottom=bottom, top=top)
    axes = [fig.add_subplot(gs[i]) for i in range(len(shapes))]
    for ax, (tag, X, Y), (lh, lv) in zip(axes, shapes, lims):
        ax.plot(X, Y, color=BLUE, lw=1.4)
        ax.set_xlim(*lh)
        ax.set_ylim(*lv)
        ax.set_aspect("equal", adjustable="datalim")         # keep the tile width, adapt limits
        ax.set_ylabel(r"$x_2$ [mm]")
        ax.set_title(tag, loc="left", fontsize=LEGEND_FS + 2, color=C_AX, pad=4)
    axes[-1].set_xlabel(r"$x_1$ [mm]")
    fig.align_ylabels(axes)
    finish(fig, axes)
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
    axes, y_max = [], 0.0
    for j, (c, mk, lab, rmse) in enumerate(rows):
        ax = fig.add_subplot(gs[j], sharey=axes[0] if j else None)
        per_piece = rmse * (1.0 + 0.35 * rng.standard_normal((250, 1))
                            + 0.10 * rng.standard_normal((250, h.size)))
        Q = np.percentile(np.maximum(per_piece, 0.0), RAMP_Q, axis=0)
        ramp_bands(ax, h, Q, color=c)
        ax.plot(h, rmse, color=c, marker=mk, ms=4.0, lw=1.8, mec="white", mew=0.6, zorder=4)
        y_max = max(y_max, Q[int(np.argmin(np.abs(RAMP_Q - 97.0)))].max())
        ax.set_xlim(h[0], h[-1])
        ax.set_xticks([0, 400, 800])                         # no tick at the right limit
        ax.set_xlabel(r"horizon $h$ [ms]")
        ax.set_title(lab, fontsize=LEGEND_FS + 1, color=C_AX, pad=5)
        if j:
            ax.tick_params(labelleft=False)                  # shared y: labels on the left only
        axes.append(ax)
    axes[0].set_ylim(0, 1.02 * y_max)
    axes[0].set_yticks([0, 5, 10])                           # short labels: "0.0" would touch the x "0"
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
    legend_top(ax, ncol=2, title=TAG_TEST)
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
    legend_top(ax, ncol=2, title=TAG_TEST)
    finish(fig, [ax])
    save(fig, f"{name}_b")


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
if want("fig_example_topviews"):
    fig_example_topviews("fig_example_topviews")
if want("fig_example_tiles"):
    fig_example_tiles("fig_example_tiles")
if want("fig_example_pair"):
    fig_example_pair("fig_example_pair")
show_if_requested()
