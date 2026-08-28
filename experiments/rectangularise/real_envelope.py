"""Turn real dwellings into Envelopes the solver harness can be handed.

Ticket 58, and the counterpart to `real_boundary.py`: that file measured whether
a real outline is *representable*, this one emits the two Envelopes a paired
solver arm needs, per dwelling, in the fit record's own frame.

Two Envelopes come out of each dwelling and the pair is the point:

  * **cap** -- `envelope_approx(mask, 2)`: bbox minus at most two notches, ADR
    0003's object, sampled per dwelling instead of fitted per room count. Against
    `CORPUS_ENVELOPES` this isolates **sampling**: same shape family, same
    generated ground truth, one Envelope per real dwelling rather than one per
    count.
  * **real** -- the true 250 mm cell mask, partitioned exactly. Against **cap**
    this isolates **shape**: the articulation ADR 0003 cannot express.

Both are emitted in `envelope_approx`'s frame -- the mask's own bounding box --
which is also the frame `swiss_fit_k2.json`'s rectangles are recorded in, so the
two can be compared without a coordinate assumption.

⚠️ **The real arm's ground truth is a RE-FIT, and it has to be.** The recorded
rectangles are fitted to the **cap** Envelope, which is a superset of the true
outline, so on the true outline they fail the validator twice over -- H1, a Room
poking into ground the dwelling never occupied, and H3, cells no rectangle
reaches. Seven of the first eight real slots were invalid that way. `refit_to_
true_mask` re-runs the shipped conversion with the domain set to the true mask;
the result is inside the boundary by construction, and what is left is the
coverage slack ADR 0028 calls the enclosed void. Both are emitted -- `truth` is
the re-fit, `cap_truth` the recorded one -- so the difference is measurable
rather than assumed.

⚠️ The **real** arm's parts are a *slab* partition, not a minimum one. Measured
over 400 dwellings the two agree at the median (ratio 1.00), and the slab is
deterministic, tiles exactly and is the shape `envelope_fit.build` itself emits.
`real_boundary.min_rectangles` is the exact count if a comparison is wanted.

⚠️ **`parts` is inert on the real arm.** `scenarios.ground_truth` gives every part
at least one room, and a real outline has a median of 6 parts against 1-4 on both
shipped fixtures -- 96 % of dwellings have a part no room fits. The real arm must
therefore supply its own truth, which is why it exists. `parts` is emitted so the
object is well-formed, never so it can be dissected.

Writes `series/real_envelopes.json.gz`. Costs ~0.4 s/dwelling.

Run: ../../venv/Scripts/python.exe real_envelope.py [n]
"""
import gzip
import json
import pickle
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fit_rects  # noqa: E402
from fit_rects import (envelope_approx, keep_largest_component,  # noqa: E402
                       watershed)
from real_boundary import crop, frame_geoms, min_rectangles  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
SERIES = Path(__file__).resolve().parent / "series"

# The band the corpus fixture serves (ADR 0029) -- a real arm outside it has no
# control to be paired against.
BAND_N = (5, 11)


def slab_rects(mask):
    """Exact rectangular partition by full-height column blocks, as coordinates.

    `envelope_fit.build`'s own shape: cut at every x where the column mask
    changes, then split each block into its maximal vertical runs. Deterministic,
    tiles exactly, and its count matched the theoretical minimum at the median
    over 400 dwellings.
    """
    ny, nx = mask.shape
    out = []
    x = 0
    while x < nx:
        col = mask[:, x]
        x2 = x + 1
        while x2 < nx and np.array_equal(mask[:, x2], col):
            x2 += 1
        y = 0
        while y < ny:
            if not col[y]:
                y += 1
                continue
            y2 = y
            while y2 < ny and col[y2]:
                y2 += 1
            out.append([int(x), int(y), int(x2), int(y2)])
            y = y2
        x = x2
    return out


def true_mask_envelope(domain, max_notches=2):
    """`envelope_approx`'s contract, with the TRUE mask as the Envelope.

    Substituted for `envelope_approx` at the call boundary in `fit_rects.
    run_dwelling`, which uses its first return purely as a boolean domain mask.
    The shipped file is not edited: `fit_rects.py` is the conversion four closed
    decisions rest on, and this arm needs a different domain, not a different
    conversion.

    Why a re-fit is needed at all. `swiss_fit_k2.json`'s rectangles are fitted
    to the CAP Envelope -- bbox minus at most two notches, a **superset** of the
    true outline -- so on the true outline they fail the validator in two ways
    at once: a Room pokes into the part of the cap the dwelling never occupied
    (H1, "leaves the Envelope") and the cells no rectangle reaches become
    unassigned floor (H3). Measured on the first eight real slots, **seven**
    witnesses were invalid. The converted dwelling is not a witness for its own
    boundary; it is a witness for its cap approximation.
    """
    ys, xs = np.nonzero(domain)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    sub = domain[y0:y1, x0:x1]
    h, w = sub.shape
    return sub, [], {
        "notches_all": 0, "notches_needed": 0, "notches_used": 0,
        "holes_filled": 0, "envelope_loss": 0.0,
        "envelope_loss_by_k": {str(k): 0.0 for k in range(5)},
        "bbox_fill": float(sub.sum()) / (h * w),
    }, (y0, x0)


def refit_to_true_mask(geoms, k_max=2, time_limit=10.0):
    """Re-fit one dwelling's Rooms with the true outline as the domain.

    Returns `run_dwelling`'s record. Its `parts` tile the TRUE mask up to the
    fit's own soft-coverage slack, which is what makes it usable as the real
    arm's witness. INFEASIBLE here is itself a measurement -- it says the
    conversion cannot express this dwelling as rectangles inside its own
    boundary, which the cap approximation never had to answer.
    """
    orig = fit_rects.envelope_approx
    fit_rects.envelope_approx = true_mask_envelope
    try:
        return fit_rects.run_dwelling(geoms, k_max=k_max, time_limit=time_limit)
    finally:
        fit_rects.envelope_approx = orig


def main():
    n_target = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    recs = [r for r in json.load(open(OUT / "swiss_fit_k2.json"))
            if r.get("envelope_loss_by_k")
            and r.get("status") in ("OPTIMAL", "FEASIBLE")
            and BAND_N[0] <= r.get("n", 0) <= BAND_N[1]]
    dw, _keys = pickle.load(open(OUT / "swiss_dw.pkl", "rb"))
    print(f"in-band converted records: {len(recs)}; emitting up to {n_target}",
          flush=True)

    rows, skipped = [], Counter()
    for r in recs:
        if len(rows) >= n_target:
            break
        items = dw.get(tuple(r["k"].split("|")))
        if items is None:
            skipped["no_items"] += 1
            continue
        geoms = frame_geoms(items)
        if geoms is None:
            skipped["no_frame"] += 1
            continue
        lab, _x0, _y0 = watershed(geoms)
        if lab is None:
            skipped["no_raster"] += 1
            continue
        mask = crop(keep_largest_component(lab) >= 0)
        if mask.sum() < 64:
            skipped["tiny"] += 1
            continue
        cap_env, cap_notches, info, _off = envelope_approx(mask, 2)
        if cap_env.shape != mask.shape:
            skipped["frame_mismatch"] += 1
            continue

        H, W = mask.shape
        # `parts[i]` is Room i's one or two rectangles (ADR 0014). The harness's
        # truth is ONE Rect per Room, so a two-rectangle Room contributes its
        # larger part and the remainder becomes measured witness loss.
        # Restricting to all-k=1 dwellings instead would select the simplest
        # outlines and flatter the real arm; the loss is reported rather than
        # selected away.
        if not r.get("parts") or len(r["parts"]) != r["n"]:
            skipped["no_parts"] += 1
            continue
        rects = [max(p, key=lambda q: (q[2] - q[0]) * (q[3] - q[1]))
                 for p in r["parts"]]
        # The fit's rectangles are recorded in this same frame. Guard it rather
        # than assume it: a rectangle outside the bbox means the frame moved.
        if any(not (0 <= a and 0 <= b and c <= W and d <= H) for a, b, c, d in rects):
            skipped["rects_out_of_frame"] += 1
            continue
        if any((c - a) < 1 or (d - b) < 1 for a, b, c, d in rects):
            skipped["degenerate_rect"] += 1
            continue

        # The real arm's witness: rectangles fitted to the TRUE mask, not to
        # the cap. See `true_mask_envelope` for why the cap fit cannot serve.
        rf = refit_to_true_mask(geoms)
        if rf.get("status") not in ("OPTIMAL", "FEASIBLE") or not rf.get("parts"):
            skipped[f"refit_{rf.get('status')}"] += 1
            continue
        if len(rf["parts"]) != r["n"]:
            skipped["refit_count"] += 1
            continue
        true_truth = [max(p, key=lambda q: (q[2] - q[0]) * (q[3] - q[1]))
                      for p in rf["parts"]]
        if any((c - a) < 1 or (d - b) < 1 for a, b, c, d in true_truth):
            skipped["refit_degenerate"] += 1
            continue

        real_parts = slab_rects(mask)
        real_notch = slab_rects(~mask)
        cap_parts = slab_rects(cap_env)
        cap_notch = slab_rects(~cap_env)
        exact, mrinfo = min_rectangles(mask)

        # How much of the true interior the dwelling's own fitted rectangles
        # cover. This is the honest size of the real arm's witness: it is a
        # coverage-soft witness, never Parts I-III's provable one.
        cov = np.zeros_like(mask)
        for a, b, c, d in true_truth:
            cov[b:d, a:c] = True
        capcov = np.zeros_like(mask)
        for a, b, c, d in rects:
            capcov[b:d, a:c] = True
        rows.append({
            "k": r["k"], "n": r["n"], "W": int(W), "H": int(H),
            "real_cells": int(mask.sum()), "cap_cells": int(cap_env.sum()),
            "real_parts": real_parts, "real_notches": real_notch,
            "cap_parts": cap_parts, "cap_notches": cap_notch,
            "truth": true_truth,
            "cap_truth": rects,
            "k_used": rf.get("k_used"),
            "refit_status": rf.get("status"),
            "refit_seconds": round(rf.get("seconds", 0.0), 2),
            "refit_uncovered": rf.get("uncovered"),
            "refit_worst_iou": round(min(rf["iou"]), 4) if rf.get("iou") else None,
            "min_rects": exact, "slab_rects": len(real_parts),
            "reflex": mrinfo["reflex"],
            "notches_all": info["notches_all"],
            "envelope_loss": r["envelope_loss"],
            "witness_cov": round(float((cov & mask).sum()) / int(mask.sum()), 4),
            "witness_spill": round(float((cov & ~mask).sum()) / int(mask.sum()), 4),
            "capfit_cov": round(float((capcov & mask).sum()) / int(mask.sum()), 4),
            "capfit_spill": round(float((capcov & ~mask).sum()) / int(mask.sum()), 4),
            "worst_iou": round(min(r["iou"]), 4) if r.get("iou") else None,
        })
        if len(rows) % 25 == 0:
            print(f"  {len(rows)}", flush=True)

    SERIES.mkdir(exist_ok=True)
    with gzip.open(SERIES / "real_envelopes.json.gz", "wt", encoding="utf-8") as fh:
        json.dump(rows, fh)
    print(f"\nwrote {SERIES / 'real_envelopes.json.gz'}  ({len(rows)} dwellings)")
    print(f"skipped: {dict(skipped)}")

    print(f"\nper room count: "
          f"{dict(sorted(Counter(r['n'] for r in rows).items()))}")
    for tag in ("real", "cap"):
        p = [len(r[f"{tag}_parts"]) for r in rows]
        nn = [len(r[f"{tag}_notches"]) for r in rows]
        print(f"  {tag:>4}: parts median {int(np.median(p))} p90 "
              f"{int(np.percentile(p,90))} max {max(p)}   "
              f"notch rects median {int(np.median(nn))} max {max(nn)}")
    k2 = sum(1 for r in rows if any(k > 1 for k in (r["k_used"] or [])))
    print(f"\n  dwellings with a two-rectangle Room (its smaller part is "
          f"dropped from the truth): {k2/len(rows):.4f}")
    wc = [r["witness_cov"] for r in rows]
    ws = [r["witness_spill"] for r in rows]
    print(f"\n  witness coverage of the true interior: p10 "
          f"{np.percentile(wc,10):.3f} median {np.median(wc):.3f} "
          f"p90 {np.percentile(wc,90):.3f}")
    print(f"  witness spill outside it:              p10 "
          f"{np.percentile(ws,10):.3f} median {np.median(ws):.3f} "
          f"p90 {np.percentile(ws,90):.3f}")
    print(f"  dwellings whose witness both covers >= 0.90 and spills <= 0.05: "
          f"{sum(a >= .90 and b <= .05 for a, b in zip(wc, ws))/len(rows):.4f}")


if __name__ == "__main__":
    main()
