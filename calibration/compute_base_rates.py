"""
Base Rate Estimation from Exploit Data

Computes annualized failure probability by primitive class using the formula
from the paper (Section 5.2):

    r_p^(0) = n_p / (N * T)

where:
    n_p = number of exploits of type p
    N   = estimated protocol universe size (~500)
    T   = observation period in years (9.56)

Also includes sensitivity analysis for N (Table 6 in paper).

Usage:
    python compute_base_rates.py
    python compute_base_rates.py --N 800
"""

import argparse
import json
import os
import sys

# Add parent to path for categorize import
sys.path.insert(0, os.path.dirname(__file__))
from categorize import categorize_dataset, print_summary


def compute_base_rates(
    results: list,
    N: int = 500,
    T: float = 9.56,
) -> dict:
    """Compute annualized base rates by primitive class.

    Args:
        results: Categorized exploit list from categorize_dataset()
        N: Estimated protocol universe size
        T: Observation period in years

    Returns:
        Dict mapping primitive -> base rate (annual probability)
    """
    from collections import Counter

    counts = Counter(r["primitive"] for r in results)
    rates = {}
    for p in ["CONTRACT", "OPERATIONAL", "ORACLE", "GOVERNANCE"]:
        n_p = counts.get(p, 0)
        rates[p] = {
            "n_exploits": n_p,
            "base_rate": n_p / (N * T),
            "base_rate_pct": f"{n_p / (N * T) * 100:.2f}%",
            "base_rate_bps": round(n_p / (N * T) * 10000, 1),
        }
    return rates


def sensitivity_analysis(results: list, T: float = 9.56) -> None:
    """Print sensitivity table for different values of N (Table 6 in paper)."""
    print(f"\n{'N':>6}  {'CONTRACT':>10}  {'OPER.':>10}  {'ORACLE':>10}  {'GOV.':>10}")
    print("-" * 52)

    for N in [300, 500, 800, 1000]:
        rates = compute_base_rates(results, N=N, T=T)
        label = f"{N}" if N != 500 else f"{N} (base)"
        print(
            f"{label:>10}  "
            f"{rates['CONTRACT']['base_rate']*100:>9.2f}%  "
            f"{rates['OPERATIONAL']['base_rate']*100:>9.2f}%  "
            f"{rates['ORACLE']['base_rate']*100:>9.2f}%  "
            f"{rates['GOVERNANCE']['base_rate']*100:>9.2f}%"
        )

    # Show ratio invariance
    rates_300 = compute_base_rates(results, N=300, T=T)
    rates_1000 = compute_base_rates(results, N=1000, T=T)
    ratio_300 = rates_300["CONTRACT"]["base_rate"] / rates_300["OPERATIONAL"]["base_rate"]
    ratio_1000 = rates_1000["CONTRACT"]["base_rate"] / rates_1000["OPERATIONAL"]["base_rate"]
    print(f"\nCONTRACT/OPERATIONAL ratio: {ratio_300:.2f}x (N=300) = {ratio_1000:.2f}x (N=1000)")
    print("Ratios are invariant to N.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute base rates")
    parser.add_argument("--N", type=int, default=500, help="Protocol universe size")
    parser.add_argument("--sensitivity", action="store_true", help="Run sensitivity analysis")
    parser.add_argument(
        "--csv",
        default=os.path.join(os.path.dirname(__file__), "..", "data", "defi_exploits.csv"),
        help="Path to exploit CSV",
    )
    args = parser.parse_args()

    results = categorize_dataset(args.csv)
    print(f"Loaded {len(results)} exploits")

    rates = compute_base_rates(results, N=args.N)
    print(f"\nBase rates (N={args.N}, T=9.56 years):")
    print(f"\n{'Primitive':<15} {'n':>5} {'Rate':>8} {'bps':>6}")
    print("-" * 38)
    for p in ["CONTRACT", "OPERATIONAL", "ORACLE", "GOVERNANCE"]:
        r = rates[p]
        print(f"{p:<15} {r['n_exploits']:>5} {r['base_rate_pct']:>8} {r['base_rate_bps']:>5.1f}")

    if args.sensitivity:
        sensitivity_analysis(results)

    # Save to JSON
    output = {
        "metadata": {
            "N": args.N,
            "T": 9.56,
            "n_exploits": len(results),
            "source": "DeFiLlama Hacks API",
        },
        "base_rates": {p: rates[p]["base_rate"] for p in rates},
    }
    out_path = os.path.join(os.path.dirname(__file__), "base_rates.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to {out_path}")
