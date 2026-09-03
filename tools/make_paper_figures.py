#!/usr/bin/env python3
"""The three figures, regenerated from data/ like the tables.

A reader of this paper currently never sees a series. That is a real gap: §6.1's
central methodological claim is that the SAME archive yields opposite diachronic
conclusions depending on what counts as one document, and a sentence asserting a
sign reversal is far weaker than a panel showing two lines going opposite ways.

Figure 1 is therefore the composition lesson, not the headline trend.
Figure 2 is the confirmatory contrast, drawn so the reader can see how little
post-period there is to work with — three years against twenty-four.
Figure 3 puts the observed effect on the power curve that was computed before it
existed, which is the paper's strongest single image: the estimate sits almost
exactly on the threshold where the design has ~0.16 power.

Style is deliberately plain: no colour semantics beyond two hues, no gridline
decoration, and every axis labelled in the units the text uses.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

# Type 42 (TrueType), not matplotlib's Type 3 default. Type 3 embeds each
# glyph as a CharProc rather than a font program, which several journal
# production pipelines reject outright, and the four figure pages of the
# submission PDF were shipping it.
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "figures"
CUT = 2023
WB, IMF = "#1f4e79", "#b45f06"


def rows(rel: str) -> list[dict]:
    p = ROOT / rel
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def save(fig, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=200, bbox_inches="tight")
    # PLOS asks for figure files as TIFF or EPS; 300 dpi TIFF, LZW so the
    # four files stay small enough to upload.
    fig.savefig(OUT / f"{name}.tif", dpi=300, bbox_inches="tight",
                pil_kwargs={"compression": "tiff_lzw"})
    plt.close(fig)
    print(f"[figures] wrote docs/figures/{name}.png, .pdf and .tif")


def fig1_composition() -> None:
    """Assembled vs document-level, same archive, opposite sign."""
    ar = rows("data/features/ar_fy_features.csv")
    doc = [r for r in rows("data/features/classic.csv")
           if r["stratum"] == "annual_report"]
    if not ar or not doc:
        print("[figures] fig1 skipped (inputs missing)")
        return

    asm = sorted((int(r["year"]), float(r["temporal_per1k"])) for r in ar)
    per_year = defaultdict(lambda: [0.0, 0.0])
    for r in doc:
        y = int(r["year"])
        tok = float(r["tokens"] or 0)
        per_year[y][0] += float(r["temporal_per1k"] or 0) * tok
        per_year[y][1] += tok
    # YEAR-MATCHED. The document pool runs to fiscal 2025 and the assembled
    # series stops at 2024; drawing each over its own span makes the two panels
    # answer slightly different questions, and comparing era means across those
    # unmatched sets manufactured an apparent sign reversal that does not exist
    # (fiscal 2025 is a single document at roughly twice its neighbours). The
    # figure is restricted to the years both series have.
    common = {y for y, _ in asm} & {y for y, v in per_year.items() if v[1] > 0}
    asm = [(y, v) for y, v in asm if y in common]
    dl = sorted((y, v[0] / v[1]) for y, v in per_year.items()
                if v[1] > 0 and y in common)

    # Third panel: the files the assembled series EXCLUDES by ruling — sibling
    # organisation volumes and duplicates. The decomposition
    # (tools/rq1_decomposition.py) shows these carry the entire 43%-vs-14%
    # contrast, while concatenation into fiscal-year units contributes nothing,
    # so the figure has to show them rather than leave them implicit.
    asm_ids = set()
    for r in ar:
        asm_ids.update(x for x in r.get("doc_ids", "").split(";") if x)
    ex = defaultdict(lambda: [0.0, 0.0])
    for r in doc:
        if r["id"] in asm_ids:
            continue
        y = int(r["year"])
        tok = float(r["tokens"] or 0)
        if tok <= 0 or y not in common:
            continue
        ex[y][0] += float(r["temporal_per1k"] or 0) * tok
        ex[y][1] += tok
    exc = sorted((y, v[0] / v[1]) for y, v in ex.items() if v[1] > 0)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2), sharey=True)
    for ax, series, title in (
            (axes[0], asm, "Assembled fiscal-year units\n(the Bank's own volumes)"),
            (axes[1], dl, "Whole document pool\n(assembled + excluded files)"),
            (axes[2], exc, "The EXCLUDED files\n(sibling organisations, duplicates)")):
        xs = [a for a, _ in series]
        ys = [b for _, b in series]
        ax.plot(xs, ys, lw=1.0, color="#999999")
        ax.scatter(xs, ys, s=9, color=WB, zorder=3)
        # decade means make the direction legible without smoothing the data away
        dec = defaultdict(list)
        for x, y in series:
            dec[x // 10 * 10].append(y)
        dx = sorted(dec)
        ax.plot([d + 5 for d in dx], [sum(dec[d]) / len(dec[d]) for d in dx],
                lw=2.4, color="#c00000", zorder=4, label="decade mean")
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("fiscal year")
        ax.legend(frameon=False, fontsize=8, loc="upper right")
    axes[0].set_ylabel("temporal anchoring per 1,000 tokens")
    fig.suptitle("Figure 1 — The factor of three is document selection, not unit "
                 "definition: the excluded files trend the other way",
                 fontsize=11, y=1.02)
    save(fig, "fig1_composition")


def fig2_panels() -> None:
    """Tier-1 rate by institution, with the post period drawn to scale."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, panel, wb_label in ((axes[0], "P1", "World Bank — ICR"),
                                (axes[1], "P2", "World Bank — PAD")):
        cells = rows(f"data/analysis/panels/cells_{panel}.csv")
        if not cells:
            continue
        for inst, colour, label in (("WB", WB, wb_label),
                                    ("IMF", IMF, "IMF Article IV")):
            pts = sorted((int(r["year"]),
                          1000 * float(r["count"]) / float(r["tokens"]))
                         for r in cells if r["institution"] == inst
                         and float(r["tokens"]) > 0)
            ax.plot([a for a, _ in pts], [b for _, b in pts], lw=1.6,
                    marker="o", ms=3.4, color=colour, label=label)
        ax.axvline(CUT - 0.5, color="#444444", ls="--", lw=1.0)
        ax.annotate("prespecified\nbreak 2023", xy=(CUT - 0.4, ax.get_ylim()[1]),
                    xytext=(CUT - 7.2, ax.get_ylim()[1] * 0.92), fontsize=8,
                    color="#444444")
        ax.set_title(f"{panel}: {wb_label} vs IMF", fontsize=10)
        ax.set_xlabel("year")
        ax.legend(frameon=False, fontsize=8, loc="upper left")
    axes[0].set_ylabel("Tier-1 markers per 1,000 tokens")
    fig.suptitle("Figure 2 — The confirmatory contrast: 24 pre-period years "
                 "against 3 post-period years", fontsize=11, y=1.02)
    save(fig, "fig2_panels")


def fig3_power() -> None:
    """The observed effect, placed on the curve computed before it existed."""
    src = None
    for cand in ("data/analysis/mde_p1p2/curve_companion_full.csv",
                 "data/analysis/mde_p1p2/curve_companion_half.csv",
                 "data/analysis/mde_p1p2/curve_companion_zero.csv"):
        if (ROOT / cand).exists():
            src = cand
            break
    if not src:
        print("[figures] fig3 skipped (no curve file)")
        return
    curves = {}
    for cand, name in (("curve_companion_zero.csv", "companion: zero"),
                       ("curve_companion_half.csv", "companion: half"),
                       ("curve_companion_full.csv", "companion: full")):
        rs = rows(f"data/analysis/mde_p1p2/{cand}")
        if not rs:
            continue
        col = next((c for c in rs[0] if "family" in c and "power" in c), None)
        col = col or next((c for c in rs[0] if c.startswith("power")), None)
        tcol = next((c for c in rs[0] if c.strip().lower() in ("theta", "θ")), None)
        if not col or not tcol:
            continue
        curves[name] = sorted((float(r[tcol]), float(r[col])) for r in rs)
    if not curves:
        print("[figures] fig3 skipped (curve columns not recognised)")
        return

    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    for (name, pts), style in zip(curves.items(), ("-", "--", ":")):
        ax.plot([a for a, _ in pts], [b for _, b in pts], style, lw=1.8,
                label=name)
    ax.axhline(0.80, color="#c00000", lw=1.0)
    ax.text(0.02, 0.815, "0.80 required", color="#c00000", fontsize=8)
    ax.axvline(0.586, color=WB, ls="-.", lw=1.2)
    ax.text(0.60, 0.06, "observed P1 effect\nθ̂ = 0.586", color=WB, fontsize=8)
    ax.set_xlabel("θ — true differential effect (log points)")
    ax.set_ylabel("power")
    ax.set_ylim(0, 1)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.set_title("Figure 3 — Power computed before any outcome existed,\n"
                 "with the effect we later observed marked", fontsize=10)
    save(fig, "fig3_power")


def fig4_contrast() -> None:
    """The estimand itself, which no other figure shows.

    Figures 2 plots each institution's raw rate, which is what a reader wants
    first but is not what the model fits. With year fixed effects and two
    institutions the design reduces to a regression on the ANNUAL WORLD
    BANK-IMF LOG-RATE CONTRAST, against a constant, a linear trend and a post
    indicator. A referee asked to judge whether beta is identified needs to see
    that series and the line fitted through its pre-period, because the whole
    identification question is whether three post-period points depart from an
    extrapolation of that line.

    Drawn deliberately without a confidence band: the band would come from the
    frozen bootstrap and this is a display, not a second inference.
    """
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, panel, lab in ((axes[0], "P1", "P1 — ICR vs IMF"),
                           (axes[1], "P2", "P2 — PAD vs IMF")):
        cells = rows(f"data/analysis/panels/cells_{panel}.csv")
        if not cells:
            continue
        d = {}
        for r in cells:
            d.setdefault(int(r["year"]), {})[r["institution"]] = (
                float(r["count"]), float(r["tokens"]))
        yrs = sorted(y for y in d if {"WB", "IMF"} <= set(d[y]))
        import math
        contrast = []
        for y in yrs:
            wb, imf = d[y]["WB"], d[y]["IMF"]
            contrast.append(math.log((wb[0] + 0.5) / wb[1])
                            - math.log((imf[0] + 0.5) / imf[1]))
        pre = [i for i, y in enumerate(yrs) if y < CUT]
        post = [i for i, y in enumerate(yrs) if y >= CUT]
        ax.plot([yrs[i] for i in pre], [contrast[i] for i in pre], "o-",
                ms=4, lw=1.4, color=WB, label="pre-period contrast")
        ax.plot([yrs[i] for i in post], [contrast[i] for i in post], "o-",
                ms=6, lw=1.6, color="#c00000", label="post-period (3 years)")
        # least squares through the pre-period only, extrapolated across
        import numpy as np
        xs = np.array([yrs[i] for i in pre], dtype=float)
        ys = np.array([contrast[i] for i in pre], dtype=float)
        b, a = np.polyfit(xs, ys, 1)
        span = np.array([min(yrs), max(yrs)], dtype=float)
        ax.plot(span, a + b * span, "--", lw=1.4, color="#444444",
                label=f"pre-2023 trend, extrapolated ({b:+.3f}/yr)")
        ax.axvline(CUT - 0.5, color="#888888", lw=0.8)
        ax.set_title(lab, fontsize=10)
        ax.set_xlabel("year")
        ax.legend(frameon=False, fontsize=7.5, loc="upper left")
    axes[0].set_ylabel("log(WB rate) − log(IMF rate)")
    fig.suptitle("Figure 4 — The estimand: the annual World Bank–IMF log-rate "
                 "contrast, and the pre-2023 trend the post years depart from",
                 fontsize=11, y=1.02)
    save(fig, "fig4_contrast")


def main() -> int:
    fig1_composition()
    fig2_panels()
    fig3_power()
    fig4_contrast()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
