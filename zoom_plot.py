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
