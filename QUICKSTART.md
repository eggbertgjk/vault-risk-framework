# Quick Start: Vault Risk Framework

Get up and running in 5 minutes.

---

## 1. Install

```bash
git clone https://github.com/eggbertgjk/vault-risk-framework.git
cd vault-risk-framework
pip install pandas numpy
```

## 2. Compute Base Rates

```bash
python calibration/compute_base_rates.py
```

Output:
```
Loaded 449 exploits

Base rates (N=500, T=9.56 years):

Primitive       n  Rate     bps
────────────────────────────────
CONTRACT        292  6.11%   611.0
OPERATIONAL      92  1.93%   193.0
ORACLE           61  1.28%   128.0
GOVERNANCE        3  0.06%    6.0
```

## 3. Analyze the Data

```python
import pandas as pd
from calibration.categorize import categorize_dataset

df = pd.DataFrame(categorize_dataset("data/defi_exploits.csv"))

# Summary by primitive
print(df["primitive"].value_counts())

# Total losses by primitive
print(df.groupby("primitive")["amount"].sum())

# Over time
df["year"] = pd.to_datetime(df["date"]).dt.year
print(df.groupby(["year", "primitive"]).size())
```

## 4. Estimate Vault Risk

Example: Curve LP + 3CRV yield farming

```python
from functools import reduce
from operator import mul

vault_risk = {
    "contract": 0.061,
    "operational": 0.019,
    "oracle": 0.013,
    "governance": 0.001,
}

# P(fail) = 1 - ∏(1 - p_i)
p_combined = 1 - reduce(mul, [1 - p for p in vault_risk.values()], 1)
print(f"Annual failure probability: {p_combined:.2%}")
# → 9.4% (1 in 11 vaults fail annually)
```

## 5. Run Detailed Example

```bash
python examples/vault_risk_profile.py
```

Compares risk profiles across multiple strategies:
- Curve 3-Pool LP
- Aave Lending
- Risky Yield Farm
- Cross-Chain Strategy

---

## Next Steps

- **Full README:** See [README.md](README.md)
- **Data Details:** See [data/README.md](data/README.md)
- **Examples:** See [examples/vault_risk_profile.py](examples/vault_risk_profile.py)
- **Paper:** See [paper/vault_risk_decomposition.pdf](paper/vault_risk_decomposition.pdf)

