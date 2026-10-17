"""
material_assignment.py — Read G1 CDP tables and assign materials in Abaqus 2022 CAE.

NOT_TESTED_IN_ABAQUS: requires `abaqus cae noGUI script=...` to verify.

Rebar material data — SOURCE: Hosseini 2026 Table 3 (REPORTED, not invented):
  M#10 Ø32.3mm (bottom bars): fy=690 MPa, Es=200,000 MPa
  M#3  Ø9.5mm  (top bars):    fy=684 MPa, Es=196,000 MPa
  NSS stirrups:                fy=463 MPa, Es=208,000 MPa
  HSS stirrups:                fy=684 MPa, Es=196,000 MPa

CDP parameters — NEEDS_EXPERT_REVIEW for dilation angle:
  Dilation angle ψ = 36°  (NEEDS_EXPERT_REVIEW: typical UHPC 30–40°)
  Eccentricity      = 0.1
  fb0/fc0           = 1.16
  K                 = 0.667 (2/3)
  Viscosity         = 0.0  (no viscous regularization at G2 prep stage)
"""

import os
import csv

try:
    from abaqus import mdb
    from abaqusConstants import ISOTROPIC
    _IN_ABAQUS = True
except ImportError:
    _IN_ABAQUS = False

# G1 tables root: abaqus_g2/ → up two levels → PROJECT_ROOT/03_MATERIALS/tables/
# When __file__ is an 8.3 short path (non-ANSI Unicode drive), the launcher sets
# UHPC_G2_DIR env var to the Unicode path so data file resolution still works.
_env_g2 = os.environ.get("UHPC_G2_DIR", "")
if _env_g2:
    _G1_TABLES_DIR = os.path.normpath(os.path.join(
        _env_g2, "..", "03_MATERIALS", "tables"
    ))
else:
    _G1_TABLES_DIR = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "03_MATERIALS", "tables"
    ))
if not os.path.isdir(_G1_TABLES_DIR):
    raise EnvironmentError(
        "G1 tables directory not found: {0}\n"
        "Expected: PROJECT_ROOT/03_MATERIALS/tables/".format(_G1_TABLES_DIR)
    )

# CDP plastic parameters — NEEDS_EXPERT_REVIEW for dilation angle
CDP_PLASTIC_PARAMS = {
    "dilation_angle_deg": 36.0,   # NEEDS_EXPERT_REVIEW: typical UHPC 30-40°
    "eccentricity": 0.1,
    "fb0_fc0": 1.16,
    "K": 0.667,
    "viscosity": 0.0,
}

POISSON_RATIO_UHPC = 0.2    # typical UHPC, NEEDS_EXPERT_REVIEW
POISSON_RATIO_STEEL = 0.3

# Rebar material properties — Hosseini 2026 Table 3 (REPORTED)
REBAR_MATERIALS = {
    "M10_BOTTOM": {
        "name": "STEEL_M10_BOT",
        "Es_mpa": 200000.0,
        "fy_mpa": 690.0,
        "nu": POISSON_RATIO_STEEL,
        "source": "Hosseini 2026 Table 3: M#10 Ø32.3mm MMFX",
    },
    "M3_TOP": {
        "name": "STEEL_M3_TOP",
        "Es_mpa": 196000.0,
        "fy_mpa": 684.0,
        "nu": POISSON_RATIO_STEEL,
        "source": "Hosseini 2026 Table 3: M#3 Ø9.5mm MMFX",
    },
    "NSS_STIRRUP": {
        "name": "STEEL_NSS_STR",
        "Es_mpa": 208000.0,
        "fy_mpa": 463.0,
        "nu": POISSON_RATIO_STEEL,
        "source": "Hosseini 2026 Table 3: NSS stirrups",
    },
    "HSS_STIRRUP": {
        "name": "STEEL_HSS_STR",
        "Es_mpa": 196000.0,
        "fy_mpa": 684.0,
        "nu": POISSON_RATIO_STEEL,
        "source": "Hosseini 2026 Table 3: HSS stirrups",
    },
}


def _read_csv_table(filepath):
    # io.open() uses CreateFileW on Windows Python 2.7 — handles non-ANSI Unicode paths.
    # Open in binary mode so csv.DictReader receives bytes (required in Py2.7).
    import io as _io
    rows = []
    with _io.open(filepath, "rb") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def _compression_tuples(rows):
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
    fname = "B{0}_{1}_{2}.csv".format(batch_id, model_id, table_type)
    fpath = os.path.join(_G1_TABLES_DIR, fname)
    return fpath if os.path.isfile(fpath) else None


def create_uhpc_material(model, batch_id, comp_model_id, tens_model_id, Ec_mpa):
    """
    Create CDP UHPC material from G1 CSV tables.
    Raises FileNotFoundError if G1 tables not found.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("material_assignment must run inside Abaqus CAE kernel")

    mat_name = "UHPC_{0}_{1}_B{2}".format(comp_model_id, tens_model_id, batch_id)

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

    comp_data = _compression_tuples(_read_csv_table(comp_file))
    tens_data = _tension_tuples(_read_csv_table(tens_file))

    if not comp_data:
        raise ValueError("Empty compression table B{0} {1}".format(batch_id, comp_model_id))
    if not tens_data:
        raise ValueError("Empty tension table B{0} {1}".format(batch_id, tens_model_id))

    mat = model.Material(name=mat_name)
    mat.Elastic(table=((Ec_mpa, POISSON_RATIO_UHPC),))

    p = CDP_PLASTIC_PARAMS
    mat.ConcreteDamagedPlasticity(table=((
        p["dilation_angle_deg"],
        p["eccentricity"],
        p["fb0_fc0"],
        p["K"],
        p["viscosity"],
    ),))

    mat.ConcreteCompressionHardening(table=tuple(comp_data))
    # Tension: STRAIN type (mesh-dependent); use sigma-w DISPLACEMENT for production
    mat.ConcreteTensionStiffening(table=tuple(tens_data))

    return mat_name


def create_all_rebar_materials(model):
    """
    Create all 4 rebar materials (M10, M3, NSS, HSS) from Hosseini 2026 Table 3.
    Returns dict {key: material_name_string}.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("material_assignment must run inside Abaqus CAE kernel")

    created = {}
    for key, props in REBAR_MATERIALS.items():
        mat = model.Material(name=props["name"])
        mat.Elastic(table=((props["Es_mpa"], props["nu"]),))
        mat.Plastic(table=((props["fy_mpa"], 0.0),))  # elastic-perfectly-plastic
        created[key] = props["name"]
    return created


def assign_section_to_part(model, part, section_name, mat_name):
    """
    Create HomogeneousSolidSection and assign to ALL cells of the Part.
    Calls SectionAssignment on the Part object, NOT on an assembly instance.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("material_assignment must run inside Abaqus CAE kernel")

    model.HomogeneousSolidSection(
        name=section_name,
        material=mat_name,
        thickness=None,
    )
    # ALL_CELLS set may already exist from geometry_builder.create_geometry_sets()
    if "ALL_CELLS" not in [s for s in part.sets.keys()]:
        part.Set(name="ALL_CELLS", cells=part.cells)
    part.SectionAssignment(
        region=part.sets["ALL_CELLS"],
        sectionName=section_name,
    )


def assign_rebar_section_to_part(model, wire_part, section_name, mat_name, area_mm2):
    """
    Create TrussSection and assign to ALL edges of a wire part.
    Must be called on the wire Part object, NOT on an assembly instance.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("material_assignment must run inside Abaqus CAE kernel")

    model.TrussSection(name=section_name, material=mat_name, area=area_mm2)
    edge_set = wire_part.Set(name="ALL_EDGES", edges=wire_part.edges)
    wire_part.SectionAssignment(region=edge_set, sectionName=section_name)
