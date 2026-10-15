"""Render a standalone collection of suggested color palettes.

Requires NumPy, Matplotlib, and Seaborn; works with the base_env conda environment.
"""

from pathlib import Path
import csv

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex
from matplotlib.patches import Rectangle
import numpy as np
import seaborn as sns


ROOT = Path(__file__).resolve().parent
PALETTES = [
    {
        "name": "Coastal pastels",
        "suggestion": "Suggested for presentations, categorical charts, and report figures.",
        "colors": [
            ("Lilac", "#AE78CC"),
            ("Apricot", "#E5B07A"),
            ("Turquoise", "#00ADC4"),
            ("Seafoam", "#79C9B1"),
            ("Deep blue", "#1D4E89"),
        ],
    },
    {
        "name": "Coral, violet & mint",
        "suggestion": "Suggested for comparing three groups or highlighting three key ideas.",
        "colors": [("Coral", "#EF767A"), ("Violet", "#7667CC"), ("Mint", "#49BEAA")],
    },
    {
        "name": "Vivid accents",
        "suggestion": "Suggested for bold diagrams, highlights, and small sets of categories.",
        "colors": [
            ("Royal blue", "#1461F0"),
            ("Salmon", "#ED6A5A"),
            ("Orchid", "#9D4EDD"),
            ("Teal", "#248277"),
        ],
    },
    {
        "name": "Earth & sky",
        "suggestion": "Suggested for grouped charts with related blue and green tones.",
        "colors": [
            ("Burnt orange", "#D95319"),
            ("Sky blue", "#4D9CD1"),
            ("Ocean blue", "#005084"),
            ("Soft green", "#92BD59"),
            ("Leaf green", "#5F8A26"),
            ("Plum", "#8050A1"),
        ],
    },
    {
        "name": "MATLAB",
        "suggestion": "Classic default palette, before R2025a. All seven colors in their original order.",
        "source": "https://www.mathworks.com/help/matlab/ref/colororder.html",
        "colors": [
            ("Blue", "#0072BD"),
            ("Orange", "#D95319"),
            ("Golden yellow", "#EDB120"),
            ("Purple", "#7E2F8E"),
            ("Green", "#77AC30"),
            ("Light blue", "#4DBEEE"),
            ("Dark red", "#A2142F"),
        ],
    },
    {
        "name": "MATLAB - gem",
        "suggestion": "Default light-theme palette since R2025a. All seven colors in their original order.",
        "source": "https://www.mathworks.com/help/matlab/ref/colororder.html",
        "colors": [
            ("Blue", "#1171BE"),
            ("Orange", "#DD5400"),
            ("Golden yellow", "#EDB120"),
            ("Purple", "#8516D1"),
            ("Green", "#3BAA32"),
            ("Light blue", "#2FBEEF"),
            ("Magenta", "#D1048B"),
        ],
    },
]
COLOR_NAMES = ["Blue", "Orange", "Green", "Red", "Purple", "Brown", "Pink", "Gray", "Olive", "Cyan"]
PALETTES.append({
    "name": "Matplotlib - tab10",
    "suggestion": "Default ten-color cycle. Suggested for categorical charts and multiple line series.",
    "source": "https://matplotlib.org/stable/gallery/color/color_cycle_default.html",
    "colors": list(zip(COLOR_NAMES, (to_hex(color).upper() for color in matplotlib.colormaps["tab10"].colors))),
})
for palette_name, suggestion in [
    ("muted", "Moderate saturation. Suggested for categorical comparisons with a softer appearance."),
]:
    names = COLOR_NAMES.copy()
    PALETTES.append({
        "name": f"Seaborn - {palette_name}",
        "suggestion": suggestion,
        "source": "https://seaborn.pydata.org/tutorial/color_palettes.html",
        "colors": list(zip(names, (color.upper() for color in sns.color_palette(palette_name, n_colors=10).as_hex()))),
    })
OPACITIES = (0.3, 0.15)
DARKENING = (0.2, 0.1)
STRIP_HEIGHT = 0.14


def rgb8(hex_color):
    return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))


def rgb(hex_color):
    return np.asarray(rgb8(hex_color)) / 255.0


def darker_hex(hex_color, amount):
    channels = np.floor(np.asarray(rgb8(hex_color)) * (1 - amount) + 0.5).astype(int)
    return "#" + "".join(f"{channel:02X}" for channel in channels)


def draw_palette():
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none"})
    row_height = 2.37 + STRIP_HEIGHT * len(DARKENING)
    height = 3.53 + row_height * len(PALETTES)
    fig = plt.figure(figsize=(16, height), dpi=150, facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, 16), ylim=(0, height))
    ax.axis("off")
    ink, muted = "#262626", "#686868"
    ax.text(0.65, height - 0.55, "Suggested color palettes", fontsize=27, weight="bold", color=ink, va="top")
    ax.text(0.65, height - 1.08, f"{len(PALETTES)} palettes for charts, presentations, and reports.",
            fontsize=11, color=muted, va="top")
    ax.text(0.65, height - 1.40, "Each color: 20% darker / 10% darker / base / 30% and 15% opacity.",
            fontsize=10, color=muted, va="top")
    y = height - 2.00
    for palette in PALETTES:
        ax.text(0.65, y, palette["name"], fontsize=15, weight="bold", color=ink, va="top")
        ax.text(0.65, y - 0.31, palette["suggestion"], fontsize=9, color=muted, va="top")
        swatch_top = y - 0.63
        count = len(palette["colors"])
        width = (14.7 - (count - 1) * 0.18) / count
        for i, (name, hex_color) in enumerate(palette["colors"]):
            x = 0.65 + i * (width + 0.18)
            color = rgb(hex_color)
            base_top = swatch_top
            for amount in DARKENING:
                shade_hex = darker_hex(hex_color, amount)
                base_top -= STRIP_HEIGHT
                ax.add_patch(Rectangle((x, base_top), width, STRIP_HEIGHT,
                                       facecolor=rgb(shade_hex), edgecolor="none"))
            ax.add_patch(Rectangle((x, base_top - 0.64), width, 0.64, facecolor=color, edgecolor="none"))
            strip_bottom = base_top - 0.64
            for alpha in OPACITIES:
                strip_bottom -= STRIP_HEIGHT
                ax.add_patch(Rectangle((x, strip_bottom), width, STRIP_HEIGHT,
                                       facecolor=color * alpha + (1 - alpha), edgecolor="none"))
            ax.text(x, strip_bottom - 0.11, hex_color, fontsize=10 if count >= 10 else 12,
                    weight="bold", color=ink, va="top")
            ax.text(x, strip_bottom - 0.39, name, fontsize=9, color=muted, va="top")
        y -= row_height
    ax.plot([0.65, 15.35], [1.22, 1.22], color="#dddddd", linewidth=0.7)
    ax.text(0.65, 1.00, "Two small strips above each base color: 20% darker, then 10% darker.",
            fontsize=10, color=muted, va="top")
    ax.text(0.65, 0.62, "Below each base color: 30% and 15% opacity on white. Darkening mixes the base color with black.",
            fontsize=10, color=muted, va="top")
    output = ROOT / "images" / "paper_color_palette"
    output.parent.mkdir(exist_ok=True)
    fig.savefig(output.with_suffix(".png"), dpi=150, facecolor="white")
    fig.savefig(output.with_suffix(".svg"), facecolor="white")
    plt.close(fig)
    return output


def write_tables():
    columns = ["palette", "suggested_use", "position", "color_name", "hex", "red", "green", "blue", "r", "g", "b",
               "darker_10_hex", "darker_10_rgb", "darker_20_hex", "darker_20_rgb", "source"]
    with (ROOT / "paper_color_palette.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for palette in PALETTES:
            for position, (name, hex_color) in enumerate(palette["colors"], 1):
                writer.writerow(dict(
                    palette=palette["name"], suggested_use=palette["suggestion"], position=position,
                    color_name=name, hex=hex_color, source=palette.get("source", ""),
                    **dict(zip(("red", "green", "blue"), rgb8(hex_color))),
                    **dict(zip(("r", "g", "b"), (format(c, ".12g") for c in rgb(hex_color)))),
                    darker_10_hex=darker_hex(hex_color, 0.1),
                    darker_10_rgb=" ".join(map(str, rgb8(darker_hex(hex_color, 0.1)))),
                    darker_20_hex=darker_hex(hex_color, 0.2),
                    darker_20_rgb=" ".join(map(str, rgb8(darker_hex(hex_color, 0.2)))),
                ))
    report = [
        "# Suggested color palettes", "",
        f"{len(PALETTES)} palettes for charts, presentations, and reports.", "",
        "[Open the palette image (SVG)](images/paper_color_palette.svg) | [PNG version](images/paper_color_palette.png)", "",
        "[![Suggested color palettes](images/paper_color_palette.png)](images/paper_color_palette.svg)", "",
        "Two small strips above each base color show 20% darker at the top, then 10% darker.",
        "The dark strips match the size of the light strips below. Their HEX codes are listed in the tables.",
        "Darkening mixes the base color with black: `darker = base * (1 - amount)`, rounded to 8-bit RGB.",
        "Below each base color, the two strips show 30% and 15% opacity on white.",
        "Use solid colors for lines and markers, and lighter fills for bands or shaded areas.", "",
    ]
    for palette in PALETTES:
        report.extend([
            f"## {palette['name']}", "", palette["suggestion"], "",
            "| Order | Color | Base HEX | 10% darker | 20% darker | Base RGB (0-255) | Base RGB (0-1) |",
            "|---|---|---|---|---|---|---|",
        ])
        for position, (name, hex_color) in enumerate(palette["colors"], 1):
            report.append(f"| {position} | {name} | `{hex_color}` | `{darker_hex(hex_color, 0.1)}` | "
                          f"`{darker_hex(hex_color, 0.2)}` | {' '.join(map(str, rgb8(hex_color)))} | "
                          f"{' '.join(f'{c:.6f}' for c in rgb(hex_color))} |")
        if "source" in palette:
            report.extend(["", f"[Palette documentation]({palette['source']})."])
        report.append("")
    (ROOT / "paper_color_palette.md").write_text("\n".join(report), encoding="utf-8")


if __name__ == "__main__":
    output = draw_palette()
    write_tables()
    print(f"Updated {output.with_suffix('.png')}")
    print(f"Updated {output.with_suffix('.svg')}")
    print(f"Updated CSV and Markdown tables: {len(PALETTES)} palettes, "
          f"{sum(len(palette['colors']) for palette in PALETTES)} colors")
