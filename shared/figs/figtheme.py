"""Theme roles for the matplotlib figures -- the Python twin of the
`Theme roles` block in shared/figs/preamble.tex.

Like the TikZ figures, every chart is generated twice: a dark variant for the
deck as shown on screen (figs/out/) and a light one for the light viewer theme
and the PDF (figs/out/light/). A generator therefore looks like

    from figtheme import themes

    def main():
        for t in themes():
            chart(t.out("s49_latency.svg"), ...)

and reads its colours off `t` instead of from module-level constants.
Charts that are shown in turn (variants of one chart) are written with
save_aligned() rather than savefig(), so they line up on the slides.

build_figs.py puts shared/figs on PYTHONPATH, so the plain import above works
from any deck's figs/scripts/ directory.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# The series colours (blu, orange, brown, green, cyan) carry meaning across
# both variants, so the light ones are the same hues darkened until they read
# on white -- not a different palette.
PALETTES = {
    "dark": dict(fg="#F2F4F7", muted="#9FB0C3", grid="#2A3340",
                 blu="#7FB0E0", orange="#F39200", brown="#C9937A",
                 green="#A9CC5B", cyan="#5BC8D8"),
    "light": dict(fg="#14202B", muted="#55657A", grid="#D5DBE3",
                  blu="#00538F", orange="#B66D00", brown="#8C4F30",
                  green="#5C8A22", cyan="#0E7C8E"),
}


class Theme(object):
    """One colour set plus the output directory its figures belong in."""

    def __init__(self, name, out_root):
        self.name = name
        self.__dict__.update(PALETTES[name])
        self.dir = out_root if name == "dark" else os.path.join(out_root, "light")
        os.makedirs(self.dir, exist_ok=True)

    def out(self, filename):
        return os.path.join(self.dir, filename)

    def apply(self, **extra):
        """Install this theme's colours as matplotlib defaults."""
        plt.rcParams.update({
            "font.family": ["Calibri", "DejaVu Sans"],
            "font.size": 13,
            "text.color": self.fg,
            "axes.labelcolor": self.fg,
            "xtick.color": self.muted,
            "ytick.color": self.muted,
            "axes.edgecolor": self.grid,
            # transparent throughout: the slide (or the paper) is the backdrop
            "figure.facecolor": "none",
            "axes.facecolor": "none",
            "savefig.facecolor": "none",
            "legend.frameon": False,
        })
        plt.rcParams.update(extra)
        return self


def save_aligned(charts, pad=0.1):
    """Save several charts so that they line up when shown in turn -- the
    matplotlib twin of \\figframe in shared/figs/preamble.tex.

    `charts` is a list of (figure, path); all figures must have the same
    figsize. tight_layout and bbox_inches="tight" would fit every chart to its
    own labels, so the axes would sit at a slightly different place in each
    and the image size would differ too. Instead, all charts get the margins
    of the most demanding one (same axes rectangle) and are cropped to the
    union of their extents (same image size)."""
    from matplotlib.transforms import Bbox

    figs = [fig for fig, _ in charts]
    sizes = {tuple(fig.get_size_inches()) for fig in figs}
    assert len(sizes) == 1, "save_aligned needs equal figsizes, got %s" % sizes
    for fig in figs:
        fig.tight_layout()
    margins = dict(left=max(f.subplotpars.left for f in figs),
                   bottom=max(f.subplotpars.bottom for f in figs),
                   right=min(f.subplotpars.right for f in figs),
                   top=min(f.subplotpars.top for f in figs))
    for fig in figs:
        fig.subplots_adjust(**margins)
    box = Bbox.union([fig.get_tightbbox(fig.canvas.get_renderer())
                      for fig in figs]).padded(pad)
    for fig, path in charts:
        fig.savefig(path, format="svg", transparent=True, bbox_inches=box)
        plt.close(fig)
        print("wrote", os.path.join(os.path.basename(os.path.dirname(path)),
                                    os.path.basename(path)))


def themes(out_root):
    """Both themes, writing into `out_root` (the deck's figs/out) and
    `out_root/light` respectively."""
    return [Theme(name, out_root) for name in ("dark", "light")]
