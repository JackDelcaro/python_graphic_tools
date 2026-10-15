"""
smoke_test.py - run the kit end to end in a temporary folder and report what fails.

    python tools/smoke_test.py             # without LaTeX text: fast, runs anywhere
    python tools/smoke_test.py --tex       # with LaTeX text (needs LaTeX; slower)

For both layouts it runs fig_examples.py and fig_template.py in a throw-away copy of the kit, so the
repository stays clean, and checks that every recipe wrote its PDF, SVG and PNG and that no script
printed a traceback or a SyntaxWarning. The map recipe is skipped when seaborn is not installed.
Exit code 0 = all good.
"""
import argparse
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ("paper_style.py", "zoom_plot.py", "fig_examples.py", "fig_template.py")
FOLDERS = {"two": "paper", "single": "paper_single"}


def run(work, env, *args):
    r = subprocess.run([sys.executable, "-X", "utf8", "-W", "error::SyntaxWarning", *args],
                       cwd=work, env=env, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tex", action="store_true", help="draw the text with LaTeX (default: without)")
    use_tex = ap.parse_args().tex

    names = re.findall(r"^def (fig_example_\w+)\(", (ROOT / "fig_examples.py").read_text(encoding="utf-8"),
                       flags=re.M)
    # a recipe may write several files (the pair writes <name>_a and <name>_b)
    wrote = {"fig_example_pair": ["fig_example_pair_a", "fig_example_pair_b"],
             "fig_example_bands": ["fig_example_bands_ramp", "fig_example_bands_patch"],
             "fig_example_legends": [f"fig_example_legends_{s}" for s in
                                     ("inside", "above", "above_boxed", "row", "row_boxed")]}
    has_seaborn = importlib.util.find_spec("seaborn") is not None
    if not has_seaborn:
        print("seaborn is not installed: skipping fig_example_map")
        names = [n for n in names if n != "fig_example_map"]

    env = dict(os.environ, PAPER_USETEX="1" if use_tex else "0")
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for f in FILES:
            shutil.copy(ROOT / f, work / f)
        shutil.copytree(ROOT / "data", work / "data")

        for layout, folder in FOLDERS.items():
            out = work / "images" / folder
            code, text = run(work, env, "fig_examples.py", "--layout", layout, "--only", ",".join(names))
            status = "ok" if code == 0 and "Traceback" not in text else "FAILED"
            print(f"[{layout}] fig_examples.py: {status}")
            if status == "FAILED":
                failures.append(f"fig_examples.py --layout {layout}:\n{text[-1500:]}")
            for n in names:
                for stem in wrote.get(n, [n]):
                    for fname in (f"{stem}.pdf", f"{stem}.svg", f"{stem}.png", f"{stem}_white.png"):
                        if not (out / fname).exists():
                            failures.append(f"[{layout}] missing {folder}/{fname}")

            code, text = run(work, env, "fig_template.py", "--layout", layout)
            status = "ok" if code == 0 and (out / "fig_template.pdf").exists() else "FAILED"
            print(f"[{layout}] fig_template.py: {status}")
            if status == "FAILED":
                failures.append(f"fig_template.py --layout {layout}:\n{text[-1500:]}")

    if failures:
        print("\nFAILED:")
        for f in failures:
            print(" -", f)
        sys.exit(1)
    print("\nall good")


if __name__ == "__main__":
    main()
