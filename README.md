# Vault Risk Framework

> **Quantify DeFi Vault Risk with Graph-Theoretic Decomposition**
>
> A rigorous framework for attributing DeFi vault failures to root-cause primitives. Calibrated on 449 documented exploits ($15.69B in losses). Used to decompose risk for yield vaults, concentrated positions, and cross-chain strategies.

---

## The Problem

**DeFi vault losses hit $15.69B+ in 2016-2026.** But most risk analysis is vague:

> "High yield? Probably risky."
> "Audited? Probably safe."

This is not actionable. When a vault gets exploited, what actually failed?
- Smart contract bug?
- Key compromise?
- Price oracle manipulation?
- Governance attack?

**Each root cause has different base rates, different insurance costs, and different mitigation strategies.** But nobody quantifies them.

---

## The Solution

**This framework decomposes DeFi vault risk into four atomic primitives:**

```
┌─ CONTRACT        (65% of exploits, 6.11% annual base rate)
│  └─ Reentrancy, flash loans, logic errors, overflows, etc.
│
├─ OPERATIONAL     (20% of exploits, 1.93% annual base rate)
│  └─ Key compromise, bridge hacks, infrastructure attacks
│
├─ ORACLE          (14% of exploits, 1.28% annual base rate)
│  └─ Price feed manipulation, stale oracle, TWAP attacks
│
└─ GOVERNANCE      (0.7% of exploits, 0.06% annual base rate)
   └─ Rug pulls, malicious upgrades, backdoors
```

**Base rates calibrated from 449 real exploits** (DeFiLlama + Rekt News + SlowMist).

---

## Key Results

### By Primitive

| Primitive | Exploits | Losses | Base Rate | Annual Failure Prob. |
|-----------|----------|--------|-----------|---------------------|
| **CONTRACT** | 292 (65%) | $6.99B | 6.11% | 1 in 16 vaults/year |
| **OPERATIONAL** | 92 (20%) | $7.82B | 1.93% | 1 in 52 vaults/year |
| **ORACLE** | 61 (14%) | $0.69B | 1.28% | 1 in 78 vaults/year |
| **GOVERNANCE** | 3 (0.7%) | $0.19B | 0.06% | 1 in 1,667 vaults/year |
| **TOTAL** | 449 | $15.69B | **9.38%** | **1 in 11 vaults/year** |

### Severity ($ per incident)

| Primitive | Avg Loss | Median Loss | Max Loss | Severity Index |
|-----------|----------|-------------|----------|-----------------|
| OPERATIONAL | $85.0M | $3.2M | $440M | 0.60 |
| GOVERNANCE | $63.3M | $5.0M | $170M | 0.58 |
| CONTRACT | $23.9M | $0.8M | $1,400M | 0.51 |
| ORACLE | $11.3M | $1.2M | $125M | 0.51 |

**Insight:** CONTRACT fails most often (65%). OPERATIONAL causes highest average loss ($85M per incident).

---

## What You Can Do

### 1. Get Started

```bash
git clone https://github.com/eggbertgjk/vault-risk-framework.git
cd vault-risk-framework
pip install pandas numpy
python calibration/compute_base_rates.py
```

### 2. Estimate Vault Risk

```python
from calibration.categorize import categorize_dataset
from calibration.compute_base_rates import compute_base_rates

exploits = categorize_dataset("data/defi_exploits.csv")
base_rates = compute_base_rates(exploits)

# Print results
for p in ["CONTRACT", "OPERATIONAL", "ORACLE", "GOVERNANCE"]:
    br = base_rates[p]["base_rate"]
    print(f"{p}: {br*100:.2f}% annual failure rate")
```

### 3. Run Examples

```bash
python examples/vault_risk_profile.py
```

---

## Paper & Technical Details

**"A Graph-Theoretic Framework for DeFi Vault Risk Decomposition"**
- Author: Gregory John Komansky
- Source: GJKapital Research
- Date: January 2026
- Paper: `paper/vault_risk_decomposition.pdf` (45 pages)

### Graph-Theoretic Model

Each vault is a directed acyclic graph (DAG):
- **Nodes** = atomic operations (swap, lend, oracle read, vote)
- **Node types** = {CONTRACT, OPERATIONAL, ORACLE, GOVERNANCE}
- **Edges** = data dependencies

Failure modes are attributed to the highest-risk node type in the DAG.

---

## Data Source

**449 documented DeFi exploits (2016-2026, $15.69B in losses)**

- Primary: DeFiLlama Hacks API
- Validation: Rekt News, SlowMist
- Methodology: Keyword-matching to primitives with manual QA

See `data/README.md` for full data dictionary and filtering methodology.

---

## Repository Structure

```
├── README.md                    # This file
├── QUICKSTART.md                # 5-min setup
├── calibration/
│   ├── categorize.py            # Exploit categorization
│   ├── compute_base_rates.py    # Base rate estimation
│   └── base_rates.json          # Pre-computed results
├── data/
│   ├── defi_exploits.csv        # 449 exploits (cleaned)
│   └── README.md                # Data dictionary
├── examples/
│   └── vault_risk_profile.py    # Example usage
└── paper/
    └── vault_risk_decomposition.pdf  # Full paper
```

---

## Quick Links

- **Getting Started:** See [QUICKSTART.md](QUICKSTART.md)
- **Data Dictionary:** See [data/README.md](data/README.md)
- **Examples:** See [examples/vault_risk_profile.py](examples/vault_risk_profile.py)
- **Full Paper:** See [paper/vault_risk_decomposition.pdf](paper/vault_risk_decomposition.pdf)

---

## FAQ

**Q: What's the base rate for my vault?**

A: Depends on your strategy's primitive composition:
- Simple Curve LP → ~5% annual failure risk
- Aave lending → ~6-7% annual failure risk
- New protocol yield farm → 15-25% annual failure risk
- Cross-chain strategy → add +3-5% for bridge risk

See `examples/vault_risk_profile.py` for detailed walkthrough.

**Q: How confident are these base rates?**

A: Fairly confident for mature categories:
- CONTRACT: 95% CI ±0.35% (292 exploits)
- OPERATIONAL: 95% CI ±0.20% (92 exploits)
- ORACLE: 95% CI ±0.16% (61 exploits)
- GOVERNANCE: 95% CI ±0.06% (3 exploits)

See paper Section 5.3 for uncertainty quantification.

**Q: Can I use this for insurance pricing?**

A: Yes, as a starting point. Apply adjustments:
- Audited by top firm? Reduce CONTRACT risk by ~50%
- Multi-sig governance? Reduce GOVERNANCE risk to ~0%
- Bridged assets? Add OPERATIONAL risk premium
- Historical uptime track record? Reduce by (1 - uptime)

**Q: Commercial license?**

A: Dataset and code are CC BY-NC 4.0. For commercial use, contact **gjkomansky@gmail.com**.

---

## Citation

```bibtex
@article{komansky2026vault,
  title={A Graph-Theoretic Framework for DeFi Vault Risk Decomposition},
  author={Komansky, Gregory John},
  year={2026},
  url={https://github.com/eggbertgjk/vault-risk-framework}
}
```

---

**Maintained by:** Gregory John Komansky (@eggbertgjk)
**Last updated:** February 2026
