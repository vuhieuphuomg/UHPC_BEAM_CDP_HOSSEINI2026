"""
Stress-strain curve plots for CDP tables.
Outputs PNG files using matplotlib.
"""
import os

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    _HAS_MPL = True
except ImportError:
    _HAS_MPL = False


def _check_mpl():
    if not _HAS_MPL:
        raise ImportError("matplotlib not available; install with: pip install matplotlib")


def plot_compression(rows, batch_id, model_id, fc_mpa, ecp, out_path):
    """
    Plot stress (MPa) vs inelastic strain for compression hardening table.
    Colour-codes rows by tag: DERIVED=blue, ADOPTED=orange, REPORTED=red,
    APPROXIMATED=purple.
    """
    _check_mpl()
    tag_colors = {
        "DERIVED": "steelblue",
        "ADOPTED": "darkorange",
        "REPORTED": "firebrick",
    }
    default_color = "mediumpurple"  # APPROXIMATED / other

    x = [float(r["inelastic_strain"]) for r in rows]
    y = [float(r["stress_mpa"]) for r in rows]
    tags = [r.get("tag", "") for r in rows]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(x, y, color="gray", lw=1.0, zorder=1)
    seen_tags = set()
    for xi, yi, tag in zip(x, y, tags):
        base_tag = "APPROXIMATED" if tag.startswith("APPROX") else tag
        color = tag_colors.get(base_tag, default_color)
        label = base_tag if base_tag not in seen_tags else None
        ax.scatter([xi], [yi], color=color, s=18, zorder=2, label=label)
        seen_tags.add(base_tag)

    ax.axvline(0, color="k", lw=0.5, ls="--")
    ax.set_xlabel("Inelastic strain (–)", fontsize=10)
    ax.set_ylabel("Compressive stress (MPa)", fontsize=10)
    ax.set_title(
        f"Compression — Batch {batch_id} / {model_id}\n"
        f"f'c={fc_mpa} MPa, εcp={ecp:.4f}",
        fontsize=10,
    )
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_raw_compression_curve(curves_dict, batch_id, model_id, fc_mpa, ecp, out_path):
    """
    Diagnostic plot for BLOCKED compression models (C3, C4).
    Shows raw σ–ε_total (top) and εin = ε − σ/Ec (bottom) for each labeled curve.
    curves_dict: {label_str: list_of_dicts} where each dict has
      eps_total, sigma_mpa, eps_in, branch.
    NOT labeled as Abaqus-ready; clearly marked as raw source curves.
    """
    _check_mpl()
    colors = ["steelblue", "darkorange", "seagreen", "firebrick", "mediumpurple"]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8), sharex=False, constrained_layout=True)

    for ci, (label, pts) in enumerate(curves_dict.items()):
        c = colors[ci % len(colors)]
        eps_asc = [p["eps_total"] for p in pts if p["branch"] == "ascending"]
        sig_asc = [p["sigma_mpa"] for p in pts if p["branch"] == "ascending"]
        ein_asc = [p["eps_in"]    for p in pts if p["branch"] == "ascending"]
        eps_all = [p["eps_total"] for p in pts]
        sig_all = [p["sigma_mpa"] for p in pts]
        ein_all = [p["eps_in"]    for p in pts]
        ax1.plot(eps_all, sig_all, color=c, lw=1.5, label=label, marker="o", ms=2)
        ax2.plot(eps_all, ein_all, color=c, lw=1.5, label=label, marker="o", ms=2)
        # Shade ascending region with εin < 0
        neg_eps = [e for e, i in zip(eps_asc, ein_asc) if i < 0]
        neg_ein = [i for i in ein_asc if i < 0]
        if neg_eps:
            ax2.fill_between(neg_eps, neg_ein, 0.0, alpha=0.12, color=c)

    ax1.axhline(fc_mpa, color="gray", lw=0.8, ls="--", alpha=0.7, label=f"f'c={fc_mpa} MPa (reported)")
    ax1.axvline(ecp, color="gray", lw=0.8, ls=":", alpha=0.7, label=f"εcp={ecp:.4f} (reported)")
    ax2.axhline(0, color="k", lw=1.0)
    ax2.axvline(ecp, color="gray", lw=0.8, ls=":", alpha=0.7)

    ax1.set_ylabel("Compressive stress (MPa)", fontsize=10)
    ax1.set_title(
        f"RAW σ–ε — Batch {batch_id} / {model_id}  [NOT Abaqus CDP]\n"
        f"f'c={fc_mpa} MPa, εcp={ecp:.4f} (REPORTED)",
        fontsize=10,
    )
    ax1.legend(fontsize=7)
    ax1.grid(True, alpha=0.3)

    ax2.set_xlabel("Total strain ε (–)", fontsize=10)
    ax2.set_ylabel("εin = ε − σ/Ec (–)", fontsize=10)
    ax2.set_title("Inelastic strain profile  [shaded = CDP-blocked region (εin < 0)]", fontsize=9)
    ax2.legend(fontsize=7)
    ax2.grid(True, alpha=0.3)

    _dir = os.path.dirname(out_path)
    if _dir:
        os.makedirs(_dir, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_tension(rows, batch_id, model_id, ft_cr, et_cr, ft_loc, et_loc, out_path):
    """
    Plot stress (MPa) vs cracking strain for tension hardening table.
    """
    _check_mpl()
    tag_colors = {
        "DERIVED": "steelblue",
        "REPORTED": "firebrick",
    }
    default_color = "mediumpurple"

    x = [float(r["cracking_strain"]) for r in rows]
    y = [float(r["stress_mpa"]) for r in rows]
    tags = [r.get("tag", "") for r in rows]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(x, y, color="gray", lw=1.0, zorder=1)
    seen_tags = set()
    for xi, yi, tag in zip(x, y, tags):
        color = tag_colors.get(tag, default_color)
        label = tag if tag not in seen_tags else None
        ax.scatter([xi], [yi], color=color, s=18, zorder=2, label=label)
        seen_tags.add(tag)

    ax.axvline(0, color="k", lw=0.5, ls="--")
    ax.set_xlabel("Cracking strain (–)", fontsize=10)
    ax.set_ylabel("Tensile stress (MPa)", fontsize=10)
    ax.set_title(
        f"Tension hardening — Batch {batch_id} / {model_id}\n"
        f"ft,cr={ft_cr} MPa, ft,loc={ft_loc} MPa",
        fontsize=10,
    )
    ax.annotate(
        "SOFTENING BRANCH\nREVIEW_REQUIRED\n(no σ-w data in paper)",
        xy=(max(x), max(y)),
        xytext=(max(x) * 0.5 + 0.0001, max(y) * 0.8),
        fontsize=7, color="gray",
        arrowprops=dict(arrowstyle="->", color="gray", lw=0.8),
    )
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
