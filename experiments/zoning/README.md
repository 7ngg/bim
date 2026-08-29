# `experiments/zoning/`

Where a set-versus-set property lives (ticket 30) and the entry sequence
(ticket 43). Findings: `docs/research/zoning.md` — §1–§5b are 30's, **§6 and
D10 are 43's**.

## What is here

| script | costs | writes |
|---|---|---|
| `measure_zoning.py N` | one corpus pass, minutes | `out/zoning.json` |
| `report.py` | seconds | `out/report.txt` |
| `measure_zoning2.py N` | one corpus pass, minutes | `out/zoning2.json` |
| `report2.py` | seconds | `out/report2.txt` |
| `sensitivity.py` | seconds | `out/sensitivity.txt` |
| `entry_order.py` | seconds | stdout |
| `entry_order2.py` | seconds | stdout |
| `entry_depth_vs_transit.py` | seconds | stdout |

The three `entry_*` probes read the JSON above and run **no corpus pass**, so a
new statistic about the entry sequence costs seconds. Same rule as the other
study directories: **if you add a statistic, add its inputs to the `measure_*`
record.**

`zoning.json` and `zoning2.json` are the **same 2 500 dwellings in the same
key-hash order** and join on `k` — that join is what
`entry_depth_vs_transit.py` does, and it is the only way to get a pass-1
quantity and a pass-2 quantity into one table.

This directory imports `experiments/rectangularise/measure_swiss.py` read-only
and edits nothing outside itself.

## Traps

**1. Social transit has three rates and they have three denominators.** Never put
two of them in one sentence.

| rate | denominator | where |
|---|---|---|
| **11.1 %** | per **sleeping Room** (666 / 5 990) | `zoning.md` §2.5, `proposer.md` §6.1 term 3 |
| **18.2 %** | per **dwelling**, all 2 500 | `out/report2.txt` |
| **25.9 %** | per **dwelling holding both** a private and a social Room (454 / 1 756) | `zoning.md` §6.6 |

The 2×2 in §6.6 is on the third denominator, because an inversion is undefined
without both classes present.

**2. The day/night gradient has two rates and only one is a rule's cost.**
§2.2's **16.1 %** is the dwelling's *mean* private hop against its *mean* social
hop. §6.5's **17.4 %** is the *minimum* on each side — what a rule binds, because
a rule binds the nearest offender. Quote 16.1 % for the gradient's shape, 17.4 %
for what asserting it would cost. And do not quote either without **51.0 %**, the
tie mass, which is the fact that actually decided ticket 43.

**3. `dist` is the contact graph, not doors.** BFS over
`measure_swiss.contact_graph` (τ 0.30 m, door run 1.00 m) — *potential*
circulation. That is exactly what `solver-formulation.md` reifies as `door_ij`,
so these hops are the right plane for **a constraint**. They are the wrong plane
for **"how far a person walks"**: contact ⊇ realised doors, so a contact hop
understates the walk. Say which you mean.

**4. §3's private-Room-touches-circulation level is threshold-dominated.** 53.3 %
at the shipped 1.00 m run, 78.4 % at 0.60 m. The direction is real; the level
measures the threshold. No rule rests on it and none should.

**5. The sample is biased toward well-connected dwellings.** 1 206 dropped as
disconnected on the contact graph, plus 144 no entrance door, 144 no private
Room, 126 outside 3–12 Rooms, 6 entry not located. For §2.1 that biases *toward*
fewer sleeping groups, making the ≤ 2 bound a **floor** on true coverage. Its
effect on §6's tie mass is unmeasured.

**6. `entry_order.py`'s R3 carries no information.** "Circulation strictly nearer
than any social Room" reads as a strong 96.8 %, and it is just "the entry Space
is circulation" restated — if the entry is circ, its distance is 0 and every
social Room is at ≥ 1 by construction of the BFS. It is in the table to be
*excluded*, not quoted.
