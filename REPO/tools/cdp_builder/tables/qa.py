"""
QA checks for CDP tables.

Reuses existing cdp_table_qa.validate() for compression (syntactic + plastic strain).
Adds equivalent tension hardening checks.
"""
import math
import sys
import os

# Allow running from repo root
_repo_root = os.path.join(os.path.dirname(__file__), "..", "..", "..")
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from tools.cdp_table_qa import validate as _validate_compression_rows


def qa_compression(rows, Ec_mpa):
    """
    Returns list of error strings (empty = pass).
    Wraps cdp_table_qa.validate() which checks:
      - first eps_in = 0
      - sigma > 0, eps_in >= 0, strict monotone
      - damage in [0,1) if present
      - plastic strain >= 0 and non-decreasing if damage present
    """
    # cdp_table_qa expects rows with string values (from CSV DictReader)
    # Our rows have numeric values — convert for compatibility
    str_rows = [
        {k: str(v) for k, v in row.items()} for row in rows
    ]
    return _validate_compression_rows(str_rows, Ec_mpa)


def qa_tension(rows, Ec_mpa):
    """
    Returns list of error strings (empty = pass).
    Checks:
      - first cracking_strain = 0
      - stress > 0, cracking_strain >= 0, strict monotone
      - total strain = cracking_strain + sigma/Ec >= 0 at each row
    """
    errors = []
    if not rows:
        return ["empty tension table"]
    prev_ck = -float("inf")
    prev_sigma = -float("inf")
    for i, row in enumerate(rows, 1):
        try:
            sigma = float(row["stress_mpa"])
            eps_ck = float(row["cracking_strain"])
        except (KeyError, ValueError) as exc:
            errors.append(f"row {i}: invalid stress/cracking_strain: {exc}")
            continue
        if not (math.isfinite(sigma) and math.isfinite(eps_ck)):
            errors.append(f"row {i}: non-finite value")
            continue
        if i == 1 and abs(eps_ck) > 1e-9:
            errors.append(f"row {i}: first cracking_strain must be 0 (got {eps_ck:.2e})")
        if sigma <= 0:
            errors.append(f"row {i}: stress must be > 0 (got {sigma})")
        if eps_ck < 0:
            errors.append(f"row {i}: cracking_strain < 0 ({eps_ck:.6e})")
        if i > 1 and eps_ck <= prev_ck:
            errors.append(
                f"row {i}: cracking_strain not strictly increasing "
                f"({eps_ck:.6e} <= {prev_ck:.6e})"
            )
        # total strain check
        eps_total = eps_ck + sigma / Ec_mpa
        if eps_total < -1e-8:
            errors.append(f"row {i}: implied total strain < 0 ({eps_total:.6e})")
        prev_ck = eps_ck
        prev_sigma = sigma
    return errors
