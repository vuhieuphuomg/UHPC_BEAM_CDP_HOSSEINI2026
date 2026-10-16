"""
G1 CDP material table runner.

Generates compression and tension hardening tables for all 3 UHPC batches.
Compression models: REF_POPOVICS (reference), C1/C2/C3/C4 (REVIEW_REQUIRED stubs)
Tension models:     REF_BILINEAR (reference), T1/T2 (REVIEW_REQUIRED stubs)

Outputs:
  03_MATERIALS/tables/B{n}_{model}_compression.csv
  03_MATERIALS/tables/B{n}_{model}_tension.csv
  03_MATERIALS/plots/B{n}_{model}_compression.png
  03_MATERIALS/plots/B{n}_{model}_tension.png
  03_MATERIALS/G1_MATERIAL_REPORT.md

Run from project root:
  python REPO/tools/cdp_builder/runner.py
or with explicit root:
  python REPO/tools/cdp_builder/runner.py --project-root <path>
"""

import argparse
import os
import sys
import datetime

# ------------------------------------------------------------------
# Path setup — allow running from any directory
# ------------------------------------------------------------------
_this_dir = os.path.dirname(os.path.abspath(__file__))
# REPO/tools/cdp_builder/ → go up two levels to REPO/, then one more to REPO/tools/
_tools_dir = os.path.normpath(os.path.join(_this_dir, ".."))  # REPO/tools/
_repo_root = os.path.normpath(os.path.join(_this_dir, "..", ".."))  # REPO/
if _tools_dir not in sys.path:
    sys.path.insert(0, _tools_dir)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from cdp_builder.batch_data import BATCHES, alpha_compression
from cdp_builder.models import (
    PopovicsCompression, BilinearTensionHardening,
    COMPRESSION_MODELS, TENSION_MODELS,
    ModelStatus, ModelNotAvailableError,
)
from cdp_builder.tables import write_compression_csv, write_tension_csv, qa_compression, qa_tension


def _project_root_from_repo(repo_root):
    return os.path.normpath(os.path.join(repo_root, ".."))


def run(project_root):
    tables_dir = os.path.join(project_root, "03_MATERIALS", "tables")
    plots_dir = os.path.join(project_root, "03_MATERIALS", "plots")
    report_path = os.path.join(project_root, "03_MATERIALS", "G1_MATERIAL_REPORT.md")
    os.makedirs(tables_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)

    results = []  # list of result dicts for report

    # ── COMPRESSION ──────────────────────────────────────────────
    comp_model_ids = list(COMPRESSION_MODELS.keys())  # REF_POPOVICS, C1..C4

    for batch_id, bdata in BATCHES.items():
        Ec = bdata["Ec_mpa"]
        for model_id, ModelClass in COMPRESSION_MODELS.items():
            inst = ModelClass(bdata)
            result = {
                "kind": "compression",
                "batch": batch_id,
                "model": model_id,
                "status": inst.STATUS.value,
                "csv": None,
                "plot": None,
                "qa_errors": [],
                "notes": [],
            }

            if inst.STATUS == ModelStatus.REVIEW_REQUIRED:
                result["notes"].append(
                    f"REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE"
                )
                results.append(result)
                continue

            # Special: Popovics degenerate for Batch 2
            alpha, is_degen = alpha_compression(batch_id)
            if is_degen and model_id == "REF_POPOVICS":
                result["notes"].append(
                    f"DEGENERATE: alpha = Ec*ecp/fc = {alpha:.4f} <= 1.0; "
                    "Popovics model invalid for Batch 2. "
                    "Use C1-C4 (REVIEW_REQUIRED) instead."
                )
                result["status"] = "DEGENERATE"
                results.append(result)
                continue

            try:
                rows = inst.generate_table()
            except ModelNotAvailableError as exc:
                result["notes"].append(f"ERROR: {exc}")
                result["status"] = "ERROR"
                results.append(result)
                continue

            # Write CSV
            csv_name = f"B{batch_id}_{model_id}_compression.csv"
            csv_path = os.path.join(tables_dir, csv_name)
            write_compression_csv(rows, csv_path)
            result["csv"] = os.path.relpath(csv_path, project_root)

            # QA
            errors = qa_compression(rows, Ec)
            result["qa_errors"] = errors

            # Plot
            try:
                from cdp_builder.plots import plot_compression
                png_name = f"B{batch_id}_{model_id}_compression.png"
                png_path = os.path.join(plots_dir, png_name)
                plot_compression(
                    rows, batch_id, model_id,
                    bdata["fc_mpa"], bdata["ecp"],
                    png_path,
                )
                result["plot"] = os.path.relpath(png_path, project_root)
            except ImportError:
                result["notes"].append("matplotlib not available; plot skipped")

            # ADOPTED post-peak note
            adopted = [r for r in rows if r.get("tag") == "ADOPTED"]
            if adopted:
                result["notes"].append(
                    f"Post-peak branch ({len(adopted)} pts) is ADOPTED "
                    "(linear descent placeholder — not from source paper). "
                    "Replace at G1 when C1 source equations are available."
                )
            if bdata.get("batch2_peak_clip"):
                result["notes"].append(
                    "CHANGELOG C-001: eps_in,peak clipped from -3.9e-5 → 0 "
                    "(FE approximation, 1.2% deviation, within scatter)."
                )

            results.append(result)

    # ── TENSION ──────────────────────────────────────────────────
    for batch_id, bdata in BATCHES.items():
        Ec = bdata["Ec_mpa"]
        for model_id, ModelClass in TENSION_MODELS.items():
            if model_id == "REF_BILINEAR":
                inst = ModelClass(bdata)
            else:
                inst = ModelClass(bdata)
            result = {
                "kind": "tension",
                "batch": batch_id,
                "model": model_id,
                "status": inst.STATUS.value,
                "csv": None,
                "plot": None,
                "qa_errors": [],
                "notes": [],
            }

            if inst.STATUS == ModelStatus.REVIEW_REQUIRED:
                result["notes"].append(
                    f"REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE"
                )
                results.append(result)
                continue

            try:
                rows = inst.generate_table()
            except ModelNotAvailableError as exc:
                result["notes"].append(f"ERROR: {exc}")
                result["status"] = "ERROR"
                results.append(result)
                continue

            # Softening note
            result["notes"].append(inst.softening_status)

            # Write CSV
            csv_name = f"B{batch_id}_{model_id}_tension.csv"
            csv_path = os.path.join(tables_dir, csv_name)
            write_tension_csv(rows, csv_path)
            result["csv"] = os.path.relpath(csv_path, project_root)

            # QA
            errors = qa_tension(rows, Ec)
            result["qa_errors"] = errors

            # Plot
            try:
                from cdp_builder.plots import plot_tension
                png_name = f"B{batch_id}_{model_id}_tension.png"
                png_path = os.path.join(plots_dir, png_name)
                plot_tension(
                    rows, batch_id, model_id,
                    bdata["ft_cr_mpa"], bdata["et_cr"],
                    bdata["ft_loc_mpa"], bdata["et_loc"],
                    png_path,
                )
                result["plot"] = os.path.relpath(png_path, project_root)
            except ImportError:
                result["notes"].append("matplotlib not available; plot skipped")

            results.append(result)

    # ── WRITE REPORT ─────────────────────────────────────────────
    _write_report(results, report_path, project_root)

    # ── CONSOLE SUMMARY ──────────────────────────────────────────
    n_pass = sum(1 for r in results if not r["qa_errors"] and r["csv"])
    n_review = sum(1 for r in results if r["status"] == "REVIEW_REQUIRED")
    n_degen = sum(1 for r in results if r["status"] == "DEGENERATE")
    n_err = sum(1 for r in results if r["status"] == "ERROR")
    n_qa_fail = sum(1 for r in results if r["qa_errors"])
    print(f"\nG1 runner complete: {len(results)} entries")
    print(f"  PASS (CSV written, QA clean): {n_pass}")
    print(f"  REVIEW_REQUIRED (stubs):      {n_review}")
    print(f"  DEGENERATE (Popovics/Batch2): {n_degen}")
    print(f"  QA errors:                    {n_qa_fail}")
    print(f"  ERROR:                        {n_err}")
    print(f"\nReport: {report_path}")
    return 0 if n_qa_fail == 0 and n_err == 0 else 1


def _write_report(results, report_path, project_root):
    today = datetime.date.today().isoformat()
    lines = [
        "# G1 Material Table Report",
        "",
        f"**Generated:** {today}  ",
        f"**Gate:** G1_MATERIAL_TABLE_VALID — HOLD (pending source papers for C1-C4, T1-T2)  ",
        "**solver_authorized:** false  ",
        "",
        "---",
        "",
        "## Summary",
        "",
    ]

    # Count by status
    all_status = {}
    for r in results:
        k = r["status"]
        all_status[k] = all_status.get(k, 0) + 1
    for k, v in sorted(all_status.items()):
        lines.append(f"- **{k}:** {v}")
    lines.append("")

    lines += [
        "## Compression tables",
        "",
        "| Batch | Model | Status | CSV | QA | Notes |",
        "|-------|-------|--------|-----|----|-------|",
    ]
    for r in results:
        if r["kind"] != "compression":
            continue
        qa_str = "PASS" if not r["qa_errors"] else "FAIL: " + "; ".join(r["qa_errors"][:2])
        csv_str = f"`{r['csv']}`" if r["csv"] else "—"
        notes = "; ".join(r["notes"][:2]) if r["notes"] else "—"
        lines.append(
            f"| {r['batch']} | {r['model']} | {r['status']} | {csv_str} | {qa_str} | {notes} |"
        )

    lines += [
        "",
        "## Tension tables",
        "",
        "| Batch | Model | Status | CSV | QA | Notes |",
        "|-------|-------|--------|-----|----|-------|",
    ]
    for r in results:
        if r["kind"] != "tension":
            continue
        qa_str = "PASS" if not r["qa_errors"] else "FAIL: " + "; ".join(r["qa_errors"][:2])
        csv_str = f"`{r['csv']}`" if r["csv"] else "—"
        notes = "; ".join(r["notes"][:1]) if r["notes"] else "—"
        lines.append(
            f"| {r['batch']} | {r['model']} | {r['status']} | {csv_str} | {qa_str} | {notes} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Blockers / REVIEW_REQUIRED items",
        "",
        "The following source papers are required to build G1-compliant tables.",
        "Add PDFs to `01_SOURCES/02_SECONDARY_REFERENCE/` and implement equations.",
        "",
        "| Model | Paper | Required for |",
        "|-------|-------|-------------|",
        "| C1 | Graybeal (FHWA) + Fakeh et al. (2025) | Compression Batch 1,2,3 |",
        "| C2 | Zhao et al. (2013) | Compression Batch 1,2,3 |",
        "| C3 | Wang et al. (2016) | Compression Batch 1,2,3 |",
        "| C4 | Yan (2010) | Compression Batch 1,2,3 |",
        "| T1 | Tian et al. (2023) + Fakeh et al. (2025) | Tension Batch 1,2,3 |",
        "| T2 | Zhao et al. (2013) | Tension Batch 1,2,3 |",
        "",
        "**Batch 2 Popovics degeneracy:** alpha = Ec·εcp/f'c = 47300×0.0032/153.2 = 0.988 < 1.",
        "C1-C4 (nonlinear ascending) required for Batch 2 compression.",
        "CHANGELOG C-001: peak eps_in clipped 0 (FE approximation) — does NOT validate C1 curve.",
        "",
        "**Softening:** post-localization σ-w data not in Hosseini 2026.",
        "Tension tables contain hardening branch only. Softening REVIEW_REQUIRED.",
        "",
        "---",
        "",
        "## G1 gate conditions",
        "",
        "G1=PASS requires ALL of:",
        "1. Source papers for C1-C4, T1-T2 loaded and equations verified",
        "2. All 18 tables (3 batches × 6 models) generate with QA PASS",
        "3. All eps_in ≥ 0, non-decreasing (Batch 2 C1 must be checked explicitly)",
        "4. Softening branch (or explicit decision to use no-softening) documented",
        "5. This report updated with PASS verdict by project engineer",
        "",
        "**G1 gate is currently HOLD.**",
    ]

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    p = argparse.ArgumentParser(description="Generate G1 CDP material tables.")
    p.add_argument(
        "--project-root",
        default=_project_root_from_repo(_repo_root),
        help="Project root directory (default: parent of REPO/)",
    )
    args = p.parse_args()
    sys.exit(run(args.project_root))


if __name__ == "__main__":
    main()
