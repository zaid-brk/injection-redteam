"""Phase 6 — turn results/*.json into the before/after ASR bar chart for the README.

Reads results/baseline.json and results/defended.json (run run_defenses.py first),
draws per-category baseline-vs-defended bars, prints the headline numbers, saves the PNG.
"""
import json
import matplotlib
matplotlib.use("Agg")  # no display needed, just write the file
import matplotlib.pyplot as plt
from collections import defaultdict


def cat_asr(path):
    """Attack success rate per category from a results file."""
    data = json.load(open(path))
    d = defaultdict(lambda: [0, 0])
    for r in data:
        d[r["category"]][0] += r["attack_succeeded"]
        d[r["category"]][1] += 1
    return {c: s / t for c, (s, t) in d.items()}


def overall(path):
    data = json.load(open(path))
    return sum(r["attack_succeeded"] for r in data) / len(data)


if __name__ == "__main__":
    base = cat_asr("results/baseline.json")
    defended = cat_asr("results/defended.json")
    cats = list(base)

    plt.figure(figsize=(10, 5))
    plt.bar([i - 0.2 for i in range(len(cats))], [base[c] for c in cats], 0.4, label="No defense")
    plt.bar([i + 0.2 for i in range(len(cats))], [defended.get(c, 0) for c in cats], 0.4, label="Defended")
    plt.xticks(range(len(cats)), cats, rotation=45, ha="right")
    plt.ylabel("Attack Success Rate")
    plt.title(f"Prompt-injection ASR: {overall('results/baseline.json'):.0%} baseline "
              f"-> {overall('results/defended.json'):.0%} defended")
    plt.legend()
    plt.tight_layout()
    plt.savefig("results/asr_chart.png", dpi=150)
    print(f"Baseline ASR:  {overall('results/baseline.json'):.0%}")
    print(f"Defended ASR:  {overall('results/defended.json'):.0%}")
    print("Wrote results/asr_chart.png")
