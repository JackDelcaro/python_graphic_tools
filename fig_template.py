"""
fig_template.py - copy this file to start a new figure: fig_<topic>.py

    python fig_template.py                   # layout of a two-column paper    -> images/paper/
    python fig_template.py --layout single   # layout of a single-column paper -> images/paper_single/

It reads data/example_horizon.csv (RMSE of three models against the forecast horizon), draws one
panel and prints the numbers the figure shows. Replace the file, the columns and the labels; keep
the structure (docs/paper_figure_guide.md, section 5): load, draw, finish, save, print.
"""
import csv
from pathlib import Path

import numpy as np

from paper_style import *      # style, palette, labels, helpers, ARGS, FIG_W, HALF, height(), ...

DATA = Path(__file__).resolve().parent / "data"


def load(filename):
    """The columns of a CSV file with a header line, as {column name: numpy array}."""
    with open(DATA / filename, newline="") as f:
        rows = list(csv.DictReader(f))
    return {k: np.array([float(r[k]) for r in rows]) for k in rows[0]}


def fig_template(name):
    d = load("example_horizon.csv")
    h = d["horizon_ms"]

    # One panel is a full column of a two-column paper and HALF the text width of a single-column
    # paper (guide, rule 18). height() gives the height for the layout; never write inches here.
    s, kind = (1.0, "curve") if LAYOUT == "two" else (HALF, "pair")
    fig, (ax,) = stacked(height(kind, s), [1.0], width=s * FIG_W)

    # One colour per method, the same in every figure of the paper (guide, rule 4): C_COMPARE and C_PROPOSED.
    ax.plot(h, d["rmse_comparison"], color=C_COMPARE, marker="o", ms=4.5, lw=1.8, mec="white", mew=0.6,
            zorder=5, label=LAB_COMPARE)
    ax.plot(h, d["rmse_proposed"], color=C_PROPOSED, marker="D", ms=4.5, lw=1.8, mec="white", mew=0.6,
            zorder=6, label=LAB_PROPOSED)

    ax.set_xlim(h[0], h[-1])                                 # cut on the data: no white margin
    ax.set_ylim(0, 6)
    ax.set_xlabel(r"forecast horizon $h$ [ms]")              # symbol and unit; no figure title
    ax.set_ylabel(r"RMSE [a.u.]")
    legend_at(ax, ncol=2, title=TAG_TEST)                    # above the panel, centred (guide, rule 6); names the data set
    finish(fig, [ax])
    save(fig, name)                                          # PDF + SVG + PNG (+ _white.png for markdown); prints the width

    # Every number the figure shows is printed, so the text and the caption quote the same data.
    for label, key in ((LAB_COMPARE, "rmse_comparison"), (LAB_PROPOSED, "rmse_proposed")):
        print(f"  {name}: {label}: RMSE {d[key][0]:.2f} a.u. at h = {h[0]:.0f} ms, "
              f"{d[key][-1]:.2f} a.u. at h = {h[-1]:.0f} ms")


if want("fig_template"):
    fig_template("fig_template")
show_if_requested()
