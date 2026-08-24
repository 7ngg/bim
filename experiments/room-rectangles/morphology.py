"""Opening and closing that do what their names say.

`why_k.py`'s `clean()` is documented as "opening then closing: drop protrusions
and fill notches narrower than r" with `CLEAN_CELLS = 2` labelled a 500 mm
structuring element. Measured against synthetic masks it does none of that:

  * `_shift_all` pads and then slices back to the ORIGINAL shape, so a dilation
    cannot grow past the array bounds. `why_k.py` rasterises each room over its
    own tight bounding box, so every room fills its array to the edge and the
    dilation is a no-op on it;
  * the composition is therefore erosion-dominated. On a tight-bbox 3.0 x 4.0 m
    rectangle it returns 96 of 192 cells -- the room eroded by 500 mm on every
    side, never restored;
  * a strip 500 mm wide is deleted entirely, so the true deletion threshold is
    ~750 mm, not 500 mm;
  * and on a padded mask it fills NO notch at all -- 250, 500, 750 and 1000 mm
    corner notches all survive untouched.

So "k after erasing features narrower than 500 mm" is really "k of the room
eroded by 500 mm all round", which is a much larger claim about a much larger
operation. This module is the honest version: a square structuring element of a
stated side, on a canvas padded so nothing is clipped, with opening and closing
as separate, testable steps.

`selftest()` asserts the properties the names promise. Run it before quoting
anything measured with this.
"""
from __future__ import annotations

import numpy as np


def _shift(m: np.ndarray, dy: int, dx: int) -> np.ndarray:
    """`m` translated by (dy, dx), vacated cells filled False."""
    out = np.zeros_like(m)
    h, w = m.shape
    ys = slice(max(0, -dy), h - max(0, dy))
    yd = slice(max(0, dy), h - max(0, -dy))
    xs = slice(max(0, -dx), w - max(0, dx))
    xd = slice(max(0, dx), w - max(0, -dx))
    out[yd, xd] = m[ys, xs]
    return out


def erode(m: np.ndarray, s: int) -> np.ndarray:
    """Erosion by an s x s square. Outside the array counts as background."""
    out = m.copy()
    for dy in range(s):
        for dx in range(s):
            out &= _shift(m, -dy, -dx)
    return out


def dilate(m: np.ndarray, s: int) -> np.ndarray:
    out = m.copy()
    for dy in range(s):
        for dx in range(s):
            out |= _shift(m, dy, dx)
    return out


def _pad(m: np.ndarray, s: int) -> np.ndarray:
    return np.pad(m, 2 * s, constant_values=False)


def _unpad(m: np.ndarray, s: int) -> np.ndarray:
    return m[2 * s:m.shape[0] - 2 * s, 2 * s:m.shape[1] - 2 * s]


def opening(m: np.ndarray, s: int) -> np.ndarray:
    """Drop protrusions and necks narrower than s cells. Never adds."""
    p = _pad(m, s)
    return _unpad(dilate(erode(p, s), s), s)


def closing(m: np.ndarray, s: int) -> np.ndarray:
    """Fill notches and gaps narrower than s cells. Never removes."""
    p = _pad(m, s)
    return _unpad(erode(dilate(p, s), s), s)


def clean(m: np.ndarray, s: int = 2) -> np.ndarray:
    """Opening then closing at s cells: erase small hardware, both signs.

    A pipe boxing is a notch, a chimney breast is a protrusion, and a room has
    both. `s = 2` on the 250 mm solve grid erases anything under 500 mm, which
    is the grid's own resolution limit -- nothing narrower is representable
    whatever this returns.
    """
    return closing(opening(m, s), s)


def selftest() -> None:
    r = np.zeros((12, 16), bool)
    r[:] = True
    assert (clean(r, 2) == r).all(), "a plain rectangle must survive untouched"

    for s, keep in ((2, 2), (3, 3)):
        for w in range(1, 6):
            m = np.zeros((20, 12), bool)
            m[:, :w] = True
            got = opening(m, s).any()
            assert got == (w >= keep), f"opening s={s} on a {w}-cell strip"

    # A bite out of the MIDDLE of an edge -- a pipe boxing -- is what closing
    # fills. Width n is filled iff the element cannot enter it.
    for s in (2, 3, 4):
        for n in range(1, 5):
            m = np.zeros((14, 14), bool)
            m[:] = True
            m[0:2, 6:6 + n] = False
            filled = bool(closing(m, s)[0:2, 6:6 + n].all())
            assert filled == (n < s), f"closing s={s} on an {n}-cell edge notch"

    # A CORNER bite is NOT filled by closing at any size, because the element
    # reaches it from the background. Stated because it bounds what any
    # morphological clean-up can claim: a boxing in a corner survives, and a
    # corner bite is exactly the shape that turns a rectangle into an L.
    m = np.zeros((14, 14), bool)
    m[:] = True
    m[0:1, 0:1] = False
    assert not closing(m, 4)[0, 0], "a corner bite survives closing -- by design"
    print("morphology selftest: ok")


if __name__ == "__main__":
    selftest()
