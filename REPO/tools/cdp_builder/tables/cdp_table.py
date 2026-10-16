"""
Write CDP tables to CSV in Abaqus-compatible format.

Compression hardening table columns: stress_mpa, inelastic_strain [, tag]
Tension hardening table columns: stress_mpa, cracking_strain [, tag]

The tag column is for audit traceability; Abaqus reads only the first two columns.
"""

import csv
import os


def write_compression_csv(rows, out_path):
    """
    Write compression hardening rows to CSV.
    rows: list of dicts with keys stress_mpa, inelastic_strain, tag.
    Returns number of rows written.
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fieldnames = ["stress_mpa", "inelastic_strain", "tag"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def write_tension_csv(rows, out_path):
    """
    Write tension hardening rows to CSV.
    rows: list of dicts with keys stress_mpa, cracking_strain, tag.
    Returns number of rows written.
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fieldnames = ["stress_mpa", "cracking_strain", "tag"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)
