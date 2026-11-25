"""Regenerate the Amdahl / Gustafson curves of this deck.

These three charts were PowerPoint chart objects, but unlike the osu_latency
measurements in lecture 02 they are not data -- they are the laws themselves,
evaluated for a handful of sequential fractions. So there is no CSV here: the
formulas are the source, which makes the charts exactly reproducible and lets
the parameters be changed by editing one line.

    Amdahl     speedup(n)    = 1 / (a + (1 - a)/n)      fixed problem size
               efficiency(n) = speedup(n) / n
    Gustafson  speedup(P)    = a + (1 - a) * P          problem scales with P

Each chart is written twice: the dark variant into figs/out/ and the light one
into figs/out/light/ (see shared/figs/figtheme.py).
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from figtheme import save_aligned, themes  # shared/figs, put on PYTHONPATH by build_figs.py

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "out"))

# one series per sequential fraction, in the deck's palette where possible
SERIES = [(0.1, "blu", "o"), (0.2, "orange", "s"), (0.3, "brown", "x"),
          (0.4, "green", "D"), (0.5, "cyan", "^")]
CORES = list(range(1, 9))


def amdahl(a, n):
    return 1.0 / (a + (1.0 - a) / n)


def gustafson(a, p):
    return a + (1.0 - a) * p


def chart(t, path, fn, ylabel, ylim):
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    for a, role, marker in SERIES:
        ax.plot(CORES, [fn(a, n) for n in CORES], "-", marker=marker,
                color=getattr(t, role), linewidth=2.0, markersize=6,
                label=r"$\alpha$=%.1f" % a)
    ax.set_xlabel("number of cores")
    ax.set_ylabel(ylabel)
    ax.set_xticks(CORES)
    ax.set_ylim(*ylim)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=t.grid, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=5,
              handlelength=1.6, columnspacing=1.2)
    return fig, path


def main():
    for t in themes(OUT):
        t.apply()
        # same chart three times over: keep the axes in place between them
        save_aligned([
            chart(t, t.out("s11_amdahl_speedup.svg"),
                  amdahl, "ideal speedup", (0, 5)),
            chart(t, t.out("s12_amdahl_efficiency.svg"),
                  lambda a, n: amdahl(a, n) / n, "efficiency", (0, 1.2)),
            chart(t, t.out("s15_gustafson.svg"),
                  gustafson, "ideal speedup", (0, 8))])


if __name__ == "__main__":
    main()
