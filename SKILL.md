---
name: paper-figures
description: Draw publication-quality matplotlib figures in one consistent house style (LaTeX text, one colour per method kept across the whole paper, boxed panels, PDF+SVG+PNG output) for two-column papers or single-column papers such as NeurIPS and ICLR. Use when asked to make, restyle, resize or batch plots or figures for a paper, thesis or report, or to set up figure scripts in a new project.
---

# paper-figures

One style module (`paper_style.py`) and a set of recipes that draw every figure of a paper at the
right size for its LaTeX class, so that all figures look like one set. This file is the entry point;
the folder it sits in is the skill directory, and every path below is relative to it.

Use it for matplotlib figures that go into a LaTeX document. Do not use it for interactive or web
charts (plotly, dashboards) or for slides.

## 0. Decide first (ask the user if it is not clear)

1. **Layout of the paper.** `two` = one column of a two-column paper (`\columnwidth` 3.5 in, e.g.
   elsarticle 5p) or `single` = the text width of a single-column paper (`\textwidth` 5.5 in, NeurIPS,
   ICLR). A figure drawn for one is the wrong size in the other. Any other class: add one line to
   `LAYOUTS` in `paper_style.py` (its `\linewidth` in inches, font sizes, `side` margin).
2. **Labels.** `LAB_*` and `TAG_*` in `paper_style.py` hold generic names ("proposed", "comparison",
   "baseline", "training set", "test set"). Change them to the project's own names once, and give each
   method one colour for the whole paper (guide, section 3).

## 1. Set up in a project

- Copy `paper_style.py` and `zoom_plot.py` into the folder of the project's figure scripts. The scripts
  import them from there; never import from the skill folder, and do not edit the copies except
  `LAYOUTS` and the label constants.
- Needs `numpy` and `matplotlib` (seaborn only for the map recipe). LaTeX (`latex`, `dvipng`) draws the
  text; without it the module falls back to matplotlib's own maths font and says so. `python
  check_setup.py` reports what is missing.
- Start a figure from `fig_template.py`; look in `fig_examples.py` for a recipe that matches (section 5).

## 2. Procedure for a new figure

1. Copy `fig_template.py` to `fig_<topic>.py` in the project. Read the data from a file; put small data
   files in `data/`.
2. Draw with the API of section 3. Take sizes from `FIG_W` and `height(kind)`, never from inches.
3. Run `python fig_<topic>.py --layout <two|single>`. It writes `images/paper/` (two) or
   `images/paper_single/` (single) as PDF, SVG and PNG, and prints the width to include the figure at. It also
   writes `<name>_white.png` (opaque white background): only for markdown files and dark viewers, never in LaTeX.
4. **Open the PNG and look at it.** Check: nothing clipped, no legend over data, tick labels readable,
   labels carry symbol and unit, each method in its colour of the paper's table. Fix and re-run. Do not report a
   figure as done without having looked at it.
5. Print every number the figure shows (the template does), so the text quotes the same data.
6. LaTeX: `\includegraphics[width=\linewidth]{fig_<topic>.pdf}` (the PDF, never the PNG). A figure drawn
   at `s * FIG_W` is included at `s\linewidth`. If LaTeX is available, compile
   `latex/figure_sheet_two.tex` or `latex/figure_sheet_single.tex` to judge it at print size.
7. Hand back the script and the data it reads, not only the image.

## 3. API (all in `paper_style.py`; `from paper_style import *`)

```python
fig, axes = stacked(height("snapshot"), [2.0, 1.0])  # panels on one x axis; width=s*FIG_W for a narrower figure
legend_at(ax, ncol=3, title=TAG_TEST)                 # legend above the panel, centred, frameless; "inside" = rounded box; boxed=True
legend_above_all(fig, axes)                           # panels sharing colours: ONE legend above everything
ramp_bands(ax, x, Q, color=c)                         # distribution as a transparency ramp; Q: (len(RAMP_Q), len(x)) quantiles
patch_bands(ax, x, Q, color=c)                        # or as a patch: 25-75 % by default
zoom_plot(ax, xlim=(x0, x1), ylim=(y0, y1), position=(left, bottom, w, h))   # from zoom_plot import zoom_plot: inset + rectangle + connectors
finish(fig, axes)                                     # boxed panels, grid under the data
save(fig, "fig_name")                                 # PDF + SVG + PNG (+ _white.png for markdown); prints the width
show_if_requested()                                   # once at the end (--show opens windows)
if want("fig_name"): ...                              # --only fig_a,fig_b draws a subset
# constants: LAYOUT, FIG_W (7.0 / 11.0 in), HALF (0.48), height(kind, s=1.0)
# kinds: curve tiles flat snapshot stack3 split grid pair   (height / width, per layout)
```

Colours: **not prescribed.** The one rule: each method or data type keeps one colour in every figure of the
paper. The colours themselves are the user's choice (example palettes in `palettes/`, many more on
coolors.co): choose them once, keep them in one table, never let matplotlib cycle colours from figure to
figure. One light preference: measured data in blue. The examples use lilac `#AE78CC` and blue `#1D4E89`
plus greys (`paper_style.py`); a project replaces the assignment with its own, once:

| what | constant | look |
|---|---|---|
| measured data | `C_MEAS` (blue, the light preference) | solid, lw 2.0 |
| proposed method | `C_PROPOSED` (lilac) | solid, lw 2.0, marker `D` |
| comparison method | `C_COMPARE` (blue) | solid, lw 1.8, marker `o` |
| baseline | `C_BASE` (dark grey) | dashed `LS_BASE`, marker `s` |
| limits, zero lines | `MUTED` | thin |
| ordered series | `viridis_colours(values)` | dark = first |
| magnitude along a path | seaborn `rocket_r` | always with a colour bar |

## 4. Rules (the guide has all sixteen: `docs/paper_figure_guide.md`, section 1)

1. Draw at twice the printed width, include at the printed width. Everything is scaled by 0.5.
2. Never write inches in a figure function; use `FIG_W` and `height(kind)`. One script then draws both layouts.
3. Never shrink the fonts to fit. Make the figure wider or split it.
4. Axis labels hold a symbol and a unit (`$y$ [a.u.]`). No figure titles; the message goes in the caption.
5. One legend per figure at a house position: `legend_at` (above the panel, frameless, by default;
   `"inside"` in a rounded box only where a corner is free; `boxed=True` boxes the one above). Panels that
   share their colours get one legend above everything (`legend_above_all`), never one per panel. Its
   title names the data set.
6. Stacked panels share the x axis; only the bottom one has tick labels.
7. Single-column: one panel is half width (`HALF`), a full-width figure is a row of tiles
   or a long time series. Figures side by side have the same height and the same build.
8. A distribution is drawn as a transparency ramp (`ramp_bands`) or as a patch (`patch_bands`, one range,
   25-75 % by default); the shading and the line drawn on it are the same quantity.
9. A zoom always comes with the rectangle and connectors (`zoom_plot`), never a bare inset.
10. Colour maps only with a colour bar. Linear axes unless the data span decades.
11. Escape LaTeX specials in labels: `\%`, `\_`, `\&`, `\#`.
12. Transparent figure background, white panels, saved as PDF + SVG + PNG (done by `save`), plus
    `<name>_white.png` with a white background for markdown files only.
13. One colour per method or data type, the same in every figure of the paper (guide, section 3).

## 5. Which recipe for what (`fig_examples.py`; guide section 6)

| need | recipe | note |
|---|---|---|
| signal and residual at one instant | `fig_example_snapshot` | stacked, shaded forecast region |
| metric with its distribution | `fig_example_bands` | drawn twice: transparency ramp and patches; in single-column use tiles or a pair |
| one tile per model, shared y | `fig_example_tiles` | the standard full-width figure of a single-column paper |
| two windows of one signal | `fig_example_split` | tiles with shared rows |
| curves with a zoom | `fig_example_convergence` | a row of two panels with an inset |
| path or field coloured by a value | `fig_example_map` | vertical colour bar on the right; needs seaborn |
| two single panels side by side | `fig_example_pair` | each 0.48 wide, `subcaption` in LaTeX |
| legend styles | `fig_example_legends` | inside / above / above boxed, and a row with one shared legend |

## 6. Pitfalls

- The printed text size is nominal: tight cropping makes the saved figure a little narrower than
  `FIG_W`, so text prints a little larger. `save` prints the saved width; guide section 9.
- Windows: run with `python -X utf8`; paths over 260 characters make `savefig` fail.
- A label with an unescaped `%` or `_` stops the save with a LaTeX error.
- Without LaTeX the module still runs (with a notice); the final figures need LaTeX.

## 7. Files in this skill

| file | use |
|---|---|
| `paper_style.py`, `zoom_plot.py` | the style and the zoom inset: copy into the project |
| `fig_template.py` | the shortest complete figure script: copy and edit |
| `fig_examples.py` | all recipes on synthetic data: read for a pattern |
| `docs/paper_figure_guide.md` | the full guide (about 1300 lines): sections 1 to 3 first, the rest on demand |
| `latex/figure_sheet_*.tex` | test sheets: every figure at print size |
| `palettes/` | example colour palettes (examples, not requirements): `paper_color_palette.md` with a picture, codes and darker / lighter variants |
| `check_setup.py` | checks Python, packages and LaTeX |
| `tools/` | maintenance of this repository, not needed to draw figures |
