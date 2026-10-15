"""
check_setup.py - checks that this machine can run the figure scripts.

    python check_setup.py

Prints what is installed and, for what is missing, what to do about it. Needs no other file.
"""
import importlib
import shutil
import sys
import tempfile
from pathlib import Path

problems = []

print(f"Python {sys.version.split()[0]}")
if sys.version_info < (3, 9):
    problems.append("Python 3.9 or newer is needed")

for module, required, note in (("numpy", True, ""), ("matplotlib", True, ""),
                               ("seaborn", False, " (only the map recipe of fig_examples.py)")):
    try:
        m = importlib.import_module(module)
        print(f"  ok       {module} {getattr(m, '__version__', '')}")
    except ImportError:
        print(f"  {'MISSING ' if required else 'missing '} {module}{note}: pip install {module}")
        if required:
            problems.append(f"pip install {module}")

print("LaTeX (draws the text of the figures; without it the scripts still run, with a different font)")
found = {tool: shutil.which(tool) for tool in ("latex", "dvipng")}
for tool, path in found.items():
    print(f"  {'ok      ' if path else 'MISSING '} {tool}" + (f"  {path}" if path else ""))

if all(found.values()):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.rc("text", usetex=True)
        plt.rcParams["text.latex.preamble"] = r"\usepackage{amsmath}\usepackage{amssymb}\usepackage{bm}"
        fig = plt.figure(figsize=(2, 1))
        fig.text(0.5, 0.5, r"$y_{\mathrm{base}}$ [a.u.] $\bm{x}$")
        with tempfile.TemporaryDirectory() as tmp:
            fig.savefig(Path(tmp) / "check.png")
            fig.savefig(Path(tmp) / "check.pdf")
        print("  ok       a test figure with LaTeX text was drawn")
    except Exception as exc:                                   # noqa: BLE001 - report whatever LaTeX says
        first = str(exc).strip().splitlines()[0] if str(exc).strip() else type(exc).__name__
        print(f"  FAILED   LaTeX is installed but a test figure failed: {first}")
        problems.append("LaTeX needs the packages amsmath, amssymb and bm (MiKTeX installs them on "
                        "request: allow it; TeX Live: tlmgr install amsmath bm)")
else:
    print("  -> install MiKTeX (Windows) or TeX Live (Linux, macOS) and make sure `latex` and `dvipng` "
          "are on the PATH.\n"
          "     Until then the figures are drawn with matplotlib's own font: fine for drafts, "
          "not for the paper.")

print()
if problems:
    print("To do:")
    for p in problems:
        print(f"  - {p}")
else:
    print("Everything needed is there. Next:  python fig_examples.py")
