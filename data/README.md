# Dataset: DeFi Exploits (2016-2026)

**449 documented DeFi exploits, $15.69B in losses, categorized into 4 atomic risk primitives.**

---

## Files

| File | Rows | Description |
|------|------|-------------|
| `defi_exploits.csv` | 449 | Cleaned exploit dataset (2016-2026) |

---

## Columns

| Column | Type | Description |
|--------|------|-------------|
| `date` | Date | Exploit date (YYYY-MM-DD) |
| `name` | String | Protocol/vault name |
| `technique` | String | Exploit technique description |
| `amount` | Float | Loss amount in USD |
| `chain` | List | Blockchain(s) affected |
| `amount_m` | Float | Amount in millions |
| **`primitive`** | String | **Root cause (CONTRACT/OPERATIONAL/ORACLE/GOVERNANCE)** |

---

## Data Cleaning

**Filters Applied:**
1. **De minimis:** Exploits < $100K excluded (noise filtering)
2. **Deduplication:** By (name, date), keep highest loss
3. **CeFi exclusion:** Pure centralized exchange hacks removed (Mt. Gox, etc.)

**Categorization:** Keyword matching on technique + manual QA

---

## Base Rates

| Primitive | Count | Base Rate | Annual Failure Prob. |
|-----------|-------|-----------|---------------------|
| CONTRACT | 292 | 6.11% | 1 in 16 |
| OPERATIONAL | 92 | 1.93% | 1 in 52 |
| ORACLE | 61 | 1.28% | 1 in 78 |
| GOVERNANCE | 3 | 0.06% | 1 in 1,667 |
| **TOTAL** | **449** | **9.38%** | **1 in 11** |

---

## How to Load

```python
import pandas as pd
from calibration.categorize import categorize_dataset

df = pd.DataFrame(categorize_dataset("data/defi_exploits.csv"))

# By primitive
print(df["primitive"].value_counts())

# Total losses
print(df.groupby("primitive")["amount"].sum())
```

---

## Sources

- **DeFiLlama:** https://defillama.com/hacks
- **Rekt News:** https://rekt.news
- **SlowMist:** https://hacked.slowmist.io/

