# How to draw figures for the paper (two-column and single-column)

This guide describes how the figures of the paper are drawn, so that all figures look like one
set. Use it for every new figure. Everything it refers to is in this folder: the style module
`paper_style.py` and the zoom module `zoom_plot.py`, the runnable recipes `fig_examples.py`, a
template for a new figure `fig_template.py`, and LaTeX test sheets in `latex/` (start with
`README.md`).

The guide covers two document layouts, and the style module switches between them with one flag
(`--layout`). **Ask which one the paper uses before you draw the first figure.** The rest of the
guide says where the two differ:

| layout (`--layout`) | document | a full figure is included at | drawn at (`FIG_W`) | label / tick / legend font, printed |
|---|---|---|---|---|
| `two` (default) | two-column, elsarticle `5p` | `\columnwidth`, 252 pt = 3.5 in | 7.0 in | 8 / 7 / 6 pt |
| `single` | single-column, NeurIPS / ICLR | `\textwidth` = 5.5 in (397.5 pt) | 11.0 in | 9 / 8 / 7 pt |

Everything below holds for both layouts unless it is marked *single-column*. A script written
once draws both: it takes its sizes from `FIG_W` and `height(kind)` and never writes inches
(section 5). What is specific to a single-column paper (half-width figures, rows of tiles, the page
budget) is collected in [section 10](#10-single-column-papers-neurips-iclr).

Contents: [1 rules](#1-the-look-in-sixteen-rules) · [2 size](#2-size) ·
[3 colours and lines](#3-colours-lines-markers) · [4 style module](#4-the-style-module) ·
[5 script layout](#5-script-layout) · [6 recipes](#6-recipes) · [7 text](#7-text-in-figures) ·
[8 LaTeX](#8-latex) · [9 checklist](#9-checklist-and-traps) ·
[10 single-column papers](#10-single-column-papers-neurips-iclr)

---------------------------------------------------------------------------------------------------

## 1. The look in sixteen rules

1. **Draw at twice the printed width, include at the printed width** (`\linewidth`). A full figure
   is drawn `FIG_W` wide: 7 in and included at `\columnwidth` (3.5 in) in a two-column paper, 11 in
   and included at `\textwidth` (5.5 in) in a single-column paper. Everything is scaled by 0.5 in the
   paper, so labels / ticks / legends of 16 / 14 / 12 pt (`two`) or 18 / 16 / 14 pt (`single`) print
   at 8 / 7 / 6 pt or 9 / 8 / 7 pt. Line widths and marker sizes scale by 0.5 too, in both layouts
   (`lw` 2.0 prints at 1 pt). The sizes are nominal: tight cropping makes the saved figure a little
   narrower than `FIG_W`, so the text prints a little larger (section 9; `save` prints the width).
2. **LaTeX text** (`usetex`, serif): the same font as the paper, math written as math
   (`$y_{\mathrm{base}}$`, `$k-1$`).
3. **Boxed panels**: four spines, ticks pointing inward on all four sides, hairline grid (0.5 pt,
   opacity 0.208) under the data, one ink colour `#262626` for spines, ticks and labels.
4. **One colour per method or data type, the same in every figure of the paper.** A method that is
   lilac in one figure is lilac in all of them, so a caption can say "the lilac curve" and the reader
   never has to learn a legend again. Which colours is your choice: the kit prescribes none (section 3
   has example palettes). Choose them once, keep them in one table (the assignment block of
   `paper_style.py`) and do not let matplotlib cycle colours from figure to figure. A light preference
   only: measured data in blue. Lines differ in marker or dash as well, so a figure survives a
   grey-scale print.
5. **Stacked panels share the x axis** (`hspace = 0.04` to `0.05`, the panels nearly touch); only
   the bottom panel has tick labels, and the height ratios give the main panel the room. Two
   windows of the same signal are two columns of closed tiles (no broken axis).
6. **One legend per figure, at a house position.** Above the panel, centred and frameless
   (`legend_at(ax)`, the default: it never covers data), or inside the panel in a rounded box
   (`legend_at(ax, "inside")`, only where the curves leave a corner free); `boxed=True` puts the
   rounded box round the legend above too. Panels that share their colours get **one** legend above
   everything (`legend_above_all(fig, axes)`), not one per panel. The title names the data set
   (`training set` / `test set`). Recipe 6.8.
7. **Axis labels hold a symbol and a unit** (`$y$ [a.u.]`, `forecast horizon $h$ [ms]`). The
   explanation goes into the caption, not into the figure.
8. **Context as shading** (the forecast region in light grey), references and zero lines as thin
   muted lines.
9. **A distribution is drawn as a transparency ramp or as a patch** (recipe 6.2 shows both).
   *Ramp* (`ramp_bands`): many nested percentile bands of one colour, each with a low opacity, so the
   shading is opaque at the median and fades towards the tails, with no visible band edges. *Patch*
   (`patch_bands`): one percentile range with a flat tint, by default 25-75 %: one patch, not several
   overlapping ones; its edges are easy to read numbers from. Both are filled patches, so they are one
   connected surface along x and stay vector in the PDF. **The shaded distribution and the line drawn
   on it must be the same quantity**, otherwise the line does not run inside its shading: shade the
   metric of each piece of the data set and draw the metric of the whole data set.
10. **Transparent figure background, white panels, saved three times**: PDF (vector, for LaTeX),
    SVG (vector, for editing) and PNG at 300 dpi (preview). A fourth file, `<name>_white.png`, is the
    same PNG on an opaque white background: **it exists only for markdown files and viewers with a
    dark background** (README, GitHub dark theme, VS Code dark preview), where the dark labels of the
    transparent files are invisible. Never use it in LaTeX or on slides.
11. **Scripts save by default** (`Agg` backend); `--show` opens interactive windows with smart zoom,
    `--only <prefix>` draws a subset.
12. **Every number a figure shows is printed to the terminal** by the same run, so the text and
    the captions quote numbers from the same data as the figure.
13. **A figure that should take less space on the page** is drawn at `s * FIG_W` and included at
    `s\linewidth` (`s = HALF = 0.48` for one of two figures side by side). The ratio between the two
    is what sets the printed font size, so scaling both keeps the text of the figure exactly as large
    as everywhere else; only the drawing gets smaller. Do not shrink the font sizes instead.
14. **A zoom shows what it zooms**: an inset always comes with the rectangle on the parent axes
    and the two lines that join them (`zoom_plot`, recipe 6.4). An inset alone leaves the reader
    guessing which part of the curve it is.
15. **Single-column: one panel is half width, a full-width figure is a row.** 5.5 in is wide for a
    single curve. A one-panel figure is drawn at `HALF * FIG_W` and stands next to another figure
    (or next to the text, `wrapfigure`); a figure that takes the full text width holds a row of tiles
    or a long time series (recipes 6.6, 6.7; section 10).
16. **Figures that stand side by side have the same height and the same build**: drawn with
    `height("pair", HALF)`, one legend row (plus title) above the panel in both, one label line
    under it. Tight cropping then leaves them the same height and the two frames line up at print
    size; a legend or label in only one of them makes them differ (recipe 6.7).

## 2. Size

Width is `FIG_W` (7.0 in with `two`, 11.0 in with `single`), unless the figure is meant to take less
space on the page (rule 13: `s * FIG_W`, included at `s\linewidth`). The height is a fraction of the
width, taken from `height(kind)` so that the script draws both layouts. A full-width figure of a
single-column paper is wider than it is tall, so its ratios are lower; the printed height in inches
is given in brackets, the number to judge against the page:

| figure type | `height(kind)` | `two` | `single` | layout | recipe |
|---|---|---|---|---|---|
| a metric vs. a parameter, with its distribution | `"curve"` | 0.40 (1.4 in) | 0.29 (1.6 in) | 1 panel, ramp + lines | `fig_example_bands` |
| the same per model, as tiles; curves with a zoom | `"tiles"` | 0.36 (1.3 in) | 0.24 (1.3 in) | 1 row of tiles, shared y, `wspace 0.08` | `fig_example_tiles`, `fig_example_convergence` |
| one panel: metric vs. horizon | `"curve"` | 0.36 to 0.45 | 0.27 to 0.32 | 1 panel | `fig_template` |
| flat one-panel figure: parameter sweep | `"flat"` | 0.16 (0.6 in) | 0.11 (0.6 in) | 1 panel, one legend row, data set named inside | (none) |
| signal + residual at one instant | `"snapshot"` | 0.62 (2.2 in) | 0.38 (2.1 in) | 2 stacked, ratios 2.0 : 1.15 | `fig_example_snapshot` |
| geometry signal, signal, residual | `"stack3"` | 0.58 (2.0 in) | 0.35 (1.9 in) | 3 stacked, ratios 0.8 : 1.4 : 0.7 | (none) |
| two windows of a signal, signal + residual | `"split"` | 0.44 (1.5 in) | 0.30 (1.65 in) | 2 rows x 2 columns of tiles, ratios 1.4 : 0.7, `wspace 0.1`; with a geometry signal (3 rows) use `"stack3"` | `fig_example_split` |
| a 2 x 2 grid of panels | `"grid"` | 0.69 (2.4 in) | 0.51 (2.8 in) | gap between the rows about 1.2 in (x label, legend and titles sit in it), `wspace 0.3` | (none) |
| one of two figures side by side | `"pair"`, `s = HALF` | 0.64 | 0.59 (of its own width: 1.6 in) | 1 panel, 2 legend entries per row | recipe 6.7 |
| map coloured by a value | from the data aspect | | | map + vertical colour bar on the right | `fig_example_map` |

A figure taller than about `0.9 * FIG_W` takes most of a column of a two-column paper; in a
single-column paper keep a full-width figure under 3 in printed (`"grid"`), the page is 9 in high
and the page limit counts figures (section 10). Shrink the secondary panels (residuals, geometry signals)
first; keep the main panel readable.

**Widths a figure is included at** (`s`, rule 13), as a fraction of `\linewidth`:

| `s` | `two` (3.5 in column) | `single` (5.5 in text width) | use |
|---|---|---|---|
| 1.0 | 3.5 in | 5.5 in | a full figure: rows of tiles, time series, grids |
| `HALF` = 0.48 | 1.7 in (too small for the 8 / 7 / 6 pt text: do not) | 2.64 in | two figures side by side (recipe 6.7) |
| 0.6 | 2.1 in | 3.3 in | a map of a compact object; also `wrapfigure` |

The widths of the document classes this guide has been used with (measure a new class with
`\typeout{\the\textwidth, \the\columnwidth, \the\linewidth}` in the preamble or the first line of the
body and read it in the log; a `\showthe` stops a non-interactive build):

| class | `\linewidth` in a figure | `LAYOUTS` entry |
|---|---|---|
| elsarticle `5p`, two columns | `\columnwidth` = 252 pt = 3.5 in | `two` |
| NeurIPS (`neurips_20xx.sty`), ICLR | `\textwidth` = 5.5 in = 397.5 pt | `single` |
| any other single-column class | its `\textwidth` | add a line (section 4) |

## 3. Colours, lines, markers

**The kit prescribes no colours.** The one rule is rule 4: each method or data type keeps one colour in
every figure of the paper. Which colours is your choice: take them from a palette you like.
`palettes/paper_color_palette.md` shows eight example palettes with their hex and RGB codes and lighter
and darker variants (regenerate with `python palettes/generate_paper_color_palette.py`); they are
examples, not requirements, and [coolors.co](https://coolors.co/) is a good place to explore and generate
more. Hints, none of them rules: solid colours for lines and markers, lighter tints for bands and areas;
a marker or a dash on every line, so a figure survives a grey-scale print; and one light preference,
measured data in blue.

The examples of this folder use two colours, lilac `#AE78CC` and blue `#1D4E89` (the first and last colour
of the first example palette), plus greys:

| what | colour | drawn as | z-order |
|---|---|---|---|
| measured signal $y$, residual $r$ | `C_MEAS` = `BLUE #1D4E89` (the light preference) | lw 2.0; markers `o` (ms 3) where the samples matter | 4 |
| proposed method | `C_PROPOSED` = `LILAC #AE78CC` | solid lw 2.0; marker `D` in metric plots | 6 |
| comparison method | `C_COMPARE` = `BLUE` | solid lw 1.8; marker `o` in metric plots | 5 |
| baseline model $y_{\mathrm{base}}$ | `C_BASE` = `INK_2 #52514e` | dashed `LS_BASE` `(0, (4, 2))`, lw 1.4 to 1.8; marker `s` | 3 |
| previous cycles $k-2$, $k-1$ | `C_PREV`: tints of blue | lw 1.2, markers `o` ms 2.8; older = lighter | 2 |
| any further method or signal | your choice | lw 1.8 | |
| limits, zero lines | `MUTED #898781` | lw 0.9 to 1.0; a limit dotted `(0, (1, 1.5))` | 1 |
| context shading (forecast region) | `NEUTRAL #c3c2b7` | `axvspan`, alpha 0.28 | 0 |
| ordered series ($N_{\mathrm{prev}} = 1..5$, cycles in time) | `viridis` from 0.05 to 0.85 | dark = first | |
| a magnitude along a path (error map) | seaborn `rocket_r` | always with a colour bar | |

Measured data and the comparison method are both blue here because no example figure shows both. A paper
that shows both in one figure gives the comparison method another colour of its palette.

* Keep the mapping in every figure of the paper, so captions stay short.
* In a figure without methods (for example a parameter sweep) the palette colours can label parameter
  values.
* A marker on a line gets a white edge: `mec="white", mew=0.6`, `ms=4.5`.
* A reference value shared by several curves: dashed `(0, (6, 3))`.
* Line widths, marker sizes and dash lengths are drawn points and print at half size in both
  layouts, so this table holds for both.

## 4. The style module

`paper_style.py` and `zoom_plot.py` sit in the root of this folder, next to the figure scripts
(`fig_examples.py`, `fig_template.py`); they are the two code blocks below. `--layout` (or the
environment variable `PAPER_LAYOUT`) picks `two` or `single`, and `FIG_W`, the font sizes and the
figure heights (`height(kind)`) follow from it. `smart_zoom.py`, the interactive zoom of `--show`,
is optional and not part of this folder.

```python
"""
paper_style.py - figure style for the paper, two-column or single-column.

Draw at twice the printed width, include at the printed width (\\linewidth): FIG_W = 7 in for a
column of a two-column paper (fonts 16/14/12 pt), 11 in for the text width of a single-column
paper such as NeurIPS (fonts 18/16/14 pt). Printed, the text is nominally 8/7/6 pt (two) and 9/8/7 pt
(single); section 9 says why the real size is a little larger. One colour per method, the same in every figure. PDF (for LaTeX) + SVG + PNG (300 dpi) in images/paper/
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
    "two":    dict(curve=0.40, tiles=0.36, flat=0.16, snapshot=0.62, stack3=0.58, split=0.44,
                   grid=0.69, pair=0.64),
    "single": dict(curve=0.29, tiles=0.24, flat=0.11, snapshot=0.38, stack3=0.35, split=0.30,
                   grid=0.51, pair=0.59),
}


def height(kind, s=1.0):
    """Drawn height [in] of a figure of type `kind` that is drawn at s * FIG_W (and included at
    s * \\linewidth): s = HALF for one of two figures side by side."""
    return s * FIG_W * ASPECT[LAYOUT][kind]


C_AX = "#262626"                              # spines, ticks, labels, grid

# ---- colours: ONE colour per method or data type, the same in every figure of the paper ---------------
# The kit prescribes none (example palettes: palettes/). Keep the choices of a paper in one table like this.
BLUE, LILAC = "#1D4E89", "#AE78CC"                    # the two colours of the examples
INK_2, MUTED, NEUTRAL = "#52514e", "#898781", "#c3c2b7"   # dark grey (baseline), limits and zero lines, context shading

# The assignment used by the examples. A paper makes its own table once and keeps it in every figure.
C_MEAS = BLUE                                         # a light preference: measured data in blue
C_PROPOSED, C_COMPARE, C_BASE = LILAC, BLUE, INK_2
C_PREV = ["#bbcadc", "#7795b8"]                       # cycle k-2, cycle k-1 (tints of BLUE: older = lighter)
LS_BASE = (0, (4, 2))                                 # baseline model
LS_REF = (0, (6, 3))                                  # shared or global reference value

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
    """Frameless legend centred above the panel, close to it; title= names the data set."""
    kw = dict(dict(loc="lower center", bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False,
                   fontsize=LEGEND_FS, handlelength=1.6, columnspacing=1.2, borderaxespad=0.1,
                   borderpad=0.15, title_fontsize=LEGEND_FS + 1), **kw)
    leg = ax.legend(handles=handles, **kw) if handles is not None else ax.legend(**kw)
    if kw.get("title"):
        leg.get_title().set_color(C_AX)
    return leg


LEGEND_ROUND = 0.3      # corner radius of a boxed legend, in units of the legend font size (matplotlib: 0.2)


def _box(leg, boxed):
    """A boxed legend: rounded corners (LEGEND_ROUND), thin light-grey edge, white face; or no frame."""
    frame = leg.get_frame()
    frame.set_visible(boxed)
    if boxed:
        frame.set_boxstyle("round", pad=0, rounding_size=LEGEND_ROUND)
        frame.set_facecolor("white")
        frame.set_edgecolor("0.75")
        frame.set_linewidth(0.8)
        frame.set_alpha(0.9)
    return leg


def legend_at(ax, where="above", boxed=None, ncol=None, handles=None, **kw):
    """Legend of one panel at a house position (rule 6).
    where="above"   centred above the panel, frameless: the default, it never covers data
    where="inside"  lower right, in a rounded box, over the panel: only where the curves leave a corner free
    boxed=None gives frameless above and boxed inside; True / False forces the rounded box on or off.
    ncol defaults to 3 above (one row) and 1 inside (stacked); title= names the data set."""
    boxed = (where == "inside") if boxed is None else boxed
    if where == "above":
        k = dict(borderpad=0.4, borderaxespad=0.3) if boxed else {}   # a frameless legend sits close
        k.update(kw)
        leg = legend_top(ax, handles, ncol=3 if ncol is None else ncol, frameon=boxed, **k)
    elif where == "inside":
        k = dict(loc="lower right", ncol=1 if ncol is None else ncol, frameon=boxed, fontsize=LEGEND_FS,
                 handlelength=1.6, title_fontsize=LEGEND_FS + 1)
        k.update(kw)
        leg = ax.legend(handles=handles, **k) if handles is not None else ax.legend(**k)
        if k.get("title"):
            leg.get_title().set_color(C_AX)
    else:
        raise ValueError(f'where must be "above" or "inside", not {where!r}')
    return _box(leg, boxed)


def legend_above_all(fig, axes, boxed=False, ncol=3, rise=None, handles=None, labels=None, **kw):
    """ONE legend above a row of panels that share their colours (rule 6), centred on the figure.
    rise [in] is the distance above the top of the panels; the default sits just above the panel titles,
    pass 0.06 if the panels have none. The entries are those of the first panel unless handles= and
    labels= are given."""
    if handles is None:
        handles, labels = axes[0].get_legend_handles_labels()
    if rise is None:                                         # just above the panel titles
        rise = ((LEGEND_FS + 1) * 0.75 + 5) / 72 + 0.06
    y = axes[0].get_position().y1 + rise / fig.get_figheight()
    pad = dict(borderpad=0.4, borderaxespad=0.3) if boxed else dict(borderpad=0.15, borderaxespad=0.1)
    kw = dict(dict(loc="lower center", bbox_to_anchor=(0.5, y), ncol=ncol, frameon=boxed, fontsize=LEGEND_FS,
                   handlelength=1.6, columnspacing=1.2, title_fontsize=LEGEND_FS + 1, **pad), **kw)
    leg = fig.legend(handles, labels, **kw)
    if kw.get("title"):
        leg.get_title().set_color(C_AX)
    return _box(leg, boxed)


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
    Also <name>_white.png: the same PNG on an opaque white background, ONLY for markdown files and
    viewers with a dark background (README, GitHub dark theme, VS Code dark preview), where the dark
    labels of the transparent files are invisible. Never use it in LaTeX or on slides.
    Nothing is written with --show. Prints the saved width: the figure prints at
    SCALE * saved width, so include it at that width as a fraction of \\linewidth (about the s it
    was drawn for, rule 13)."""
    if ARGS.show:
        return
    OUT.mkdir(parents=True, exist_ok=True)
    fig.patch.set_alpha(0.0)
    for ax in fig.axes:
        ax.patch.set_facecolor("white")
        ax.patch.set_alpha(1.0)
    for ext, kw in (("pdf", {}), ("svg", {}), ("png", {"dpi": 300})):
        fig.savefig(OUT / f"{name}.{ext}", bbox_inches="tight", pad_inches=PAD_IN, **kw)
    fig.patch.set_alpha(1.0)                                 # opaque white background: markdown files only
    fig.patch.set_facecolor("white")
    fig.savefig(OUT / f"{name}_white.png", bbox_inches="tight", pad_inches=PAD_IN, dpi=300)
    w_in = fig.get_tightbbox(fig.canvas.get_renderer()).width + 2 * PAD_IN
    plt.close(fig)
    print(f"  -> {OUT.name}/{name}.pdf  (saved {w_in:.2f} in = {w_in * SCALE / PRINT_W:.2f} "
          f"\\linewidth at scale {SCALE})")


# ---- a distribution: transparency ramp or patches --------------------------------------------
RAMP_Q = np.r_[0.5, np.arange(1.0, 100.0), 99.5]   # quantile grid the ramp is built from
RAMP_ALPHA, RAMP_GAMMA = 0.38, 1.1                 # opacity at the median, fade towards the tails


def ramp_bands(ax, x, Q, qs=RAMP_Q, color=C_PROPOSED, n_bands=40, alpha_max=RAMP_ALPHA,
               gamma=RAMP_GAMMA, zorder=1):
    """Distribution as a transparency ramp: nested percentile ranges, opaque at the median, fading
    towards the tails, no visible edges. One connected surface along x, vector in the PDF.
    The ranges are drawn as rings that do not overlap, each with the opacity that the nested bands
    would add up to there, 1 - (1 - alpha_max / n_bands)**k for k bands: every pixel is blended once, so
    the colour is exact even in a PNG (forty faint layers stacked on each other drift in hue in 8-bit
    blending: lilac turns grey). Band k spans the central range whose half-width in quantile units is
    t_k = (1 - k / n_bands)**(1 / gamma). Q: quantile function, shape (len(qs), len(x))."""
    a = alpha_max / n_bands

    def bound(p):
        return np.array([np.interp(p, qs, Q[:, j]) for j in range(Q.shape[1])])

    t = [(1.0 - k / n_bands) ** (1.0 / gamma) for k in range(1, n_bands + 1)]      # t[-1] = 0: the median
    edges = [(bound(50.0 * (1.0 - tk)), bound(50.0 * (1.0 + tk))) for tk in t]     # (lower, upper) of band k
    for k in range(1, n_bands):                                  # ring k: band k without band k + 1
        (lo_out, hi_out), (lo_in, hi_in) = edges[k - 1], edges[k]
        alpha = 1.0 - (1.0 - a) ** k
        ax.fill_between(x, lo_out, lo_in, color=color, alpha=alpha, lw=0, zorder=zorder)
        ax.fill_between(x, hi_in, hi_out, color=color, alpha=alpha, lw=0, zorder=zorder)


def patch_bands(ax, x, Q, qs=RAMP_Q, color=C_PROPOSED, levels=((25, 75, 0.30),), zorder=1):
    """Distribution as a patch: one flat tint for one percentile range, by default 25-75 %. More ranges
    can be passed as levels, (lower percentile, upper percentile, opacity), but one patch is easier to read
    than overlapping ones. Q as in ramp_bands."""
    for lo_p, hi_p, alpha in levels:
        lo = np.array([np.interp(lo_p, qs, Q[:, j]) for j in range(Q.shape[1])])
        hi = np.array([np.interp(hi_p, qs, Q[:, j]) for j in range(Q.shape[1])])
        ax.fill_between(x, lo, hi, color=color, alpha=alpha, lw=0, zorder=zorder)


PAD_IN = 0.02                                 # pad_inches of save()


def show_if_requested():
    if ARGS.show:
        plt.show()


def viridis_colours(values, lo=0.05, hi=0.85):
    """Colours for an ordered series (N_prev = 1..5, cycles in time order): dark = first."""
    cm = plt.get_cmap("viridis")
    return {v: cm(c) for v, c in zip(values, np.linspace(lo, hi, len(values)))}
```

### The zoom module

`zoom_plot.py` is a Python port of the MATLAB `zoom_plot.m`: it puts a zoomed copy
of a region of an axes into an inset, draws the rectangle of that region on the parent axes, and
joins the two with the two lines that touch both boxes without crossing them (the bridging edges
of the convex hull of the eight corners, so any placement of the inset works). The region is given
in data coordinates and the inset in axes coordinates; the inset is filled with a copy of the
parent's data artists, and the rectangle and lines follow the parent's limits, as the listeners do
in the MATLAB version.

```python
"""
zoom_plot.py
------------
Python port of the MATLAB zoom_plot.m: show a zoomed portion of an axes in a second (inset)
axes, mark the zoomed region with a rectangle on the parent axes, and connect the two with
straight lines.

    from zoom_plot import zoom_plot

    z = zoom_plot(ax, xlim=(150, 200), ylim=(3.50, 3.60),      # region, in DATA coordinates
                  position=(0.36, 0.34, 0.60, 0.56))           # inset, in AXES coordinates
    z.child.set_yticks([3.5, 3.6])                             # the inset axes
    z.rect, z.lines                                            # rectangle, the two connectors

As in the MATLAB function, `position` is [left, bottom, width, height] as a fraction of the
parent axes, and the inset is filled with a copy of what the parent draws in data coordinates
(Line2D, LineCollection, filled areas). Pass copy=False to draw the inset by hand.

Which corners are connected is decided from the relative position of rectangle and inset (the
two lines are the outer tangents of the two boxes, so they never cross either of them); pass
`corners` to force a choice. Rectangle and lines are recomputed when the parent's limits
change, i.e. they stay attached to the data, like the listeners of the MATLAB version.

Only straight connectors are drawn (no "pinned" interactive editing of the MATLAB version:
here the region is given in data coordinates, which is what a paper figure needs).
"""

from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.collections import LineCollection, PolyCollection

try:
    from plot_style import style_ax
except ImportError:                                    # paper scripts / stand-alone use
    try:
        from paper_style import style_ax
    except ImportError:
        def style_ax(ax_or_axes, color="#262626"):
            pass

COLOR = "#262626"
# corner order used everywhere below: 0 = bottom left, 1 = bottom right, 2 = top right, 3 = top left
_CORNERS = ((0, 0), (1, 0), (1, 1), (0, 1))


class ZoomPlot:
    """Handles of one zoom: .parent, .child (inset axes), .rect, .lines (two connectors)."""

    def __init__(self, parent, child, rect, lines, corners):
        self.parent, self.child, self.rect, self.lines = parent, child, rect, lines
        self.corners = corners

    def update(self, *_):
        """Re-place the connectors (called on every limit change of the parent)."""
        _place_lines(self)

    def set_region(self, xlim=None, ylim=None):
        """Move the zoomed region; the inset follows."""
        x0, y0 = self.rect.get_xy()
        x1, y1 = x0 + self.rect.get_width(), y0 + self.rect.get_height()
        xlim = xlim if xlim is not None else (x0, x1)
        ylim = ylim if ylim is not None else (y0, y1)
        self.rect.set_bounds(xlim[0], ylim[0], xlim[1] - xlim[0], ylim[1] - ylim[0])
        self.child.set_xlim(*xlim)
        self.child.set_ylim(*ylim)
        self.update()


def zoom_plot(parent, xlim, ylim, position=(0.55, 0.52, 0.42, 0.44), color=COLOR, lw=1.0,
              ls="-", corners="auto", copy=True, style=True, tick_fs=None, ticks=True,
              zorder=8, connectors=True, **kw):
    """Zoomed inset of `parent` showing [xlim] x [ylim] (data coordinates).

    parent     : Axes to zoom into
    xlim, ylim : the zoomed region, in data coordinates
    position   : [left, bottom, width, height] of the inset, as a fraction of the parent axes
    corners    : "auto" (outer tangents) or ((rect_corner, inset_corner), (rect_corner, inset_corner))
                 with 0 = bottom left, 1 = bottom right, 2 = top right, 3 = top left
    copy       : copy the parent's data artists into the inset
    style      : apply style_ax() to the inset
    tick_fs    : font size of the inset's tick labels (default: 3 pt smaller than the parent's)
    ticks      : False removes the inset's tick labels
    kw         : passed to parent.inset_axes()

    Returns a ZoomPlot with .child, .rect and .lines.
    """
    child = parent.inset_axes(position, zorder=zorder, **kw)
    if copy:
        copy_artists(parent, child)
    child.set_xlim(*xlim)
    child.set_ylim(*ylim)
    if style:
        style_ax([child])
        child.set_axisbelow(True)
    for s in child.spines.values():                    # the inset's frame matches the rectangle
        s.set_edgecolor(color)
        s.set_linewidth(lw)
    if tick_fs is None:
        tick_fs = max(6.0, parent.xaxis.get_ticklabels()[0].get_size() - 3
                      if parent.xaxis.get_ticklabels() else 8.0)
    child.tick_params(labelsize=tick_fs)
    if not ticks:
        child.tick_params(labelbottom=False, labelleft=False)
    child.patch.set_facecolor("white")                 # hide the parent's curves behind the inset
    child.patch.set_alpha(1.0)

    rect = Rectangle((xlim[0], ylim[0]), xlim[1] - xlim[0], ylim[1] - ylim[0], fill=False,
                     edgecolor=color, linewidth=lw, linestyle=ls, zorder=zorder - 1)
    rect.set_transform(parent.transData)
    parent.add_patch(rect)

    lines = []
    if connectors:
        for _ in range(2):
            ln = Line2D([], [], color=color, lw=lw, ls=ls, zorder=zorder - 1, clip_on=False)
            ln.set_transform(parent.transAxes)
            parent.add_line(ln)
            lines.append(ln)

    z = ZoomPlot(parent, child, rect, lines, corners)
    _place_lines(z)
    parent.callbacks.connect("xlim_changed", z.update)
    parent.callbacks.connect("ylim_changed", z.update)
    return z


# ---------------------------------------------------------------------------------------
# copy of the parent's content into the inset
# ---------------------------------------------------------------------------------------
def copy_artists(src, dst):
    """Copy the artists that `src` draws in data coordinates into `dst` (lines, line
    collections, filled areas). Artists in other coordinates (axhline, axvspan, text) and
    legends are skipped, as they are not part of the zoomed data."""
    for a in list(src.get_children()):
        if not getattr(a, "get_visible", lambda: True)():
            continue
        if a.get_transform() is not src.transData:
            continue
        if isinstance(a, Line2D):
            new = Line2D(a.get_xdata(), a.get_ydata())
            new.update_from(a)
            new.set_transform(dst.transData)
            dst.add_line(new)
        elif isinstance(a, LineCollection):
            new = LineCollection(a.get_segments(), cmap=a.cmap, norm=a.norm,
                                 linewidths=a.get_linewidths(), linestyles=a.get_linestyle(),
                                 capstyle=a.get_capstyle(), zorder=a.get_zorder(),
                                 alpha=a.get_alpha())
            if a.get_array() is not None:
                new.set_array(a.get_array())
            else:
                new.set_color(a.get_colors())
            new.set_transform(dst.transData)
            dst.add_collection(new)
        elif isinstance(a, PolyCollection):
            new = PolyCollection([p.vertices for p in a.get_paths()],
                                 facecolors=a.get_facecolor(), edgecolors=a.get_edgecolor(),
                                 linewidths=a.get_linewidths(), alpha=a.get_alpha(),
                                 zorder=a.get_zorder())
            new.set_transform(dst.transData)
            dst.add_collection(new)


# ---------------------------------------------------------------------------------------
# connectors: outer tangents of the two boxes (never cross the rectangle or the inset)
# ---------------------------------------------------------------------------------------
def _box_corners(x0, y0, x1, y1):
    return [(x0 + fx * (x1 - x0), y0 + fy * (y1 - y0)) for fx, fy in _CORNERS]


def _hull(points):
    """Convex hull (monotone chain), points as (x, y, tag); returns the hull in order."""
    pts = sorted(points)
    if len(pts) <= 2:
        return pts

    def half(seq):
        out = []
        for p in seq:
            while len(out) >= 2:
                (ax, ay), (bx, by), (cx, cy) = out[-2][:2], out[-1][:2], p[:2]
                if (bx - ax) * (cy - ay) - (by - ay) * (cx - ax) <= 0:
                    out.pop()
                else:
                    break
            out.append(p)
        return out

    lower, upper = half(pts), half(pts[::-1])
    return lower[:-1] + upper[:-1]


def _auto_corners(rect_pts, child_pts):
    """The two hull edges that join a rectangle corner to an inset corner."""
    tagged = [(x, y, 0, i) for i, (x, y) in enumerate(rect_pts)] + \
             [(x, y, 1, i) for i, (x, y) in enumerate(child_pts)]
    h = _hull(tagged)
    pairs = []
    for a, b in zip(h, h[1:] + h[:1]):
        if a[2] != b[2]:
            pairs.append((a[3], b[3]) if a[2] == 0 else (b[3], a[3]))
    return pairs if len(pairs) == 2 else []


def _place_lines(z):
    if not z.lines:
        return
    parent, child = z.parent, z.child
    inv = parent.transAxes.inverted()
    x0, y0 = z.rect.get_xy()
    x1, y1 = x0 + z.rect.get_width(), y0 + z.rect.get_height()
    rect_pts = [tuple(inv.transform(parent.transData.transform(p)))
                for p in _box_corners(x0, y0, x1, y1)]
    cx0, cy0, cw, ch = child.get_position().bounds                     # figure coordinates
    child_pts = [tuple(inv.transform(parent.figure.transFigure.transform(p)))
                 for p in _box_corners(cx0, cy0, cx0 + cw, cy0 + ch)]
    pairs = _auto_corners(rect_pts, child_pts) if z.corners == "auto" else list(z.corners)
    for ln, pair in zip(z.lines, pairs):
        (ax_, ay_), (bx_, by_) = rect_pts[pair[0]], child_pts[pair[1]]
        ln.set_data([ax_, bx_], [ay_, by_])
        ln.set_visible(True)
    for ln in z.lines[len(pairs):]:
        ln.set_visible(False)
```

## 5. Script layout

* **Computation and plotting are separate.** Heavy computation writes CSV / JSON / NPZ into
  `results/`; figure scripts only read `results/` and draw. Re-drawing a figure then takes seconds.
  In this folder the figure scripts read the small files in `data/` (see `fig_template.py`).
* **One file per type of plot** (signals, hyperparameters, accuracy, examples, ...), one
  function per figure, named after the file it writes: `fig_<topic>_<variant>`.
* **Print the numbers** each figure shows, with the figure name in front.
* **One script draws both layouts.** A figure function takes its sizes from `FIG_W` and
  `height(kind)`, never from inches. `python fig_example.py --layout single` writes
  `images/paper_single/`, the default writes `images/paper/`, so the two paper versions never
  overwrite each other. A figure that is arranged differently in the two (a 2 x 2 grid in one, a
  row in the other) branches on `LAYOUT == "single"` inside its function.

Skeleton:

```python
"""
fig_example.py - paper figures of <topic>.  Reads results/, writes images/paper/.
usage:  python fig_example.py [--show] [--only fig_example_bands]
"""
import numpy as np
from matplotlib.lines import Line2D

from paper_style import *          # style, palette, labels, helpers, ARGS
from zoom_plot import zoom_plot    # inset + rectangle + connectors (recipe 6.4)

def fig_example(name):
    fig, (ax,) = stacked(FIG_W * 0.5, [1.0])
    ...                                  # draw
    finish(fig, [ax])
    save(fig, name)


if want("fig_example"):
    fig_example("fig_example")
show_if_requested()
```

## 6. Recipes

The recipes below run as they are (synthetic data in place of the results files); the pictures
are their output. Recipes 6.1 to 6.5 show `--layout two` first and `--layout single` second;
6.6 to 6.8 are the figures that belong to the single-column layout. Together with the skeleton imports
above they are one script.

**The pictures in this guide are the `_white.png` files** (opaque white background): markdown viewers with a
dark theme show the transparent PNGs with invisible labels. The transparent PNGs are in the same folder,
and the `_white.png` is made only for markdown files, never for a paper.

### 6.1 Signal and residual at one instant

Recipe `fig_example_snapshot`: shaded forecast region on both panels, vertical line at the present,
measured samples with markers in the past, in-panel tags on a background patch.

![snapshot](paper_figure_guide_img/fig_example_snapshot_white.png)
![snapshot, single](paper_figure_guide_img/fig_example_snapshot_single_white.png)

```python
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
```

### 6.2 A metric with its distribution: ramp or patches

Recipe `fig_example_bands` draws the same data twice, so that the two ways of showing a distribution can
be compared. The line is the metric of the whole data set (here the RMSE of the test set versus the
horizon); the shading is the distribution of the same metric over the pieces of the data set (here the
RMSE of each of 250 cycles), so the line runs inside its own shading. The y axis is cut at 8: the upper
tails of the wide distributions are clipped by the frame instead of setting the scale of the whole figure.

*Transparency ramp* (`ramp_bands`, first pair of pictures): 40 nested percentile ranges of one colour,
opaque at the median and fading to the tails with no visible edges; it shows the whole shape of the
distribution. The ranges are drawn as rings that do not overlap, each with the opacity that the nested
bands would add up to at that depth (`1 - (1 - alpha_max / n_bands)^k`), so every pixel is blended
once and the colour is exact even in a PNG: forty faint layers stacked on each other drift in hue
(lilac turns grey) because 8-bit blending rounds every layer.

*Patch* (`patch_bands`, second pair): one flat tint for one percentile range, here 25-75 % (the middle
half of the pieces). The edges can be read as numbers, and the picture holds up better in a grey-scale
print. One patch, not several overlapping ones: nested ranges (for example a light 5-95 % under a
darker 25-75 %) mix with the shading of the other methods and are hard to read.

Both are filled patches (`fill_between`), not an image: the surface is connected along x, stays vector in
the PDF and has no column seams. The three methods are drawn in one panel; where two shadings overlap the
colours mix, which is acceptable for a few methods; with more, give each its own tile (recipe 6.6). Cut
the x axis on the data (`ax.set_xlim(x[0], x[-1])`), otherwise the shading stops before the frame.

![ramp](paper_figure_guide_img/fig_example_bands_ramp_white.png)
![ramp, single](paper_figure_guide_img/fig_example_bands_ramp_single_white.png)

![patches](paper_figure_guide_img/fig_example_bands_patch_white.png)
![patches, single](paper_figure_guide_img/fig_example_bands_patch_single_white.png)

```python
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
```

### 6.3 Two windows of a signal side by side

Recipe `fig_example_split`: two windows of the same signal as two columns of closed tiles.
The column widths are proportional to the window lengths (same seconds per inch), the y axes are
shared along each row (tick labels only on the left), and the gap `wspace = 0.1` separates the
tiles. A broken axis (hidden inner spines and break marks) was tried and dropped: separate tiles
read more clearly.

![split](paper_figure_guide_img/fig_example_split_white.png)
![split, single](paper_figure_guide_img/fig_example_split_single_white.png)

```python
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
```

### 6.4 Curves with a zoom

Recipe `fig_example_convergence`. When curves coincide at full scale, zoom on the converged part
instead of adding a panel: `zoom_plot(ax, xlim=..., ylim=..., position=[l, b, w, h])` makes the
inset, copies the curves into it, and marks the region with a rectangle and two connectors, so the
reader sees which part is magnified (a bare `inset_axes` does not). The curves of an ordered series (here
the number of previous cycles) use `viridis` (dark = first), and one legend above the row
(`legend_above_all`) names them for both panels.

![convergence](paper_figure_guide_img/fig_example_convergence_white.png)
![convergence, single](paper_figure_guide_img/fig_example_convergence_single_white.png)

```python
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
```

### 6.5 Path coloured by a value

Recipe `fig_example_map`: a `LineCollection` coloured by the value, equal aspect, panel height from the
data aspect, and a normal vertical colour bar on the right. The map and the colour bar are placed with
margins in inches, so the colour bar is exactly as tall as the map. The colour scale covers the range of
the data; if a few peaks wash out the rest, cap it (`vmax`) and say so in the caption. For two maps with
the same scale, use one `Normalize` for both and one colour bar. A colour map is only ever drawn with its
colour bar.

![map](paper_figure_guide_img/fig_example_map_white.png)
![map, single](paper_figure_guide_img/fig_example_map_single_white.png)

```python
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
```

### 6.6 A row of tiles at full width

Recipe `fig_example_tiles`, the typical full-width figure of a single-column paper
(rule 15): one tile per model, the same y axis (labels on the first tile only), the distribution of
the metric as a transparency ramp inside each tile, so no two shadings overlap (trap: overlaid
transparent fans turn muddy). The y axis is cut at 8, as in recipe 6.2. The data set is named by an
in-panel tag on a patch of the background colour; the model names are the tile titles. Ticks stay away
from the right limit (0, 400, 800 on a 0-1050 ms axis), otherwise the "1000" of one tile touches the
"0" of the next.

![tiles](paper_figure_guide_img/fig_example_tiles_single_white.png)

```python
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
```

### 6.7 Two figures side by side

Pattern of the half-width pair of a single-column paper (rules 15 and 16): each figure is drawn at
`HALF * FIG_W` (5.28 in with `single`), set side by side with `\hfill` and `subcaption` (section 8).
So that the two frames line up at print size, both get the same height (`height("pair", HALF)`)
and the same build: one legend (title and one row) above the panel and one label line under it
(rule 16). At half width a legend holds two entries per row (`ncol=2`); a third goes into a second
row, in both figures. The picture shows the two saved files as `\hfill` places them.

![pair](paper_figure_guide_img/fig_example_pair_single_white.png)

```python
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
```

### 6.8 Legends

Three ways to place the legend of one panel, and one rule for a row of tiles. `legend_at(ax)` (`"above"`)
centres a frameless legend above the panel: it never covers data and is the default.
`legend_at(ax, "inside")` puts a rounded box in the lower right corner, over the panel: use it only where
the curves leave that corner free. `boxed=True` puts the same rounded box round the legend above. The
corner radius is `LEGEND_ROUND` (0.3 of the legend font size; matplotlib's own box is 0.2). The picture
shows, left to right: inside, above, above and boxed.

![legends: inside, above, above and boxed](paper_figure_guide_img/fig_example_legends_panels_single_white.png)

When several panels share their colours, one legend above everything says it once:
`legend_above_all(fig, axes)`. Its `rise` is the distance above the panels in inches (the default sits just above
the panel titles, 0.06 if there are none). A legend repeated in every panel only adds noise and is not used. The
second picture is the same row with `boxed=True`.

![a row of tiles, one legend above everything](paper_figure_guide_img/fig_example_legends_row_single_white.png)
![the same, boxed](paper_figure_guide_img/fig_example_legends_row_boxed_single_white.png)

```python
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
```

## 7. Text in figures

* **Model and signal names** are the same in every figure and in the text:
  `proposed`, `comparison`, `baseline $y_{\mathrm{base}}$`, `measured $y$`,
  `$u$ (commanded input)`, `cycle $k-1$`. Use the constants `LAB_*` of the style module, and change
  them once per project.
* **Data sets** are `training set` and `test set` (legend title or panel title); no dates, no
  internal folder names.
* **Axis labels**: symbol and unit, `$\tau = t - t_k$ [s]`, `$r$ [a.u.]`, `$\kappa$ [1/m]`,
  `previous cycles $N_{\mathrm{prev}}$`. Words in subscripts go into `\mathrm{}`.
* **LaTeX special characters** in labels must be escaped: `\%`, `\_`, `\&`, `\#`.
* **Titles** only for the columns of a grid or for a map (`ax.set_title(..., fontsize=LEGEND_FS + 1,
  color=C_AX, pad=5)`); no figure titles. The message of the figure goes into the caption.
* **Tags inside a panel** ("past", "forecast") sit on a patch of the local background colour
  (`bbox=dict(boxstyle="square,pad=0.15", fc=..., ec="none", alpha=0.9)`) so no curve runs through
  them.
* **Legends** are placed with `legend_at` and `legend_above_all` (rule 6, recipe 6.8), not with
  `ax.legend()` and matplotlib's defaults.
* **Panel letters** of two figures side by side ((a), (b)) are written by `\subcaption`, not
  drawn into the graphic.

## 8. LaTeX

`\linewidth` is `\columnwidth` in a two-column paper and `\textwidth` in a single-column paper, and
inside a `subfigure` it is the width of that subfigure, so the same line is right everywhere:

```latex
\usepackage{graphicx}
\graphicspath{{../images/paper/}}        % {../images/paper_single/} for --layout single

\begin{figure}[t]
  \centering
  \includegraphics[width=\linewidth]{fig_example_snapshot.pdf}
  \caption{Forecast at one instant of the test set. Top: measured signal, baseline model and
  the forecast of the proposed model. Bottom: residual.}
  \label{fig:snapshot}
\end{figure}
```

A figure that should take less space keeps its own scale (rule 13); include it at the fraction
`save` prints for it, in practice the `s` it was drawn for:

```latex
\includegraphics[width=0.48\linewidth]{fig_example_pair_a.pdf}     % drawn at HALF * FIG_W
```

*Single-column:* two figures side by side (recipe 6.7, rules 15 and 16), each drawn at
`HALF * FIG_W`, with `subcaption`; `[t]` aligns their tops:

```latex
\usepackage{subcaption}

\begin{figure}[t]
  \centering
  \begin{subfigure}[t]{0.48\linewidth}
    \includegraphics[width=\linewidth]{fig_example_pair_a.pdf}
    \caption{RMSE versus horizon.}\label{fig:pair-a}
  \end{subfigure}\hfill
  \begin{subfigure}[t]{0.48\linewidth}
    \includegraphics[width=\linewidth]{fig_example_pair_b.pdf}
    \caption{Loss versus previous cycles.}\label{fig:pair-b}
  \end{subfigure}
  \caption{Both on the test set.}\label{fig:pair}
\end{figure}
```

*Single-column:* a figure next to the text, drawn at the same `s` it is included at:

```latex
\usepackage{wrapfig}

\begin{wrapfigure}{r}{0.48\linewidth}
  \centering
  \includegraphics[width=0.48\linewidth]{fig_example_pair_a.pdf}
  \caption{RMSE versus horizon.}
\end{wrapfigure}
```

* Always include the PDF (vector); the SVG is for editing (e.g. Inkscape), the PNG for previews. The
  `_white.png` is for markdown files and dark viewers only, never for LaTeX.
* Place figures with `[t]`; put `\FloatBarrier` (package `placeins`) before the bibliography so no
  figure floats past it.
* Judge figures at print size: `latex/figure_sheet_two.tex` (elsarticle `5p`) and
  `latex/figure_sheet_single.tex` (single column, 5.5 in) lay **every** figure out at
  `\linewidth`; compile with `pdflatex` (twice, for the references) after re-drawing. For a
  venue, put its style file in the sheet instead of the stand-in (the sheet says where). Keep
  every figure in the sheet, also the ones the paper does not use: it is the place where a
  figure is chosen.

## 9. Checklist and traps

* [ ] Looked at the figure in the compiled preview at print size: no legend over data, no clipped
      labels, tick labels readable, legend order = drawing importance.
* [ ] Each method has the same colour as in every other figure of the paper; data set named.
* [ ] Numbers quoted in the text come from the terminal output of the same run.
* [ ] PDF, SVG and PNG (300 dpi) written to `images/paper/`; figure background transparent, panels
      white. The extra `<name>_white.png` (white background) is for markdown files only.
* [ ] Every zoom has its rectangle and connectors.
* [ ] The layout of the figures is the layout of the paper (`--layout`, folder `images/paper/` or
      `images/paper_single/`), and each figure is included at the width `save` printed for it.
* [ ] Two figures side by side: same height, same legend rows, `subfigure[t]`, judged together
      at print size (rule 16).

Traps met while making the paper figures:

* **`style_ax` turns ticks on for all four sides.** Hide spines or ticks (colour bars, special
  layouts) after calling it.
* **`savefig(transparent=True)` also makes the panels transparent.** For a transparent figure with
  white panels set `fig.patch.set_alpha(0)` and `ax.patch.set_facecolor("white")` before saving
  (done in `save`).
* **Overlaid transparent fans of several colours turn muddy**; put each distribution in its own tile
  with a shared y axis.
* **Tick labels at the edge of side-by-side tiles collide** ("1000" of one tile touches "0" of the
  next); place the ticks away from the right limit (0, 400, 800 on a 0-1050 ms axis).
* **A very flat figure** (`0.2 * FIG_W`): shorten the y label (a rotated label longer than the
  panel sticks out), limit the y ticks (`MaxNLocator(nbins=3)`), put the legend in one row and name
  the data set inside the panel.
* **Shared axes share their tick locators.** Changing the minor ticks of one panel of a `sharex`
  stack changes all of them; to hide ticks on one panel use `tick_params(length=0)`.
* **Axis limits of a window** come from the data inside that window, with a 9 % pad; limits from
  the whole signal flatten the part that is shown.
* **The 5th percentile of an absolute error is close to 0**, so a fan of $|e|$ starts near zero and
  its darkest part (the median) sits well below the RMSE: the shading then does not follow the
  line drawn on top of it. Shade the distribution of the same quantity as the line (the metric per
  cycle / per window), or draw the median of what is shaded.
* **A shading drawn as an image** (`imshow`, `pcolormesh`) is rasterised in the PDF, and
  `pcolormesh` leaves faint vertical seams between its columns; `fill_between` rings
  (`ramp_bands`) look the same, stay vector and are connected along x.
* **Many faint layers stacked on each other change colour.** Agg blends in 8 bits and rounds every
  layer, so forty layers of opacity 0.01 drift towards grey (a lilac ramp turned grey). Give every
  pixel one blend with the final opacity, as `ramp_bands` does.
* **Leave no white margin under a shading**: with the default `xlim` the ramp stops before the
  frame; set the limits to the first and last x of the data.
* **An inset without the rectangle** does not say what it magnifies; use `zoom_plot` and check that
  the rectangle is visible (a very flat region becomes a thin sliver, which is still the honest
  picture).
* **A shrunk figure** (rule 13) must be included at the matching `s\columnwidth`; at
  `\columnwidth` its text prints `1/s` times too large.
* **`usetex` needs LaTeX** (MiKTeX / TeX Live) on the `PATH`; the first run is slow while the font
  cache is built. A label with an unescaped `%` or `_` stops the save with a LaTeX error. Without
  LaTeX the module draws with matplotlib's own maths font (it says so at the start): fine for a
  draft, not for the final figures.
* **Colour maps only with a colour bar**; unexplained colours read as noise. Linear axes by default,
  logarithmic only when the data span decades.
* **Windows console** (cp1252): keep terminal prints ASCII (`->`, `...`) or run `python -X utf8`.
* **Very long paths** (more than 260 characters, e.g. deep OneDrive or temp folders) make `savefig`
  fail with `FileNotFoundError` although the folder exists; write to a shorter path.
* **With `torch` in the same script**, import `numpy` and `pandas` before `torch` (otherwise
  "OMP: Error #15" on Windows / conda).
* **The printed text size is nominal.** `save` prints "saved X in = Y \linewidth": the text prints
  at drawn size x (printed width / saved width), and the saved width is smaller than `FIG_W`
  because tight cropping removes the unused margin of matplotlib's default panel margins (0.125 /
  0.9 of the width). With `two` the recipes save 6.0 of 7.0 in, a scale of 0.58, so 16 / 14 / 12 pt
  print at about 9.3 / 8.1 / 7.0 pt, not at 8 / 7 / 6. With `single` the side margins are 0.05
  (`LAYOUTS`), the saved width is about 10.5 of 11 in, a scale of 0.52, and 18 / 16 / 14 pt print at
  about 9.4 / 8.4 / 7.3 pt. To get other printed sizes change `fonts` (or `side`) in the `LAYOUTS`
  line of the layout; do not scale the included graphic by hand.
* **A figure of a pair that has a legend or a label the other has not** is cropped to a different
  height, and the two frames no longer line up next to each other (rule 16). Give both the same
  elements, or none.

## 10. Single-column papers (NeurIPS, ICLR)

A single-column paper uses the same style (sections 1 to 9) at a different size. What is different:

* **Width and text.** The text width is 5.5 in (check the style file of the year with the
  `\typeout` line of section 2). A full figure is drawn 11 in wide with `--layout single`, fonts
  18 / 16 / 14 pt, and prints with text of about 9 / 8 / 7 pt next to the 10 pt body. 7 pt is the
  smallest text of the paper; if a figure needs more room make it wider or split it, do not shrink
  the fonts (rule 13).
* **One panel is half width, a full figure is a row** (rules 15 and 16). 5.5 in is too wide for one
  curve; a full-width figure is a row of tiles or a long time series.
* **Figures cost pages.** The main text of a NeurIPS paper has a page limit (9 pages in recent
  calls; check the current one) and a figure counts against it like text. Printed heights from the
  table in section 2: a row of tiles 1.3 in, a signal with its residual 2.1 in, a 2 x 2 grid 2.8 in,
  on a text height of 9 in.
* **Colour.** Each method keeps its colour in every figure of the paper (rule 4), and the baseline is
  also dashed and the methods have different markers, so a figure stays readable in a grey-scale print.

How each recipe is used in a single-column paper:

| recipe | in a single-column paper |
|---|---|
| 6.1 signal and residual | full width, as it is |
| 6.2 metric with its distribution | one panel is too wide at full width: use 6.6 (tiles), or draw it at `HALF` (6.7) |
| 6.3 two windows of a signal | full width, as it is (the layout this width is good for) |
| 6.4 curves with a zoom | full width, as it is (a row of two panels) |
| 6.5 path coloured by a value | full width for an elongated object |
| 6.6 a row of tiles | the standard full-width figure |
| 6.7 two figures side by side | the standard one-panel figure |
| 6.8 legends | any style; one shared legend above a row of tiles |

Setting up a new single-column paper:

1. Copy `paper_style.py` and `zoom_plot.py` next to the figure scripts; run every script with
   `--layout single` (or `set PAPER_LAYOUT=single`).
2. Point `\graphicspath` at `images/paper_single/`; include figures at `\linewidth` and
   `s\linewidth` (section 8).
3. Put every figure on one candidates sheet in the venue's class and judge it at print size
   (section 8), before the paper text is written around it.
4. For another class, add a line to `LAYOUTS` with its `\linewidth`, the font sizes and `side`
   (section 4), and an entry to `ASPECT` if its heights should differ.
