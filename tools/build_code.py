"""
build_code.py - regenerate paper_style.py, zoom_plot.py and fig_examples.py from the guide.

    python tools/build_code.py          # run from the repository root, or from anywhere

The guide (docs/paper_figure_guide.md) is the source of truth: its code blocks ARE the style module,
the zoom module and the recipes. Edit the guide, run this, then run tools/smoke_test.py. Do not edit
the three generated files by hand: the next run overwrites them.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDE = ROOT / "docs" / "paper_figure_guide.md"

EXAMPLES_HEADER = '''"""
fig_examples.py - every recipe of docs/paper_figure_guide.md (section 6) as a runnable script, on
synthetic data. Run it to see what the figures look like, and copy from it for a new figure.

    python fig_examples.py                        # two-column layout    -> images/paper/
    python fig_examples.py --layout single        # single-column layout -> images/paper_single/
    python fig_examples.py --only fig_example_tiles,fig_example_pair
    python fig_examples.py --show                 # interactive windows instead of files

The map recipe needs seaborn (pip install seaborn); the others need only numpy and matplotlib.
The functions are the recipes of the guide, written out here so that they run as they are.
"""
'''


def main():
    md = GUIDE.read_text(encoding="utf-8")
    blocks = re.findall(r"```python\n(.*?)```", md, flags=re.S)

    style = zoom = skeleton = None
    recipes = []
    for b in blocks:
        if "paper_style.py - figure style" in b:
            style = b
        elif b.lstrip().startswith('"""\nzoom_plot.py'):
            zoom = b
        elif "fig_example.py - paper figures" in b:
            skeleton = b
        elif re.search(r"^def fig_example_\w+\(", b, flags=re.M):
            recipes.append(b)
    if not (style and zoom and skeleton and recipes):
        sys.exit("build_code: a code block of the guide was not found (style, zoom, skeleton, recipes)")

    (ROOT / "paper_style.py").write_text(style, encoding="utf-8", newline="\n")
    (ROOT / "zoom_plot.py").write_text(zoom, encoding="utf-8", newline="\n")

    imports = "\n".join(l for l in skeleton.splitlines() if l.startswith(("import ", "from ")))
    names = [n for b in recipes for n in re.findall(r"^def (fig_example_\w+)\(", b, flags=re.M)]
    calls = "\n".join(f'if want("{n}"):\n    {n}("{n}")' for n in names)
    body = "\n\n".join(r.rstrip("\n") + "\n" for r in recipes)
    (ROOT / "fig_examples.py").write_text(
        EXAMPLES_HEADER + imports + "\n\n\n" + body + "\n\n" + calls + "\nshow_if_requested()\n",
        encoding="utf-8", newline="\n")
    print("written: paper_style.py, zoom_plot.py, fig_examples.py")
    print("recipes:", ", ".join(names))


if __name__ == "__main__":
    main()
