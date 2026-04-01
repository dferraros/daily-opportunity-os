"""
SubagentStart hook (matcher: geo-scout-.*): pre-loads Venezuela/LATAM context
for geo scout agents before they run.

Reads config/regions.yaml and prints a context summary to stdout.
Claude injects this output as pre-context for the subagent.
Exits 0 always (never blocks).
"""
import sys
import os
from datetime import date
from pathlib import Path


def find_project_root() -> Path:
    candidates = [
        Path("C:/Users/ferra/OneDrive/Desktop/Projects/.worktrees/daily-opportunity-os"),
        Path(__file__).resolve().parent.parent,
    ]
    for c in candidates:
        if (c / "config").exists():
            return c
    return Path(__file__).resolve().parent.parent


def load_yaml_simple(path: Path) -> dict:
    """
    Minimal YAML parser for flat/nested key: value structures.
    Handles the regions.yaml format without requiring PyYAML.
    Falls back to empty dict on any failure.
    """
    try:
        import yaml  # type: ignore
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        pass

    # Fallback: return empty so defaults are used
    return {}


def main():
    root = find_project_root()
    today_str = date.today().isoformat()

    # Defaults — used when YAML parse fails or fields are missing
    ve_wtp = "0.25x US"
    ve_saas = "$3-15/mo"
    ve_payments = "Zelle/USDT/Binance P2P"
    ve_distrib = "WhatsApp-first"
    latam_wtp = "0.40x US"
    latam_payments = "PSE(CO)/PIX(BR)/OXXO(MX)/Zelle(VE)"
    latam_whatsapp = "90%"
    wedge_categories = (
        "payments_and_collections, smb_software_informal_operators, "
        "commerce_trust_layers, remittances_and_diaspora_finance"
    )

    regions_path = root / "config" / "regions.yaml"
    if regions_path.exists():
        data = load_yaml_simple(regions_path)
        regions = data.get("regions", {})

        ve = regions.get("venezuela", {})
        if ve:
            ve_wtp = f"{ve.get('wtp_multiplier', 0.25)}x US"
            ve_saas = ve.get("saas_price_range", ve_saas)
            rails = ve.get("dominant_payment_rails", [])
            if rails:
                ve_payments = "/".join(rails[:3])  # top 3
            ve_distrib = f"{ve.get('distribution_primary', 'WhatsApp')}-first"

        latam = regions.get("latam", {})
        if latam:
            latam_wtp = f"{latam.get('wtp_multiplier_vs_us', 0.40)}x US"
            wp_pct = latam.get("whatsapp_penetration", 0.90)
            latam_whatsapp = f"{int(float(wp_pct) * 100)}%"
            preferred = latam.get("preferred_payments", {})
            if preferred:
                parts = []
                for country_code, methods in preferred.items():
                    if methods:
                        country_abbr = country_code[:2].upper()
                        parts.append(f"{methods[0]}({country_abbr})")
                if parts:
                    latam_payments = "/".join(parts[:5])

    print("GEO CONTEXT PRELOADED:")
    print(
        f"Venezuela: WTP {ve_wtp} | SaaS {ve_saas} | "
        f"Payments: {ve_payments} | Distribution: {ve_distrib}"
    )
    print(
        f"LATAM: WTP {latam_wtp} | Payments: {latam_payments} | "
        f"WhatsApp {latam_whatsapp} penetration"
    )
    print(f"Active wedge categories: {wedge_categories}")
    print(f"Current date: {today_str}")

    sys.exit(0)


if __name__ == "__main__":
    main()
