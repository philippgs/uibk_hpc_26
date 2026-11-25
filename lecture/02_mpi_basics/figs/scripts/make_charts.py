"""Regenerate the osu_latency charts from figs/data/osu_latency.csv.

These replace the two PowerPoint chart objects; the numbers are the ones that
were cached inside the original .pptx (see extract_data.py).

Like every other figure, each chart is written twice: the dark variant into
figs/out/ and the light one into figs/out/light/ (see shared/figs/figtheme.py).
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from figtheme import save_aligned, themes  # shared/figs, put on PYTHONPATH by build_figs.py

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data", "osu_latency.csv"))
OUT = os.path.normpath(os.path.join(HERE, "..", "out"))


def load():
    with open(DATA, encoding="utf8") as fh:
        rows = list(csv.DictReader(fh))
    cats = [r["problem_size"] for r in rows]
    cols = {k: [float(r[k]) for r in rows]
            for k in rows[0] if k != "problem_size"}
    return cats, cols


def style(ax, t):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=t.grid, linewidth=0.8)
    ax.set_axisbelow(True)


# The slide shows the charts at a fixed height, so a smaller canvas means
# larger text and markers on the slide; at 10 x 4.8 in the labels were tiny.
FIGSIZE = (7.6, 3.65)


def chart_latency(t, cats, cols):
    """Slide 49: latency only."""
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.plot(cats, cols["latency intra socket"], "-o", color=t.blu,
            linewidth=2.2, markersize=6, label="latency intra socket")
    ax.plot(cats, cols["latency inter socket"], "-s", color=t.orange,
            linewidth=2.2, markersize=6, label="latency inter socket")
    ax.set_xlabel("problem size")
    ax.set_ylabel("latency [us]")
    ax.set_ylim(0, 4000)
    style(ax, t)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2)
    return fig


def chart_latency_l3(t, cats, cols):
    """Slide 50: latency plus L3 cache misses on a secondary axis."""
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.plot(cats, cols["latency intra socket"], "-o", color=t.blu,
            linewidth=2.2, markersize=6, label="latency intra socket")
    ax.plot(cats, cols["latency inter socket"], "-s", color=t.orange,
            linewidth=2.2, markersize=6, label="latency inter socket")
    ax.set_xlabel("problem size")
    ax.set_ylabel("latency [us]")
    ax.set_ylim(0, 4000)
    style(ax, t)

    ax2 = ax.twinx()
    ax2.plot(cats, cols["L3 misses intra socket"], "-x", color=t.brown,
             linewidth=2.0, markersize=7, label="L3 misses intra socket")
    ax2.plot(cats, cols["L3 misses inter socket"], "-D", color=t.green,
             linewidth=2.0, markersize=5, label="L3 misses inter socket")
    ax2.set_ylabel("L3 cache misses [1]")
    ax2.set_ylim(0, 1200000)
    # plain grouped digits rather than matplotlib's "1e6" offset label
    ax2.yaxis.set_major_formatter(
        FuncFormatter(lambda v, _: "{:,}".format(int(v)).replace(",", ".")))
    ax2.spines["top"].set_visible(False)
    ax2.tick_params(colors=t.muted)
    ax2.yaxis.label.set_color(t.fg)

    handles = ax.get_legend_handles_labels()[0] + ax2.get_legend_handles_labels()[0]
    labels = ax.get_legend_handles_labels()[1] + ax2.get_legend_handles_labels()[1]
    ax.legend(handles, labels, loc="upper center",
              bbox_to_anchor=(0.5, -0.22), ncol=2)

    return fig


def main():
    cats, cols = load()
    for t in themes(OUT):
        t.apply()
        # the two are shown on consecutive slides: same axes, same size
        save_aligned([
            (chart_latency(t, cats, cols), t.out("s49_latency.svg")),
            (chart_latency_l3(t, cats, cols), t.out("s50_latency_l3.svg"))])


if __name__ == "__main__":
    main()
