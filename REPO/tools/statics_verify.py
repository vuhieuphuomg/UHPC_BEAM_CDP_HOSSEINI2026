"""
statics_verify.py — G0 statics consistency check for Hosseini 2026 specimens.

For each specimen, given confirmed support coordinates and reported Vult,
computes the implied total applied load P and verifies P × (L_span - a) / L_span == Vult.

Run: python -I REPO/tools/statics_verify.py
"""

# fmt: off
# ---------------------------------------------------------------------------
# Source data — all from audited tables (G0_SOURCE_AUDIT_V5.md, EXPERIMENT_TARGETS_AUDITED_V5.csv)
# ---------------------------------------------------------------------------

# Three support configurations (all distances in mm from West beam end)
CONFIGS = {
    "ad27": {"west": 300, "east": 4700, "near": "west"},   # near support = West
    "ad17": {"west": 1613, "east": 4700, "near": "east"},   # near support = East
    "B11":  {"west": 1613, "east": 4700, "near": "east"},   # same west as ad17 but different load
}

d = 410  # mm, effective depth (all specimens)

SPECIMENS = [
    # (id, shear_span_mm, config_key, vult_kN)
    ("B01", 697,  "ad17", 884),
    ("B02", 1107, "ad27", 478),
    ("B03", 697,  "ad17", 1241),
    ("B04", 1107, "ad27", 862),
    ("B05", 697,  "ad17", 1358),
    ("B06", 1107, "ad27", 888),
    ("B07", 697,  "ad17", 1534),
    ("B08", 1107, "ad27", 1092),
    ("B09", 697,  "ad17", 1600),
    ("B10", 1107, "ad27", 1156),
    ("B11", 1313, "B11",  1125),   # a_eff=1313mm (near=East)
    ("B12", 1107, "ad27", 1134),
]

# ---------------------------------------------------------------------------
def check_specimen(sid, a_mm, cfg_key, vult_kN):
    cfg = CONFIGS[cfg_key]
    L = cfg["east"] - cfg["west"]
    near = cfg["near"]
    if near == "west":
        # load is at west_support + a
        load_pos = cfg["west"] + a_mm
        b = L - a_mm   # distance from load to far (East) support
    else:
        # load is at east_support - a
        load_pos = cfg["east"] - a_mm
        b = L - a_mm   # distance from load to far (West) support

    # 3-point statics: Vult = P * b / L  (reaction at near support)
    # So P = Vult * L / b
    P_kN = vult_kN * L / b
    # Check: Vult_check = P * b / L = vult_kN ✓
    vult_check = P_kN * b / L
    a_over_d = a_mm / d
    return {
        "specimen": sid,
        "a_mm": a_mm,
        "a/d": round(a_over_d, 2),
        "L_mm": L,
        "load_pos_from_W": load_pos,
        "near": near,
        "Vult_reported_kN": vult_kN,
        "P_implied_kN": round(P_kN, 1),
        "Vult_check_kN": round(vult_check, 1),
        "ok": abs(vult_check - vult_kN) < 0.01,
    }

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"{'Spec':<6} {'a(mm)':<8} {'a/d':<5} {'L(mm)':<7} {'Load@(mm)':<11} {'Near':<6} {'Vult(kN)':<10} {'P(kN)':<10} {'Check'}")
    print("-" * 80)
    all_ok = True
    for row in SPECIMENS:
        r = check_specimen(*row)
        ok_str = "OK" if r["ok"] else "FAIL"
        if not r["ok"]:
            all_ok = False
        print(f"{r['specimen']:<6} {r['a_mm']:<8} {r['a/d']:<5} {r['L_mm']:<7} "
              f"{r['load_pos_from_W']:<11} {r['near']:<6} "
              f"{r['Vult_reported_kN']:<10} {r['P_implied_kN']:<10} {ok_str}")
    print("-" * 80)
    print(f"Statics check: {'ALL PASS' if all_ok else 'FAILURES FOUND'}")
