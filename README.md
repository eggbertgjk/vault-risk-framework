# Vault Risk Framework

**A Graph-Theoretic Framework for DeFi Vault Risk Decomposition**

Gregory John Komansky | GJKapital Research | January 2026

---

## Overview

This repository contains the supplementary materials for the paper *"A Graph-Theoretic Framework for DeFi Vault Risk Decomposition"*.

The framework represents DeFi vaults as directed acyclic graphs (DAGs) with nodes typed by four atomic primitives (CONTRACT, ORACLE, GOVERNANCE, OPERATIONAL), enabling node-level risk attribution calibrated from 449 documented exploits.

## Contents

```
paper/          LaTeX source for the paper
data/           Categorized exploit dataset (449 exploits, 2016-2026)
calibration/    Base rate estimation scripts
```

## Key Results

| Primitive | Exploits | Losses | Base Rate | Severity |
|-----------|----------|--------|-----------|----------|
| CONTRACT | 292 (65%) | $6.99B | 6.11% | 0.51 |
| OPERATIONAL | 92 (20%) | $7.82B | 1.93% | 0.60 |
| ORACLE | 61 (14%) | $0.69B | 1.28% | 0.51 |
| GOVERNANCE | 3 (0.7%) | $0.19B | 0.06% | 0.58 |

CONTRACT dominates frequency; OPERATIONAL dominates severity.

## Data Source

Exploit data sourced from [DeFiLlama Hacks API](https://defillama.com/hacks), cross-validated against [Rekt News](https://rekt.news) and [SlowMist](https://hacked.slowmist.io/). See `calibration/categorize.py` for the keyword-to-primitive mapping.

## Usage

```bash
# Reproduce base rates from exploit data
python calibration/compute_base_rates.py

# View categorization methodology
python calibration/categorize.py --summary
```

## Citation

```bibtex
@article{komansky2026vault,
  title={A Graph-Theoretic Framework for DeFi Vault Risk Decomposition},
  author={Komansky, Gregory John},
  year={2026},
  note={GJKapital Research}
}
```

## License

CC BY-NC 4.0 (non-commercial use). For commercial licensing, contact gjkomansky@gmail.com.
