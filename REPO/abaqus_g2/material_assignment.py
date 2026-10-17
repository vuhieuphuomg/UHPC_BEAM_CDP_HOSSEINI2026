"""
material_assignment.py — Read G1 CDP tables and assign materials in Abaqus 2022 CAE.

NOT_TESTED_IN_ABAQUS: requires `abaqus cae noGUI script=...` to verify.

Material naming convention:
  UHPC_C{compression_model}_T{tension_model}_B{batch_id}
  Example: UHPC_C1_T2_B3 — C1 compression, T2 tension, Batch 3 data.

G1 CSV tables location:
  03_MATERIALS/tables/B{n}_{MODEL}_compression.csv
  03_MATERIALS/tables/B{n}_{MODEL}_tension.csv

CDP parameters (fixed for all materials — Hosseini-independent):
  Dilation angle ψ = 36° (typical UHPC range 30–40°; NEEDS_EXPERT_REVIEW)
  Eccentricity  ε = 0.1
  fb0/fc0       = 1.16
  K             = 0.667 (2/3)
  Viscosity     = 0.0 (no viscous regularization at G2 preparation stage)

NEEDS_EXPERT_REVIEW: CDP dilation angle not calibrated from Hosseini data.
  Must be set by engineer before solver run.
"""

import os
import csv

try:
    from abaqus import mdb
    from abaqusConstants import (
        ISOTROPIC, ENGINEERING_CONSTANTS,
        INCREMENTAL,
    )
    _IN_ABAQUS = True
except ImportError:
    _IN_ABAQUS = False

# G1 tables root directory (relative to repo root)
_G1_TABLES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "03_MATERIALS", "tables"
)

# CDP plastic parameters — NEEDS_EXPERT_REVIEW for dilation angle
CDP_PLASTIC_PARAMS = {
    "dilation_angle_deg": 36.0,     # NEEDS_EXPERT_REVIEW: typical UHPC 30-40°
    "eccentricity": 0.1,
    "fb0_fc0": 1.16,
    "K": 0.667,
    "viscosity": 0.0,               # no viscous reg at G2 prep stage
}

# Poisson's ratio (assumed elastic isotropic)
POISSON_RATIO = 0.2   # typical UHPC; NEEDS_EXPERT_REVIEW

# MMFX rebar properties (elastic-perfectly-plastic; no hardening curve at G2)
REBAR_STEEL = {
    "Es_mpa": 200000.0,
    "nu": 0.3,
    "fy_mpa": 1379.0,   # MMFX Grade 4100 = 600ksi = ~4137 MPa...
    # NEEDS_EXPERT_REVIEW: Grade 4100 = 4100 ksi? No — MPa.
    # MMFX Grade 4100 (US): fy = 4100 psi × 6.895 = 28.3MPa? That seems wrong.
    # MMFX CFRP rebar Grade 4 (4000 MPa)?
    # Actually "Grade 4100" in Hosseini likely means Grade 4100 MPa yield.
    # NEEDS_EXPERT_REVIEW: exact fy for MMFX Grade 4100 from Hosseini Table 1.
    "tag": "NEEDS_EXPERT_REVIEW: MMFX Grade 4100 fy not confirmed from Hosseini Table 1",
}


def _read_csv_table(filepath):
    """Read a G1 CDP table CSV; return list of row dicts."""
    rows = []
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def _compression_tuples(rows):
    """Convert compression CSV rows to Abaqus (stress, eps_in) tuples."""
    result = []
    for row in rows:
        try:
            s = float(row["stress_mpa"])
            ei = float(row["inelastic_strain"])
            if s > 0:
                result.append((s, ei))
        except (KeyError, ValueError):
            continue
    return result


def _tension_tuples(rows):
    """Convert tension CSV rows to Abaqus (stress, cracking_strain) tuples."""
    result = []
    for row in rows:
        try:
            s = float(row["stress_mpa"])
            ck = float(row["cracking_strain"])
            if s > 0:
                result.append((s, ck))
        except (KeyError, ValueError):
            continue
    return result


def _find_table_file(batch_id, model_id, table_type):
    """
    Find the G1 CSV table file for a given batch/model/type.
    table_type: 'compression' or 'tension'
    Returns filepath or None if not found.
    """
    fname = "B{0}_{1}_{2}.csv".format(batch_id, model_id, table_type)
    fpath = os.path.join(_G1_TABLES_DIR, fname)
    if os.path.isfile(fpath):
        return fpath
    return None


def create_uhpc_material(model, batch_id, comp_model_id, tens_model_id, Ec_mpa):
    """
    Create a CDP UHPC material in the Abaqus model.

    Args:
        model: Abaqus mdb.models[name] object
        batch_id: 1, 2, or 3
        comp_model_id: e.g. 'C1', 'C2', 'C4_ADAPTED_LB'
        tens_model_id: e.g. 'T2'
        Ec_mpa: elastic modulus from batch data

    Returns material name string, or raises if table files not found.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("material_assignment must run inside Abaqus CAE kernel")

    mat_name = "UHPC_{0}_{1}_B{2}".format(comp_model_id, tens_model_id, batch_id)

    # Read G1 CSV tables
    comp_file = _find_table_file(batch_id, comp_model_id, "compression")
    tens_file = _find_table_file(batch_id, tens_model_id, "tension")

    if comp_file is None:
        raise FileNotFoundError(
            "Compression table not found: B{0}_{1}_compression.csv in {2}".format(
                batch_id, comp_model_id, _G1_TABLES_DIR))
    if tens_file is None:
        raise FileNotFoundError(
            "Tension table not found: B{0}_{1}_tension.csv in {2}".format(
                batch_id, tens_model_id, _G1_TABLES_DIR))

    comp_rows = _read_csv_table(comp_file)
    tens_rows = _read_csv_table(tens_file)
    comp_data = _compression_tuples(comp_rows)
    tens_data = _tension_tuples(tens_rows)

    if not comp_data:
        raise ValueError("Empty compression table for B{0} {1}".format(batch_id, comp_model_id))
    if not tens_data:
        raise ValueError("Empty tension table for B{0} {1}".format(batch_id, tens_model_id))

    mat = model.Material(name=mat_name)

    # Elastic
    mat.Elastic(table=((Ec_mpa, POISSON_RATIO),))

    # CDP plastic parameters
    p = CDP_PLASTIC_PARAMS
    mat.ConcreteDamagedPlasticity(
        table=((
            p["dilation_angle_deg"],
            p["eccentricity"],
            p["fb0_fc0"],
            p["K"],
            p["viscosity"],
        ),)
    )

    # Compression hardening table: (stress, eps_in)
    mat.ConcreteCompressionHardening(table=tuple(comp_data))

    # Tension stiffening table: (stress, cracking_strain), type=STRAIN (default)
    mat.ConcreteTensionStiffening(table=tuple(tens_data))

    return mat_name


def create_rebar_material(model, mat_name="MMFX_REBAR"):
    """
    Create elastic-perfectly-plastic rebar material.
    NEEDS_EXPERT_REVIEW: fy not confirmed.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("material_assignment must run inside Abaqus CAE kernel")

    mat = model.Material(name=mat_name)
    mat.Elastic(table=((REBAR_STEEL["Es_mpa"], REBAR_STEEL["nu"]),))
    # Plastic: (yield_stress, plastic_strain) — EP at G2, no hardening
    mat.Plastic(table=((REBAR_STEEL["fy_mpa"], 0.0),))
    return mat_name


def assign_section_to_part(model, assembly, part_name, instance_name,
                            mat_name, section_name="SEC_UHPC_BEAM"):
    """
    Create homogeneous solid section and assign to entire beam part.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("material_assignment must run inside Abaqus CAE kernel")

    model.HomogeneousSolidSection(
        name=section_name,
        material=mat_name,
        thickness=None,
    )
    region = assembly.instances[instance_name].cells
    assembly.instances[instance_name].SectionAssignment(
        region=region,
        sectionName=section_name,
    )
