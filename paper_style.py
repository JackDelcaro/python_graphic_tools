"""
paper_style.py - figure style for the paper, two-column or single-column.

Draw at twice the printed width, include at the printed width (\\linewidth): FIG_W = 7 in for a
column of a two-column paper (fonts 16/14/12 pt), 11 in for the text width of a single-column
paper such as NeurIPS (fonts 18/16/14 pt). Printed, the text is nominally 8/7/6 pt (two) and 9/8/7 pt
(single); section 9 says why the real size is a little larger. Fixed palette assigned by role. PDF (for LaTeX) + SVG + PNG (300 dpi) in images/paper/
(images/paper_single/ for --layout single), with a transparent figure background and white panels.

    from paper_style import *
    fig, axes = stacked(height("snapshot"), [2.0, 1.0])
    ...
    finish(fig, axes)
    save(fig, "fig_name")
    show_if_requested()                  # once, at the end of the script

--layout two|single picks the document (env. PAPER_LAYOUT; default two); --show opens interactive
windows instead of writing files; --only fig_a,fig_b draws a subset. Without LaTeX on the PATH (or
with PAPER_USETEX=0) the text is drawn with matplotlib's own maths font: fine for a draft, the
final figures need LaTeX.
"""

import argparse
import os
import shutil
from pathlib import Path

import matplotlib

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--show", action="store_true", help="interactive windows instead of files")
_ap.add_argument("--only", default="", help="comma-separated figure-name prefixes to draw")
_ap.add_argument("--layout", default=os.environ.get("PAPER_LAYOUT", "two"), choices=("two", "single"),
                 help="two: one column of a two-column paper; single: text width of a single-column paper")
ARGS, _ = _ap.parse_known_args()
matplotlib.use("TkAgg" if ARGS.show else "Agg")          # before pyplot is imported
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

LAYOUT = ARGS.layout
OUT = Path(__file__).resolve().parent / "images" / ("paper" if LAYOUT == "two" else f"paper_{LAYOUT}")

# ---- layout: the width a figure is included at, and the fonts ----------------------------------
# a new document class is one line: its \linewidth in a figure [in], the drawn font sizes [pt]
# (legend, tick, label) and side, the left and right margin of the panels as a fraction of the width
# (None: matplotlib's 0.125 / 0.9). A wide figure needs a smaller side margin than a narrow one,
# otherwise tight cropping removes a lot of white and the text prints larger than planned (section 9).
LAYOUTS = {
    "two":    dict(width=3.5, fonts=(12, 14, 16), side=None),   # elsarticle 5p: \columnwidth = 252 pt
    "single": dict(width=5.5, fonts=(14, 16, 18), side=0.05),   # NeurIPS, ICLR: \textwidth = 5.5 in
}
SCALE = 0.5                                   # printed size / drawn size, in every layout
PRINT_W = LAYOUTS[LAYOUT]["width"]            # [in]; \linewidth in a figure environment
FIG_W = PRINT_W / SCALE                       # [in] drawn width of a full figure: 7.0 / 11.0
HALF = 0.48                                   # two figures side by side: each 0.48 \linewidth
LEGEND_FS, TICK_FS, LABEL_FS = LAYOUTS[LAYOUT]["fonts"]

# height / width of a figure of each type (section 2); a wide single-column figure is lower
ASPECT = {
    "two":    dict(curve=0.50, tiles=0.45, flat=0.20, snapshot=0.78, stack3=0.72, split=0.55,
                   grid=0.86, pair=0.80),
    "single": dict(curve=0.36, tiles=0.30, flat=0.14, snapshot=0.48, stack3=0.44, split=0.38,
                   grid=0.64, pair=0.74),
}


def height(kind, s=1.0):
    """Drawn height [in] of a figure of type `kind` that is drawn at s * FIG_W (and included at
    s * \\linewidth): s = HALF for one of two figures side by side."""
    return s * FIG_W * ASPECT[LAYOUT][kind]


C_AX = "#262626"                              # spines, ticks, labels, grid

# ---- palette: fixed slots, assigned by role, never cycled -----------------------------------
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
MAGENTA, GREEN, VIOLET, RED = "#e87ba4", "#008300", "#4a3aa7", "#e34948"
INK_2, MUTED, NEUTRAL = "#52514e", "#898781", "#c3c2b7"
C_MEAS, C_PROPOSED, C_COMPARE, C_INPUT, C_BASE = BLUE, ORANGE, AQUA, YELLOW, INK_2
C_PREV = ["#bcd4f2", "#7fabe6"]               # cycle k-2, cycle k-1 (tints of BLUE)
LS_BASE = (0, (4, 2))                         # baseline model
LS_REF = (0, (6, 3))                          # shared or global reference value

# ---- labels: one spelling in every figure ---------------------------------------------------
LAB_PROPOSED, LAB_COMPARE = "proposed", "comparison"
LAB_BASE = r"baseline $y_{\mathrm{base}}$"
PREV_LABELS = [r"cycle $k-2$", r"cycle $k-1$"]
TAG_TRAIN, TAG_TEST = "training set", "test set"

USETEX = shutil.which("latex") is not None and os.environ.get("PAPER_USETEX", "1") != "0"
if not USETEX:
    print("paper_style: no LaTeX (or PAPER_USETEX=0): drawing with matplotlib's own maths font, "
          "the text differs slightly from the paper; install LaTeX for the final figures")
plt.rc("text", usetex=USETEX)
plt.rc("font", family="serif")
if not USETEX:
    plt.rcParams.update({"mathtext.fontset": "cm", "font.serif": ["cmr10", "DejaVu Serif"],
                         "axes.formatter.use_mathtext": True})
plt.rcParams.update({
    "text.latex.preamble": r"\usepackage{amsmath}\usepackage{amssymb}\usepackage{bm}",
    "axes.labelsize": LABEL_FS, "xtick.labelsize": TICK_FS, "ytick.labelsize": TICK_FS,
    "legend.fontsize": LEGEND_FS, "lines.linewidth": 1.5, "lines.solid_capstyle": "round",
    "axes.linewidth": 0.8, "xtick.major.width": 0.8, "ytick.major.width": 0.8,
    "legend.frameon": False, "legend.handlelength": 1.6, "legend.handletextpad": 0.5,
    "legend.columnspacing": 1.2, "legend.labelspacing": 0.35, "legend.borderaxespad": 0.3,
})
if LAYOUTS[LAYOUT]["side"] is not None:
    plt.rcParams.update({"figure.subplot.left": LAYOUTS[LAYOUT]["side"],
                         "figure.subplot.right": 1.0 - LAYOUTS[LAYOUT]["side"]})


def want(name):
    """True if the figure is selected by --only (or no selection was given)."""
    only = [s for s in ARGS.only.split(",") if s]
    return not only or any(name.startswith(o) for o in only)


def style_ax(axes, color=C_AX):
    """Boxed panel: hairline grid, ticks inward on all four sides, one ink colour
    (same as plot_style.style_ax)."""
    for ax in (axes if np.iterable(axes) else [axes]):
        ax.grid(True, linestyle="-", linewidth=0.5, alpha=0.208, color=color)
        ax.tick_params(axis="both", which="both", direction="in",
                       top=True, right=True, bottom=True, left=True, colors=color)
        ax.xaxis.label.set_color(color)
        ax.yaxis.label.set_color(color)
        ax.title.set_color(color)
        for spine in ax.spines.values():
            spine.set_edgecolor(color)


def stacked(height, ratios, sharex=True, hspace=0.05, width=None):
    """Panels stacked on one x axis; only the bottom panel keeps its tick labels.
    width: drawn width [in], FIG_W by default; s * FIG_W for a figure included at s * \\linewidth."""
    fig = plt.figure(figsize=(width or FIG_W, height))
    gs = fig.add_gridspec(len(ratios), 1, height_ratios=ratios, hspace=hspace)
    axes = [fig.add_subplot(gs[0])]
    for i in range(1, len(ratios)):
        axes.append(fig.add_subplot(gs[i], sharex=axes[0] if sharex else None))
    if sharex:
        for a in axes[:-1]:
            a.tick_params(labelbottom=False)
    return fig, axes


def legend_top(ax, handles=None, ncol=3, y=1.0, **kw):
    """Frameless legend centred above the panel; title= names the data set."""
    kw = dict(dict(loc="lower center", bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False,
                   fontsize=LEGEND_FS, handlelength=1.6, columnspacing=1.2,
                   title_fontsize=LEGEND_FS + 1), **kw)
    leg = ax.legend(handles=handles, **kw) if handles is not None else ax.legend(**kw)
    if kw.get("title"):
        leg.get_title().set_color(C_AX)
    return leg


def finish(fig, axes):
    """Style every panel, keep the grid under the data, smart zoom with --show."""
    style_ax(axes)
    for ax in axes:
        ax.set_axisbelow(True)
    if ARGS.show:
        try:
            from smart_zoom import attach
            attach(fig)
        except ImportError:
            pass


def save(fig, name):
    """PDF (for LaTeX) + SVG + PNG at 300 dpi; transparent figure background, white panels.
    Nothing is written with --show. Prints the saved width: the figure prints at
    SCALE * saved width, so include it at that width as a fraction of \\linewidth (about the s it
    was drawn for, rule 15)."""
    if ARGS.show:
        return
    OUT.mkdir(parents=True, exist_ok=True)
    fig.patch.set_alpha(0.0)
    for ax in fig.axes:
        ax.patch.set_facecolor("white")
        ax.patch.set_alpha(1.0)
    for ext, kw in (("pdf", {}), ("svg", {}), ("png", {"dpi": 300})):
        fig.savefig(OUT / f"{name}.{ext}", bbox_inches="tight", pad_inches=PAD_IN, **kw)
    w_in = fig.get_tightbbox(fig.canvas.get_renderer()).width + 2 * PAD_IN
    plt.close(fig)
    print(f"  -> {OUT.name}/{name}.pdf  (saved {w_in:.2f} in = {w_in * SCALE / PRINT_W:.2f} "
          f"\\linewidth at scale {SCALE})")


# ---- a distribution as a transparency ramp ---------------------------------------------------
RAMP_Q = np.r_[0.5, np.arange(1.0, 100.0), 99.5]   # quantile grid the ramp is built from
RAMP_ALPHA, RAMP_GAMMA = 0.38, 1.1                 # opacity at the median, fade towards the tails


def ramp_bands(ax, x, Q, qs=RAMP_Q, color=C_PROPOSED, n_bands=40, alpha_max=RAMP_ALPHA,
               gamma=RAMP_GAMMA, zorder=1):
    """Distribution as a transparency ramp made of nested filled bands (patches): one connected
    surface along x, vector in the PDF, following the quantile curves exactly. Band k spans the
    central range whose half-width in quantile units is t_k, so the opacities add up to
    alpha_max * (1 - t^gamma): opaque at the median, transparent at the tails.
    Q: quantile function of the distribution, shape (len(qs), len(x))."""
    a = alpha_max / n_bands
    for k in range(1, n_bands + 1):
        t = (1.0 - k / n_bands) ** (1.0 / gamma)
        lo_p, hi_p = 50.0 * (1.0 - t), 50.0 * (1.0 + t)
        lo = np.array([np.interp(lo_p, qs, Q[:, j]) for j in range(Q.shape[1])])
        hi = np.array([np.interp(hi_p, qs, Q[:, j]) for j in range(Q.shape[1])])
        ax.fill_between(x, lo, hi, color=color, alpha=a, lw=0, zorder=zorder)


PAD_IN = 0.02                                 # pad_inches of save(), needed by save_labels()


def save_labels(fig, name, items):
    """Write images/paper/<name>_labels.tex: the position of each label as a fraction of the
    SAVED image, so that LaTeX can write the text on top of the included graphic (\\ovlfig /
    \\ovltag macros, section 8). Use it for labels that must follow the document, e.g.
    "Fig. 7" on the box that marks where another figure is taken.
    items: (axes, x_data, y_data, latex_label, tikz_anchor)."""
    if ARGS.show or not items:
        return
    fig.canvas.draw()
    bb = fig.get_tightbbox(fig.canvas.get_renderer())                  # [in]
    x0, y0 = bb.x0 - PAD_IN, bb.y0 - PAD_IN
    w, h = bb.width + 2 * PAD_IN, bb.height + 2 * PAD_IN
    out = [f"% {name}: label positions as a fraction of the image (generated, do not edit)"]
    for ax, x, y, ref, anchor in items:
        xd, yd = np.asarray(ax.transData.transform((x, y))) / fig.dpi
        out.append(rf"\ovltag{{{(xd - x0) / w:.4f}}}{{{(yd - y0) / h:.4f}}}{{{anchor}}}{{{ref}}}")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}_labels.tex").write_text("\n".join(out) + "\n")
    print(f"  -> {OUT.name}/{name}_labels.tex ({len(items)} labels)")


def show_if_requested():
    if ARGS.show:
        plt.show()


def viridis_colours(values, lo=0.05, hi=0.85):
    """Colours for an ordered series (N_prev = 1..5, cycles in time order): dark = first."""
    cm = plt.get_cmap("viridis")
    return {v: cm(c) for v, c in zip(values, np.linspace(lo, hi, len(values)))}
