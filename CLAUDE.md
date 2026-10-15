# CLAUDE.md

Instructions for working **on this repository**. To *use* the kit in another project, read `SKILL.md`.

## What this is

A matplotlib + LaTeX figure style for papers, for two-column and single-column documents
(`--layout two|single`), with runnable recipes, a template, LaTeX test sheets and a long guide.

## Source of truth: the guide

`docs/paper_figure_guide.md` contains the code. These three files are **generated from its code
blocks**; do not edit them by hand, the next build overwrites them:

| generated file | from the code block that contains |
|---|---|
| `paper_style.py` | `paper_style.py - figure style` |
| `zoom_plot.py` | a block that starts with `"""` and `zoom_plot.py` |
| `fig_examples.py` | every block with `def fig_example_...(` (the recipes), plus the imports of the block that contains `fig_example.py - paper figures` |

`tools/build_code.py` finds the blocks by those marker strings. Do not rename or reword the markers.

Everything else is edited directly: `fig_template.py`, `check_setup.py`, `README.md`, `SKILL.md`,
`latex/*.tex`, `data/`, `tools/`, `palettes/` (hand-maintained examples; `python
palettes/generate_paper_color_palette.py` regenerates its markdown, CSV and images).

## Commands

```
python tools/build_code.py          # regenerate the three files from the guide
python tools/smoke_test.py          # run everything in a temp folder, no LaTeX needed
python tools/smoke_test.py --tex    # the same with LaTeX text (needs latex and dvipng)
python check_setup.py               # what this machine has
cd latex && pdflatex figure_sheet_single && pdflatex figure_sheet_single   # a test sheet (after drawing the figures)
```

After any change to code in the guide: build, run the smoke test, and **look at the figures** (run
`fig_examples.py` for both layouts and open the PNGs in `images/`; the smoke test only checks that
files are written and nothing crashes). The pictures in `docs/paper_figure_guide_img/` are the output of
`fig_examples.py`. The guide and the README show the `_white.png` files (opaque white background, made
for markdown files because transparent PNGs have invisible labels on a dark theme): `--layout two` as
`fig_example_<name>_white.png`, `--layout single` as `fig_example_<name>_single_white.png`;
`fig_example_pair_single_white.png` is `pair_a_white` and `pair_b_white` side by side with a 4 % gap, and `fig_example_legends_panels_single_white.png` is `legends_inside`, `legends_above`
and `legends_above_boxed` side by side (bottom-aligned). The
transparent PNGs stay in the folder next to them (do not delete them). Regenerate by hand when a recipe
changes.

## Conventions

- Figure functions take sizes from `FIG_W`, `HALF` and `height(kind)`, never from inches, so one script
  draws both layouts. A recipe that must differ per layout branches on `LAYOUT == "single"`.
- Backslashes in Python strings: write `\\linewidth` in a normal string or use a raw string. A single
  `\l` is a `SyntaxWarning` (a `SyntaxError` in a future Python); the smoke test runs with that
  warning turned into an error.
- Dependencies stay `numpy` and `matplotlib` (seaborn only for the map recipe). Do not add others.
- Generated output goes to `images/`, which is git-ignored. Do not commit figures except the pictures
  in `docs/`.
- Keep the guide's numbers consistent with the code: the size table (section 2) with `ASPECT`, the
  layout table with `LAYOUTS`, the print-size note (section 9) with what `save` prints.
- The labels in `paper_style.py` (`LAB_*`, `TAG_*`) and all example data are generic placeholders. Keep
  them generic here; a project changes them in its own copy of `paper_style.py`.

## Status

Tested on Windows 11, Python 3.13, matplotlib 3.11, MiKTeX; the LaTeX sheets compile with
`pdflatex`. Not tested on Linux or macOS, with other matplotlib versions, or in CI.
