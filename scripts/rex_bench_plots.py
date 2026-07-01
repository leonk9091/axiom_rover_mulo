"""Generate MULO-REX expected bench plots.

These plots are not test evidence. They are deterministic reference envelopes
for planning the first GX50 bench run and validating report plumbing.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "enterprise" / "figures"
DATA_DIR = ROOT / "docs" / "enterprise" / "datasets"


def build_expected_profile() -> pd.DataFrame:
    t = np.arange(0, 601, 1)
    target_w = np.piecewise(
        t,
        [t < 60, (t >= 60) & (t < 180), (t >= 180) & (t < 360), (t >= 360) & (t < 540), t >= 540],
        [0, 100, 300, 500, 700],
    ).astype(float)
    rpm = np.where(target_w <= 0, 3000, 4300 + target_w * 3.1)
    rpm = np.minimum(rpm, 7200)
    vdc = np.where(target_w <= 0, 35, 42 + target_w * 0.025)
    vdc = np.minimum(vdc, 65)
    bus_v = 27.2 + np.minimum(target_w, 700) / 700 * 1.4
    charge_a = target_w / np.maximum(bus_v, 1.0)
    rectifier_c = 30 + (target_w / 700) ** 1.4 * 55
    buck_c = 32 + (target_w / 700) ** 1.2 * 50
    exhaust_zone_c = 45 + (target_w / 700) ** 1.1 * 120
    throttle = np.clip(target_w / 700, 0, 1)
    return pd.DataFrame(
        {
            "time_s": t,
            "target_w": target_w,
            "rpm": rpm,
            "dc_link_voltage_v": vdc,
            "bus_voltage_v": bus_v,
            "charge_current_a": charge_a,
            "rectifier_temp_c": rectifier_c,
            "buck_temp_c": buck_c,
            "exhaust_zone_temp_c": exhaust_zone_c,
            "throttle_request": throttle,
        }
    )


def save_plot(df: pd.DataFrame, filename: str, title: str, columns: list[str], ylabel: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 5), dpi=140)
    for col in columns:
        ax.plot(df["time_s"], df[col], label=col)
    ax.set_title(title)
    ax.set_xlabel("time_s")
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(OUT_DIR / filename)
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df = build_expected_profile()
    df.to_csv(DATA_DIR / "rex_expected_bench_profile.csv", index=False)
    save_plot(df, "rex_expected_power_current.png", "MULO-REX Expected Power and Charge Current", ["target_w", "charge_current_a"], "W / A")
    save_plot(df, "rex_expected_rpm_vdc.png", "MULO-REX Expected RPM and DC Link", ["rpm", "dc_link_voltage_v"], "rpm / V")
    save_plot(df, "rex_expected_thermal.png", "MULO-REX Expected Thermal Envelope", ["rectifier_temp_c", "buck_temp_c", "exhaust_zone_temp_c"], "deg C")


if __name__ == "__main__":
    main()
