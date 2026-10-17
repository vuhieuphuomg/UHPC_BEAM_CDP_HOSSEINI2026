"""
G1 CDP material table runner.

Generates compression and tension tables for all 3 UHPC batches.
Compression:  REF_POPOVICS (ref), C1/C2 (IMPLEMENTED), C3/C4 (BLOCKED)
Tension:      REF_BILINEAR (ref), T1 (hardening only), T2 (hardening+softening)

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
                    "REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE"
                )
                results.append(result)
                continue

            if inst.STATUS == ModelStatus.BLOCKED:
                result["notes"].append(
                    f"BLOCKED: {getattr(inst, 'BLOCKED_REASON', 'see model docstring')}"
                )
                # Generate raw diagnostic plots if model provides raw curves
                if hasattr(inst, "raw_sigma_eps_curve"):
                    try:
                        from cdp_builder.plots import plot_raw_compression_curve
                        curves = {}
                        if model_id == "C3":
                            an = inst.eps_in_analysis()
                            pct = an["pct_ascending_negative"]
                            pts = inst.raw_sigma_eps_curve()
                            curves[f"Wang (ADAPTED); εin<0: {pct:.0f}% asc"] = pts
                            result["notes"].append(
                                f"εin analysis: α_Wang={an['alpha_wang']:.4f}; "
                                f"η_cross={an['eta_crossover']:.4f}; "
                                f"εin<0 on {pct:.1f}% of ascending; "
                                f"εin_peak={an['eps_in_at_peak']:.2e}; "
                                f"ε0_Wang={an['eps0_wang']:.5f}; ε20={an['eps20_wang']:.5f}"
                            )
                        elif model_id == "C4":
                            an = inst.eps_in_analysis()
                            for aa, ad in zip(inst.ALPHA_A_RANGE, inst.ALPHA_D_RANGE):
                                pts = inst.raw_sigma_eps_curve(alpha_a=aa, alpha_d=ad)
                                pct = an[aa]["pct_ascending_negative"]
                                curves[f"Yan αa={aa} αd={ad}; εin<0: {pct:.0f}% asc"] = pts
                            an_summary = "; ".join(
                                f"αa={aa}: {an[aa]['pct_ascending_negative']:.1f}%"
                                for aa in inst.ALPHA_A_RANGE
                            )
                            result["notes"].append(
                                f"εin<0 on ascending: {an_summary} "
                                f"(k=Ec×εcp/fc={list(an.values())[0]['k']:.4f})"
                            )
                        if curves:
                            png_name = f"B{batch_id}_{model_id}_raw_curve.png"
                            png_path = os.path.join(plots_dir, png_name)
                            plot_raw_compression_curve(
                                curves, batch_id, model_id,
                                bdata["fc_mpa"], bdata["ecp"],
                                png_path,
                            )
                            result["plot"] = os.path.relpath(png_path, project_root)
                    except Exception as exc:
                        result["notes"].append(f"Raw plot error: {exc}")
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
                    "(C1: Fakeh Eq.9 M=7061.5×λf^-0.411 with ASSUMED fiber dims l=13mm df=0.2mm; "
                    "REF_POPOVICS: linear descent placeholder)."
                )
            if bdata.get("batch2_peak_clip"):
                result["notes"].append(
                    "CHANGELOG C-001: eps_in,peak clipped from -3.9e-5 → 0 "
                    "(FE approximation, 1.2% deviation, within scatter)."
                )
            # C4_ADAPTED peak strain deviation
            if hasattr(inst, "peak_strain_deviation"):
                dev = inst.peak_strain_deviation()
                result["notes"].append(
                    f"ADAPTED eps_c0: {dev['eps_c0_model']:.6f} "
                    f"vs ecp_rep={dev['ecp_reported']:.5f} "
                    f"({dev['dev_pct']:+.1f}%); "
                    f"k={dev['k']:.4f}; eps_in_peak={dev['eps_in_at_peak']:.2e}; "
                    f"αa={dev['alpha_a']} αd={dev['alpha_d']} [SECONDARY source]"
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
                    "REVIEW_REQUIRED: source paper not in 01_SOURCES/02_SECONDARY_REFERENCE"
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
            if hasattr(inst, "softening_status"):
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
    n_blocked = sum(1 for r in results if r["status"] == "BLOCKED")
    n_degen = sum(1 for r in results if r["status"] == "DEGENERATE")
    n_err = sum(1 for r in results if r["status"] == "ERROR")
    n_qa_fail = sum(1 for r in results if r["qa_errors"])
    print(f"\nG1 runner complete: {len(results)} entries")
    print(f"  PASS (CSV written, QA clean): {n_pass}")
    print(f"  REVIEW_REQUIRED (stubs):      {n_review}")
    print(f"  BLOCKED (tech/data blocker):  {n_blocked}")
    print(f"  DEGENERATE (Popovics/Batch2): {n_degen}")
    print(f"  QA errors:                    {n_qa_fail}")
    print(f"  ERROR:                        {n_err}")
    try:
        print(f"\nReport: {report_path}")
    except UnicodeEncodeError:
        print("\nReport: [path contains non-ASCII characters; see G1_MATERIAL_REPORT.md]")
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
        "## Blockers",
        "",
        "### BLOCKED models (source equations available; raw σ–ε plots generated; CDP table blocked)",
        "",
        "| Model | Source | Blocker summary | εin<0 on ascending | Resolution |",
        "|-------|--------|-----------------|---------------------|------------|",
        "| C3 | Wang (2016) Adv Mech Eng 8(2) — PRIMARY ✓ | Initial slope 2×fp/ε0 >> Ec (Wang Eq.7 ε0). ε20 from Eq.10-11 resolved. | B1:~96.6%, B2:~93.9%, B3:100% | Expert decision on ascending branch hybrid law |",
        "| C4 | Yan (2010) via Fakeh (2025) Table 3 — SECONDARY | αa∈[1.1,1.138] > k≈0.988–1.091 for all batches. αa/αd are ranges only. | αa=1.1: B1:89.6%, B2:100%, B3:48.9%; αa=1.138: B1:91.9%, B2:100%, B3:78.8% | Yan (2010) original paper + engineering decision |",
        "",
        "### BLOCKED softening (hardening tables generated; post-peak unavailable)",
        "",
        "| Model | Blocker | Resolution required |",
        "|-------|---------|---------------------|",
        "| T1 | εu (ultimate strain at 0.85×ft) not in Hosseini 2026; Tian (2023) paper not in sources | Tian (2023) paper |",
        "",
        "### Mesh-dependent softening (implemented but mesh-dependent)",
        "",
        "| Model | Note |",
        "|-------|------|",
        "| T2 | Zhao σ–εck post-peak implemented; mesh-dependent. Fakeh σ–w conversion available when lc is set. |",
        "",
        "**Batch 2 Popovics degeneracy:** alpha = Ec·εcp/f'c = 47300×0.0032/153.2 = 0.988 < 1.",
        "C1 and C2 implemented for Batch 2. CHANGELOG C-001: peak eps_in clip approved.",
        "",
        "**Fiber dimensions ASSUMED:** l=13mm, df=0.2mm (not in Hosseini 2026).",
        "C1 post-peak slope M and T1 λf-based formulas use ASSUMED fiber dimensions.",
        "Confirm fiber specifications before using C1 post-peak for structural analysis.",
        "",
        "### C4_YAN_EC_ADAPTED — peak strain deviation from reported ecp",
        "",
        "eps_c0_model = αa × fc / Ec (ADAPTED; initial tangent = Ec exactly by construction).  ",
        "Deviation from reported ecp: ratio = αa / k  where k = Ec × ecp / fc.",
        "",
        "| Batch | fc (MPa) | Ec (MPa) | ecp (rep.) | k | αa=1.100: eps_c0 | dev% | αa=1.138: eps_c0 | dev% |",
        "|-------|---------|---------|-----------|---|----------------|------|----------------|------|",
        "| B1 | 152.8 | 46000 | 0.0035 | 1.054 | 0.003652 | +4.3% | 0.003782 | +8.1% |",
        "| B2 | 153.2 | 47300 | 0.0032 | 0.988 | 0.003565 | +11.4% | 0.003687 | +15.2% |",
        "| B3 | 166.4 | 45400 | 0.0040 | 1.091 | 0.004028 | +0.7% | 0.004172 | +4.3% |",
        "",
        "**C3 Wang — excluded from Abaqus FE matrix (theoretical reference only).**  ",
        "Engineering decision 2026-10-17: C3 Wang not compatible with Ec_reported for Abaqus CDP.",
        "Raw σ–ε curves retained for comparison. Requires expert decision before FE inclusion.",
        "",
        "---",
        "",
        "## G1 gate conditions",
        "",
        "G1=PASS requires ALL of:",
        "1. C3/C4 BLOCKED resolved (expert decision on ascending εin + source papers)",
        "2. T1 softening resolved (Tian 2023 paper + εu confirmed)",
        "3. All tables that generate must QA PASS (currently: C1,C2,T1,T2 = 12 tables)",
        "4. Softening decision for T1/T2 documented (σ–w vs σ–εck)",
        "5. Fiber dimensions confirmed or ASSUMED flag escalated",
        "6. This report updated with PASS verdict by project engineer",
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
