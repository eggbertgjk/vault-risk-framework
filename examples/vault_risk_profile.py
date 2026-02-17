#!/usr/bin/env python3
"""
Example: Estimate Risk Profile for DeFi Vaults

This script shows how to use the Vault Risk Framework to estimate
the annual failure probability of different yield strategies.
"""

import sys
import os
from functools import reduce
from operator import mul

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from calibration.compute_base_rates import compute_base_rates
from calibration.categorize import categorize_dataset


def combine_risks(primitives: dict) -> dict:
    """Combine independent primitive risks."""
    p_combined = 1 - reduce(mul, [1 - p for p in primitives.values()], 1)
    
    contributions = {}
    for name, p in primitives.items():
        others = [1 - x for k, x in primitives.items() if k != name]
        marginal = p * reduce(mul, others, 1)
        contributions[name] = marginal / p_combined if p_combined > 0 else 0

    return {
        "combined_risk": p_combined,
        "combined_risk_pct": f"{p_combined*100:.2f}%",
        "odds": f"1 in {int(1/p_combined)}" if p_combined > 0 else "negligible",
        "contributions": contributions,
    }


def main():
    """Run examples for different vault strategies."""

    exploits = categorize_dataset(
        os.path.join(os.path.dirname(__file__), "..", "data", "defi_exploits.csv")
    )
    base_rates = compute_base_rates(exploits, N=500)

    br = {
        "contract": base_rates["CONTRACT"]["base_rate"],
        "operational": base_rates["OPERATIONAL"]["base_rate"],
        "oracle": base_rates["ORACLE"]["base_rate"],
        "governance": base_rates["GOVERNANCE"]["base_rate"],
    }

    print("=" * 70)
    print("VAULT RISK PROFILE EXAMPLES")
    print("=" * 70)
    print(f"\nBase rates from {len(exploits)} documented exploits:\n")
    for p in ["contract", "operational", "oracle", "governance"]:
        print(f"  {p.upper():<15} {br[p]*100:>6.2f}%")

    # Example 1: Curve LP
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Curve 3-Pool LP (5% APY)")
    print("=" * 70)

    curve_lp = {
        "contract": br["contract"],
        "operational": br["operational"],
        "oracle": 0,
        "governance": br["governance"] * 0.5,
    }

    result = combine_risks(curve_lp)
    print(f"\nAnnual Failure Probability: {result['combined_risk_pct']}")
    print(f"Odds: {result['odds']}")

    # Example 2: Aave
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Aave USDC Lending (2% APY)")
    print("=" * 70)

    aave = {
        "contract": br["contract"] * 1.1,
        "operational": br["operational"] * 0.7,
        "oracle": br["oracle"],
        "governance": br["governance"],
    }

    result = combine_risks(aave)
    print(f"\nAnnual Failure Probability: {result['combined_risk_pct']}")
    print(f"Odds: {result['odds']}")

    # Example 3: Risky farm
    print("\n" + "=" * 70)
    print("EXAMPLE 3: New Protocol Yield Farm (25% APY)")
    print("=" * 70)

    risky = {
        "contract": br["contract"] * 2.0,
        "operational": br["operational"] * 1.5,
        "oracle": br["oracle"] * 2.0,
        "governance": br["governance"] * 3.0,
    }

    result = combine_risks(risky)
    print(f"\nAnnual Failure Probability: {result['combined_risk_pct']}")
    print(f"Odds: {result['odds']}")

    print("\n" + "=" * 70)
    print("RISK RANKING")
    print("=" * 70)

    strategies = {
        "Curve 3-Pool": curve_lp,
        "Aave Lending": aave,
        "New Farm": risky,
    }

    results = {name: combine_risks(risk) for name, risk in strategies.items()}
    sorted_by_risk = sorted(results.items(), key=lambda x: x[1]["combined_risk"])
    
    print(f"\n{'Strategy':<20} {'Annual Failure':<15} {'Odds':<20}")
    print("-" * 55)
    for name, result in sorted_by_risk:
        print(f"{name:<20} {result['combined_risk_pct']:<15} {result['odds']:<20}")

    print("\n✅ Framework working! Use these estimates as a starting point for risk analysis.")


if __name__ == "__main__":
    main()
