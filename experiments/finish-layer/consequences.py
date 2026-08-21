"""Ticket 35 — what moves if t_finish is not 15 mm.

Recomputes, for candidate finish thicknesses, the three quantities the ticket
names: the internal wall total, the ADR 0007 residue class, and ADR 0004's
even-thickness gate (which ADR 0010 consequence 2 binds on TOTALS, exempting a
layer component that only ever enters a total doubled).

Reads nothing and writes nothing outside this directory. The shipped profile is
NOT touched; this only reports arithmetic.
"""
T_INT_STRUCTURAL = 120   # AzDTN 2.17-1 cl. 4.3 / Table 29 n.2 — half-brick, verified
T_PARTY_STRUCTURAL = 250 # one brick, derived from the 50 dB requirement
GRID = 250               # ADR 0001 solve grid

def report(t_finish):
    t_int = T_INT_STRUCTURAL + 2 * t_finish
    t_party = T_PARTY_STRUCTURAL + 2 * t_finish
    residue = (-t_int) % GRID
    return {
        "t_finish": t_finish,
        "t_int": t_int,
        "t_party": t_party,
        "residue_class_mod_250": residue,
        "t_int_even": t_int % 2 == 0,
        "t_int_halves_cleanly": t_int % 2 == 0,   # erode() needs t_int/2 integral
        "t_party_halves_cleanly": t_party % 2 == 0,
    }

print(f"{'t_finish':>9} {'t_int':>6} {'t_party':>8} {'residue':>8} {'t_int even':>11} {'t_party even':>13}")
for tf in (8, 10, 12, 15, 18, 20, 25):
    r = report(tf)
    mark = "  <== shipped / proposed" if tf == 15 else ""
    print(f"{r['t_finish']:>9} {r['t_int']:>6} {r['t_party']:>8} "
          f"{r['residue_class_mod_250']:>8} {str(r['t_int_even']):>11} "
          f"{str(r['t_party_halves_cleanly']):>13}{mark}")

print()
print("ADR 0004 evenness, as sharpened by ADR 0010 consequence 2:")
print("  binds on TOTALS (they get halved by erode), NOT on a layer component")
print("  (it only ever enters a total doubled). 120 + 2*t_finish is even for")
print("  EVERY integer t_finish, so an odd finish is legal. Check:")
odd_ok = all(report(t)["t_int_even"] for t in range(1, 60))
print(f"  t_int even for every integer t_finish in 1..59: {odd_ok}")

print()
print("ADR 0010 shipped values reproduced from the layer sum:")
r15 = report(15)
print(f"  t_int   = 120 + 2*15 = {r15['t_int']}   (ADR 0010 says 150) "
      f"{'OK' if r15['t_int'] == 150 else 'MISMATCH'}")
print(f"  t_party = 250 + 2*15 = {r15['t_party']}   (ADR 0010 says 280) "
      f"{'OK' if r15['t_party'] == 280 else 'MISMATCH'}")
print(f"  residue = -150 mod 250 = {r15['residue_class_mod_250']}   "
      f"(ADR 0010 says 100) {'OK' if r15['residue_class_mod_250'] == 100 else 'MISMATCH'}")
