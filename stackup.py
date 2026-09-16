import random
import matplotlib.pyplot as plt

# ---------- The assembly ----------
# A housing bore holds a bearing, a spacer, and a second bearing.
# The leftover gap has to land inside a spec range.

BORE_NOMINAL = 44.20   # depth of the machined bore (mm)
BORE_TOL = 0.15        # machined feature, hardest to hold

# Each part: name, nominal size (mm), tolerance (mm)
parts = [
    ("Bearing A", 12.00, 0.05),   # purchased, tight from the supplier
    ("Spacer",    20.00, 0.10),   # turned in-house
    ("Bearing B", 12.00, 0.05),   # same purchased part
]

GAP_MIN = 0.05   # any tighter and the bearings bind
GAP_MAX = 0.40   # any looser and the shaft floats

# ---------- Classic methods ----------

stack_nominal = sum(p[1] for p in parts)
gap_nominal = BORE_NOMINAL - stack_nominal

worst_tol = BORE_TOL + sum(p[2] for p in parts)
rss_tol = (BORE_TOL ** 2 + sum(p[2] ** 2 for p in parts)) ** 0.5

print(f"Nominal gap:  {gap_nominal:.3f} mm")
print(f"Spec range:   {GAP_MIN:.3f} to {GAP_MAX:.3f} mm")
print()
print(f"Worst case:   {gap_nominal - worst_tol:+.3f} to {gap_nominal + worst_tol:+.3f} mm")
print(f"RSS:          {gap_nominal - rss_tol:+.3f} to {gap_nominal + rss_tol:+.3f} mm")

# ---------- Monte Carlo ----------

TRIALS = 10000
gaps = []          # store every simulated gap so we can plot them

for _ in range(TRIALS):
    # tol/3 assumes the tolerance band covers +/- 3 standard deviations,
    # so about 99.7% of parts land inside it
    bore = random.gauss(BORE_NOMINAL, BORE_TOL / 3)
    stack = sum(random.gauss(nom, tol / 3) for name, nom, tol in parts)
    gaps.append(bore - stack)

too_tight = sum(1 for g in gaps if g < GAP_MIN)
too_loose = sum(1 for g in gaps if g > GAP_MAX)
fails = too_tight + too_loose
fail_rate = 100 * fails / TRIALS

print()
print(f"Monte Carlo ({TRIALS} assemblies)")
print(f"  Too tight:    {too_tight}")
print(f"  Too loose:    {too_loose}")
print(f"  Failure rate: {fail_rate:.2f} %")

# ---------- Chart ----------

plt.figure(figsize=(8, 5))
plt.hist(gaps, bins=60, color="#8fa8a0", edgecolor="white", linewidth=0.5)

plt.axvline(GAP_MIN, color="#a93b2c", linestyle="--", linewidth=2)
plt.axvline(GAP_MAX, color="#a93b2c", linestyle="--", linewidth=2)

plt.xlabel("Assembly gap (mm)")
plt.ylabel("Number of assemblies")
plt.title(f"Simulated gap distribution - {fail_rate:.2f}% out of spec")

plt.text(GAP_MIN, plt.ylim()[1] * 0.95, " bind limit",
         color="#a93b2c", ha="left", va="top", fontsize=9)
plt.text(GAP_MAX, plt.ylim()[1] * 0.95, "float limit ",
         color="#a93b2c", ha="right", va="top", fontsize=9)

plt.tight_layout()
plt.savefig("gap_distribution.png", dpi=150)
plt.show()