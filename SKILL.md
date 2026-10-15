---
name: paper-figures
description: Draw publication-quality matplotlib figures in one consistent house style (LaTeX text, fixed role-based palette, boxed panels, PDF+SVG+PNG output) for two-column papers or single-column papers such as NeurIPS and ICLR. Use when asked to make, restyle, resize or batch plots or figures for a paper, thesis or report, or to set up figure scripts in a new project.
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
   "baseline", "training set", "test set"). Change them to the project's own names once; keep the
   *roles* (proposed / comparison / baseline) and their colours.

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
   `images/paper_single/` (single) as PDF, SVG and PNG, and prints the width to include the figure at.
4. **Open the PNG and look at it.** Check: nothing clipped, no legend over data, tick labels readable,
   labels carry symbol and unit, the right colours for the roles. Fix and re-run. Do not report a
   figure as done without having looked at it.
5. Print every number the figure shows (the template does), so the text quotes the same data.
6. LaTeX: `\includegraphics[width=\linewidth]{fig_<topic>.pdf}` (the PDF, never the PNG). A figure drawn
   at `s * FIG_W` is included at `s\linewidth`. If LaTeX is available, compile
   `latex/figure_sheet_two.tex` or `latex/figure_sheet_single.tex` to judge it at print size.
7. Hand back the script and the data it reads, not only the image.

## 3. API (all in `paper_style.py`; `from paper_style import *`)

```python
fig, axes = stacked(height("snapshot"), [2.0, 1.0])  # panels on one x axis; width=s*FIG_W for a narrower figure
legend_top(ax, ncol=3, title=TAG_TEST)                # frameless legend above the panel, title = data set
ramp_bands(ax, x, Q, color=C_PROPOSED)                    # distribution as a transparency ramp; Q: (len(RAMP_Q), len(x)) quantiles
zoom_plot(ax, xlim=(x0, x1), ylim=(y0, y1), position=(left, bottom, w, h))   # from zoom_plot import zoom_plot: inset + rectangle + connectors
finish(fig, axes)                                     # boxed panels, grid under the data
save(fig, "fig_name")                                 # PDF + SVG + PNG; prints the width to include it at
show_if_requested()                                   # once at the end (--show opens windows)
if want("fig_name"): ...                              # --only fig_a,fig_b draws a subset
# constants: LAYOUT, FIG_W (7.0 / 11.0 in), HALF (0.48), height(kind, s=1.0)
# kinds: curve tiles flat snapshot stack3 split grid pair   (height / width, per layout)
```

Palette, assigned by role and never cycled:

| role | constant | look |
|---|---|---|
| measured data | `C_MEAS` (blue) | solid, lw 2.0 |
| proposed model | `C_PROPOSED` (orange) | solid, lw 2.0, marker `D` |
| comparison model | `C_COMPARE` (aqua) | solid, lw 1.8, marker `o` |
| baseline | `C_BASE` (dark grey) | dashed `LS_BASE`, marker `s` |
| commanded / reference input | `C_INPUT` (yellow) | solid |
| limits, zero lines | `MUTED` | thin |
| ordered series | `viridis_colours(values)` | dark = first |
| magnitude along a path | seaborn `rocket_r` | always with a colour bar |

## 4. Rules (the guide has all twenty: `docs/paper_figure_guide.md`, section 1)

1. Draw at twice the printed width, include at the printed width. Everything is scaled by 0.5.
2. Never write inches in a figure function; use `FIG_W` and `height(kind)`. One script then draws both layouts.
3. Never shrink the fonts to fit. Make the figure wider or split it.
4. Axis labels hold a symbol and a unit (`$y$ [a.u.]`). No figure titles; the message goes in the caption.
5. One frameless legend above the top panel; its title names the data set.
6. Stacked panels share the x axis; only the bottom one has tick labels.
7. Single-column: one panel is half width (`HALF`), a full-width figure is a row of at most three tiles
   or a long time series. Figures side by side have the same height and the same build.
8. Distribution and the line drawn on it are the same quantity.
9. A zoom always comes with the rectangle and connectors (`zoom_plot`), never a bare inset.
10. Colour maps only with a colour bar. Linear axes unless the data span decades.
11. Escape LaTeX specials in labels: `\%`, `\_`, `\&`, `\#`.
12. Transparent figure background, white panels, saved as PDF + SVG + PNG (done by `save`).

## 5. Which recipe for what (`fig_examples.py`; guide section 6)

| need | recipe | note |
|---|---|---|
| signal and residual at one instant | `fig_example_snapshot` | stacked, shaded forecast region |
| metric with its distribution | `fig_example_bands` | transparency ramp; in single-column use tiles or a pair |
| one tile per model, shared y | `fig_example_tiles` | the standard full-width figure of a single-column paper |
| two windows of one signal | `fig_example_split` | tiles with shared rows |
| curves with a zoom, grouped bars | `fig_example_convergence` | 2 x 2 grid |
| path or field coloured by a value | `fig_example_map` | needs seaborn |
| top views of different objects | `fig_example_topviews` | equal tile widths, drawn at 0.6 |
| two single panels side by side | `fig_example_pair` | each 0.48 wide, `subcaption` in LaTeX |

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
| `check_setup.py` | checks Python, packages and LaTeX |
| `tools/` | maintenance of this repository, not needed to draw figures |
