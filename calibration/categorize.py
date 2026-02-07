"""
Exploit Categorization by Atomic Primitive

Maps DeFi exploit technique descriptions to the four atomic primitive classes
defined in the paper. This is the keyword-matching methodology described in
Section 5.1 (Data).

Usage:
    python categorize.py                # Categorize exploits from CSV
    python categorize.py --summary      # Print category summary
"""

import argparse
import csv
import os
from collections import Counter
from typing import Dict, Tuple

# Keyword-to-primitive mapping (from paper Section 5.1)
PRIMITIVE_KEYWORDS: Dict[str, list] = {
    "CONTRACT": [
        "reentrancy", "access control", "logic error", "flash loan",
        "flashloan", "overflow", "underflow", "rounding", "protocol logic",
        "smart contract", "infinite mint", "integer", "input validation",
        "front-end", "uninitialized", "delegate", "self-destruct",
        "constructor", "signature", "replay", "compiler", "language",
    ],
    "OPERATIONAL": [
        "key compromise", "private key", "bridge", "frontend", "dns",
        "infrastructure", "social engineering", "insider", "supply chain",
        "compromised", "phishing", "stolen key", "hot wallet", "cold wallet",
        "internal", "employee", "credential",
    ],
    "ORACLE": [
        "oracle manipulation", "price feed", "stale price", "twap",
        "oracle failure", "price oracle", "oracle", "price manipulation",
    ],
    "GOVERNANCE": [
        "rug pull", "rugpull", "admin key", "malicious upgrade",
        "governance attack", "backdoor", "owner",
    ],
}


def categorize_exploit(technique: str, target_type: str = "") -> str:
    """Assign a single exploit to its root-cause primitive class.

    Args:
        technique: Free-text technique description from DeFiLlama
        target_type: Optional target type field

    Returns:
        One of: CONTRACT, OPERATIONAL, ORACLE, GOVERNANCE, UNCATEGORIZED
    """
    text = f"{technique} {target_type}".lower()

    # Check GOVERNANCE first (rug pulls are distinctive)
    for kw in PRIMITIVE_KEYWORDS["GOVERNANCE"]:
        if kw in text:
            return "GOVERNANCE"

    # ORACLE before CONTRACT (oracle manipulation is specific)
    for kw in PRIMITIVE_KEYWORDS["ORACLE"]:
        if kw in text:
            return "ORACLE"

    # OPERATIONAL (key compromise, bridge)
    for kw in PRIMITIVE_KEYWORDS["OPERATIONAL"]:
        if kw in text:
            return "OPERATIONAL"

    # CONTRACT (default for code-level exploits)
    for kw in PRIMITIVE_KEYWORDS["CONTRACT"]:
        if kw in text:
            return "CONTRACT"

    # Fallback: most uncategorized exploits are contract-level
    return "CONTRACT"


def categorize_dataset(csv_path: str, raw_mode: bool = False) -> list:
    """Categorize all exploits in a CSV file.

    The provided dataset (data/defi_exploits.csv) is already filtered.
    If processing raw DeFiLlama API output, use raw_mode=True to apply:
        1. De minimis: exclude exploits < $100K
        2. Deduplication: by (name_lower + date), keep higher loss amount
        3. CeFi exclusion: remove pure centralized exchange hacks

    Args:
        csv_path: Path to DeFiLlama-format exploit CSV
        raw_mode: If True, apply all three filters (for raw API data).
                  If False (default), only categorize (dataset already cleaned).

    Returns:
        List of dicts with added 'primitive' field
    """
    # CeFi keywords — centralized exchange/custodian hacks with no on-chain component
    CEFI_KEYWORDS = [
        "centralized exchange", "cefi", "custodian", "mt. gox", "mt gox",
        "bitfinex", "coincheck", "zaif", "cryptopia", "quadrigacx",
    ]

    raw_rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            technique = row.get("technique", row.get("classification", ""))
            target_type = row.get("targetType", row.get("target_type", ""))
            amount = float(row.get("amount", row.get("amount_m", 0)) or 0)

            if raw_mode:
                # Filter 1: De minimis — exclude < $100K
                if "amount_m" in row:
                    if amount < 0.1:
                        continue
                elif amount < 100_000:
                    continue

                # Filter 3: CeFi exclusion
                text = f"{row.get('name', '')} {technique} {target_type}".lower()
                if any(kw in text for kw in CEFI_KEYWORDS):
                    continue

            raw_rows.append(row)

    if raw_mode:
        # Filter 2: Deduplicate by (name_lower + date), keep higher loss
        seen: Dict[str, dict] = {}
        for row in raw_rows:
            name = row.get("name_lower", row.get("name", "")).lower().strip()
            date = row.get("date", "")
            key = f"{name}|{date}"
            amount = float(row.get("amount", row.get("amount_m", 0)) or 0)

            if key in seen:
                existing_amt = float(
                    seen[key].get("amount", seen[key].get("amount_m", 0)) or 0
                )
                if amount > existing_amt:
                    seen[key] = row
            else:
                seen[key] = row
        raw_rows = list(seen.values())

    # Categorize
    results = []
    for row in raw_rows:
        technique = row.get("technique", row.get("classification", ""))
        target_type = row.get("targetType", row.get("target_type", ""))
        primitive = categorize_exploit(technique, target_type)
        row["primitive"] = primitive
        results.append(row)

    return results


def print_summary(results: list) -> None:
    """Print category summary statistics."""
    counts: Counter = Counter()
    losses: Dict[str, float] = {}

    for r in results:
        p = r["primitive"]
        counts[p] += 1
        amt = float(r.get("amount", r.get("amount_m", 0)) or 0)
        if "amount_m" in r:
            amt *= 1e6
        losses[p] = losses.get(p, 0) + amt

    total_n = sum(counts.values())
    total_loss = sum(losses.values())

    print(f"\n{'Primitive':<15} {'Count':>6} {'Share':>7} {'Loss ($M)':>12} {'Loss %':>7}")
    print("-" * 50)
    for p in ["CONTRACT", "OPERATIONAL", "ORACLE", "GOVERNANCE"]:
        n = counts.get(p, 0)
        loss = losses.get(p, 0)
        print(
            f"{p:<15} {n:>6} {n/total_n:>6.1%} "
            f"{loss/1e6:>11.1f} {loss/total_loss:>6.1%}"
        )
    print("-" * 50)
    print(f"{'TOTAL':<15} {total_n:>6} {'':>7} {total_loss/1e6:>11.1f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Categorize DeFi exploits")
    parser.add_argument("--summary", action="store_true", help="Print summary")
    parser.add_argument(
        "--csv",
        default=os.path.join(os.path.dirname(__file__), "..", "data", "defi_exploits.csv"),
        help="Path to exploit CSV",
    )
    args = parser.parse_args()

    results = categorize_dataset(args.csv)

    if args.summary:
        print_summary(results)
    else:
        print(f"Categorized {len(results)} exploits")
        print_summary(results)
