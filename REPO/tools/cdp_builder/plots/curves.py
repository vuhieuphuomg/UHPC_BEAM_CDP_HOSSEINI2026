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
