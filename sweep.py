import numpy as np
import matplotlib.pyplot as plt

# ---------- Same assembly as stackup.py ----------

BORE_NOMINAL = 44.20
BASE_BORE_TOL = 0.15

parts = [
    ("Bearing A", 12.00, 0.05),
    ("Spacer",    20.00, 0.10),
    ("Bearing B", 12.00, 0.05),
]

GAP_MIN = 0.05
GAP_MAX = 0.40

TRIALS = 200000   # more trials than before, so the curves come out smooth


def fail_rate(bore_tol, part_tols):
    """Simulate TRIALS assemblies and return the percent that fall out of spec."""
    bore = np.random.normal(BORE_NOMINAL, bore_tol / 3, TRIALS)

    stack = np.zeros(TRIALS)
    for (name, nominal, _), tol in zip(parts, part_tols):
        stack += np.random.normal(nominal, tol / 3, TRIALS)

    gap = bore - stack
    return 100 * np.mean((gap < GAP_MIN) | (gap > GAP_MAX))


# ---------- Baseline ----------

base_part_tols = [p[2] for p in parts]
names = ["Housing bore"] + [p[0] for p in parts]
base_tols = [BASE_BORE_TOL] + base_part_tols

baseline = fail_rate(BASE_BORE_TOL, base_part_tols)
print(f"Baseline failure rate: {baseline:.2f} %\n")

# ---------- Sweep each tolerance one at a time ----------

# Scale factor: 0.25 = four times tighter, 2.0 = twice as loose.
# Every line passes through 1.0, so they're directly comparable.
scale_range = np.linspace(0.25, 2.0, 20)

plt.figure(figsize=(8, 5))

for i, name in enumerate(names):
    rates = []
    for s in scale_range:
        t = base_tols[i] * s
        bore_tol = BASE_BORE_TOL
        part_tols = list(base_part_tols)

        if i == 0:
            bore_tol = t          # sweeping the bore
        else:
            part_tols[i - 1] = t  # sweeping one of the parts

        rates.append(fail_rate(bore_tol, part_tols))

    plt.plot(scale_range, rates, marker="o", markersize=3, label=name)

    # What happens if we halve this one tolerance?
    halved = base_tols[i] / 2
    bore_tol = BASE_BORE_TOL
    part_tols = list(base_part_tols)
    if i == 0:
        bore_tol = halved
    else:
        part_tols[i - 1] = halved

    print(f"{name:14s} {base_tols[i]:.3f} -> {halved:.3f} mm "
          f"gives {fail_rate(bore_tol, part_tols):.2f} % "
          f"(from {baseline:.2f} %)")

plt.axhline(baseline, color="#777777", linestyle=":", linewidth=1)
plt.text(0.26, baseline, " current design", color="#555555",
         fontsize=9, va="bottom")

plt.xlabel("Tolerance, relative to current design (1.0 = as-is)")
plt.ylabel("Assemblies out of spec (%)")
plt.title("Which tolerance actually drives the scrap rate?")
plt.legend()
plt.tight_layout()
plt.savefig("tolerance_sweep.png", dpi=150)
plt.show()