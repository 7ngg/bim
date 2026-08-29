"""The single accessor between a region profile and everything that consumes it.

Ticket 69. `absolute_area.STAT_FLOOR` was a hand transcription of
`room-constraints.json` with nothing in the repo binding the two, and the ticket
was raised on the RISK of drift. Three of the eight copies it names were already
wrong when it was taken:

  * `absolute_area.MARKET` sat four cells behind ADR 0035, which had landed the
    day before -- PRIVATE 12,0 against 13,2, both living limbs 16,0 against 17,6,
    and KITCHEN_DINING reading a `part` cell ADR 0034 forbids as a target.
  * `absolute_area.HABITABLE` omitted DINING, whose `counts_as_otaq` is true, so
    `floors_for` under-counted otaq and could hand a living room the one-otaq
    floor 15,0 where the profile's own guard says 16,0.
  * `fit_warp.MIN_SIDE` had no KITCHEN_DINING entry and fell to the default 5,
    one grid cell below the 6 its own stated formula gives.

WHY A MODULE AND NOT SIX JSON LOOKUPS. `floors_for` did not merely copy numbers;
it hand-implemented `mapping.rooms[*].az_area`'s GUARD RESOLUTION -- the
`when_otaq_count` match, the fallthrough order, and the otaq set the condition
reads. A lookup replacing the values would have left the wrong half bound. And
the lookup could not be written at all: the copies are keyed by CORPUS label, the
profile by ERGONOMIC key, and no artefact published the map between them. It is
now `ergonomic.corpus_label_map`, and this module is its only reader.

THE DATA IS A HARD DEPENDENCY. `floor_warp._check_floor_transcription` returned
silently when `data/` was absent -- "rigs may run without the repo data" -- and
that escape hatch is what let a copy survive to be checked instead of read. There
is no fallback here: no file, no import. A rig that cannot see the profile cannot
size a room to it.

    sys.path.insert(0, <repo>/experiments/region-profile)
    from profile_read import statutory_floor_m2, market_default_m2, min_side_units

Every function takes an ERGONOMIC key. The `*_for_label` wrappers take a corpus
label and go through the bridge, for the rigs that speak that vocabulary.
"""
import json
import math
import pathlib

DATA = pathlib.Path(__file__).resolve().parents[2] / "data/standards/room-constraints.json"
PROFILE = "AZ"

if not DATA.exists():                       # hard, never a fallback -- see docstring
    raise RuntimeError(
        "profile_read: %s is missing. The region profile is a hard dependency of every "
        "rig that sizes a room -- ticket 69. There is deliberately no bundled fallback: "
        "a fallback copy is the drift this module exists to remove." % DATA)

DOC = json.loads(DATA.read_text(encoding="utf-8"))
_ERG = DOC["ergonomic"]["rooms"]
_MEDIANS = DOC["ergonomic"]["corpus_medians"]
_BRIDGE = DOC["ergonomic"]["corpus_label_map"]
_AZ = DOC["profiles"][PROFILE]["rooms"]
_MAPPING = _AZ["mapping"]["rooms"]
_AREAS = _AZ["areas_m2"]
_CONSTRUCTION = DOC["profiles"][PROFILE]["construction"]

# The solve grid and the internal wall thickness, READ rather than restated.
# `residue_class_mod_grid` publishes both, and ADR 0007's ship gate already
# asserts that the profile offers exactly one `t_int` -- so a rig pinning 250/150
# in its own header was a ninth and tenth copy of the same class as the six the
# ticket names. `t_int` is ADR 0010's layer-set TOTAL (120 structural + 2 x 15
# finish), which is the plane ADR 0001 erodes from.
GRID_MM = _CONSTRUCTION["residue_class_mod_grid"]["grid_mm"]
T_INT_MM = _CONSTRUCTION["residue_class_mod_grid"]["t_int_mm"]

COLLAPSE = {k: v for k, v in _BRIDGE["collapse"].items() if k != "comment"}


def labels():
    """Every corpus label the bridge defines, collapse sources included. Total by
    construction over what the conversion can emit -- so a table built over this
    never falls through to a default."""
    return list(_BRIDGE["labels"]) + list(COLLAPSE)

# `hall`, `entrance_lobby` and `corridor` share one merged median that ticket 31's
# three-way split made unusable, and corpus_medians records it as an explicit null.
# Rung 2 is empty for all three and the ladder falls through to absent, per brief.md 9.2.
_MEDIAN_KEY = {"hall": "hall_entrance_lobby_corridor",
               "entrance_lobby": "hall_entrance_lobby_corridor",
               "corridor": "hall_entrance_lobby_corridor"}


def _v(cell):
    return cell["v"] if isinstance(cell, dict) else None


# ---------------------------------------------------------------------------
# The bridge: corpus label -> ergonomic key.
# ---------------------------------------------------------------------------
def erg_key(label, lenient=False):
    """`ergonomic.corpus_label_map`, collapse applied first. Raises on a label the
    bridge does not define, because a silent default is what MIN_SIDE_DEFAULT did."""
    label = COLLAPSE.get(label, label)
    row = _BRIDGE["labels"].get(label)
    if row is None:
        raise KeyError("corpus label %r is not in ergonomic.corpus_label_map "
                       "(corpus %s)" % (label, _BRIDGE["corpus"]))
    if lenient and row["erg_lenient"]:
        return row["erg_lenient"]
    return row["erg"]


# ---------------------------------------------------------------------------
# The ergonomic layer -- region-free, and the base of every hard floor.
# ---------------------------------------------------------------------------
def ergonomic_min_area_m2(key):
    return _v(_ERG[key]["min_area"])


def min_clear_short_mm(key):
    return _v(_ERG[key]["min_clear_short"])


def counts_as_otaq(key):
    """AzDTN cl. 5.5's unit, `counts_as_otaq` -- NOT `is_habitable`. The two
    diverge on exactly one type (`kitchen_dining`) and gate V6 holds that."""
    return bool(_ERG[key]["counts_as_otaq"])


def otaq_count(keys):
    return sum(1 for k in keys if counts_as_otaq(k))


def min_side_units(key, t_int_mm=None, grid_mm=None):
    """The centreline rectangle a clear minimum needs, rounded UP onto the grid,
    because it is a floor: `ceil((min_clear_short + t_int) / grid)`. ADR 0001's
    erosion in reverse. DERIVED, not transcribed -- so what is bound here is the
    formula, where `fit_warp.MIN_SIDE` was the formula's frozen output."""
    t = T_INT_MM if t_int_mm is None else t_int_mm
    g = GRID_MM if grid_mm is None else grid_mm
    return math.ceil((min_clear_short_mm(key) + t) / g)


# ---------------------------------------------------------------------------
# The AZ profile -- resolved through the guard list, never by key.
# ---------------------------------------------------------------------------
def _guard(key, otaq):
    """`mapping.rooms[key].az_area`: ordered, first match wins, the single
    `when_otaq_count: null` limb last. Returns the matching guard entry or None."""
    guards = _MAPPING[key]["az_area"]
    if guards is None:
        return None
    for g in guards:
        w = g["when_otaq_count"]
        if w is None or (otaq is not None and w == otaq):
            return g
    return None


def statutory_floor_m2(key, otaq=None):
    """`dim.statutory_min_area`'s AZ limb. None where the profile is silent --
    ten of nineteen keys, and `mapping.null_means` says silence is not an error.

    A `part` read IS returned: ADR 0034 makes an entailed bound a sound lower
    bound on the room, so it may floor. What it may never do is target."""
    g = _guard(key, otaq)
    if g is None:
        return None
    total = _v((_AREAS[g["key"]] or {}).get("statutory_floor"))
    if total is None:
        return None
    for extra in g.get("compose_with") or []:
        total += _v(_AREAS[extra]["statutory_floor"])
    return total


def hard_area_floor_m2(key, otaq=None):
    """`CONTEXT.md`'s **Hard area floor**: max(ergonomic, statutory). The composed
    number every consumer wants, in the one place an amendment to either half
    lands."""
    erg = ergonomic_min_area_m2(key)
    stat = statutory_floor_m2(key, otaq)
    return erg if stat is None else max(erg, stat)


def market_default_m2(key, otaq=None):
    """`brief.md` 9.2's ladder -- `market_default` -> corpus median -> absent --
    with ADR 0034 decision 2 enforced HERE rather than by a comment: a `part` read
    may never feed the soft tier, so it falls straight through to rung 2.

    That rule is why `absolute_area.MARKET["KITCHEN_DINING"]` was 6,0. The cell it
    copied is real and first-hand (AzDTN 2.7-3 cl. 5.1) and it measures the
    kitchen ZONE; read as the kitchen-diner's target it under-targets the room by
    the whole dining half. Rung 2 gives 18,8."""
    g = _guard(key, otaq)
    if g is not None and g["referent"] != "part":
        v = _v((_AREAS[g["key"]] or {}).get("market_default"))
        if v is not None:
            return v
    return _v(_MEDIANS.get(_MEDIAN_KEY.get(key, key)))          # rung 2, or absent


# ---------------------------------------------------------------------------
# Corpus-label wrappers, for the rigs that speak that vocabulary.
# ---------------------------------------------------------------------------
def statutory_floor_for_label(label, otaq=None, lenient=False):
    return statutory_floor_m2(erg_key(label, lenient), otaq)


def hard_area_floor_for_label(label, otaq=None, lenient=False):
    return hard_area_floor_m2(erg_key(label, lenient), otaq)


def market_default_for_label(label, otaq=None, lenient=False):
    return market_default_m2(erg_key(label, lenient), otaq)


def ergonomic_min_area_for_label(label, lenient=False):
    return ergonomic_min_area_m2(erg_key(label, lenient))


def min_side_units_for_label(label, t_int_mm=None, grid_mm=None, lenient=False):
    return min_side_units(erg_key(label, lenient), t_int_mm, grid_mm)


def otaq_count_for_labels(labs, lenient=False):
    return otaq_count([erg_key(l, lenient) for l in labs])


# ---------------------------------------------------------------------------
# The tables the rigs import by name. Built from the data at import, so they are
# a CACHE OF A READ and never a transcription -- every consumer that did
# `MIN_SIDE.get(t, MIN_SIDE_DEFAULT)` keeps working and there is no copy left.
# ---------------------------------------------------------------------------
def min_side_table(t_int_mm=None, grid_mm=None):
    return {lab: min_side_units_for_label(lab, t_int_mm, grid_mm) for lab in labels()}


def ergonomic_area_table():
    return {lab: ergonomic_min_area_for_label(lab) for lab in labels()}


def market_default_table(otaq=None):
    """`dim.market_default_area`'s target per corpus label. A label whose ladder
    ends at absent is OMITTED rather than zeroed, so a consumer doing
    `max(a, TABLE.get(t, 0.0))` gets the documented no-preference behaviour."""
    out = {}
    for lab in labels():
        v = market_default_for_label(lab, otaq)
        if v is not None:
            out[lab] = v
    return out
