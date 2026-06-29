"""
GSN Analytics Engine
- Critical path identification
- Schedule/cost performance indices
- Risk scoring & heatmap data
- Fiber health anomaly detection (KS-Test, PSI)
- Bottleneck detection
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import ks_2samp
import warnings
warnings.filterwarnings("ignore")


# ─── Critical Path ────────────────────────────────────────────────────────────

def compute_critical_path(milestones_df: pd.DataFrame) -> pd.DataFrame:
    """Identify critical path milestones and their float/delay impact."""
    df = milestones_df.copy()
    df["planned_date"] = pd.to_datetime(df["planned_date"])
    df["actual_date"] = pd.to_datetime(df["actual_date"])

    # Float = slack before milestone becomes critical (0 = on critical path)
    df["total_float_days"] = df.apply(
        lambda r: (r["actual_date"] - r["planned_date"]).days if pd.notna(r["actual_date"]) else np.nan, axis=1
    )
    df["is_critical"] = df["is_critical_path"] | (df["total_float_days"].fillna(0) > 14)
    df["delay_impact"] = df["total_float_days"].clip(lower=0)

    # Cascade delay: if a CP milestone is late, downstream shifts
    df = df.sort_values(["project_id", "milestone_idx"])
    df["cascade_delay"] = 0
    for pid, grp in df.groupby("project_id"):
        cumulative = 0
        idxs = grp.index.tolist()
        for i in idxs:
            if df.loc[i, "is_critical"]:
                cumulative += max(0, df.loc[i, "delay_impact"])
            df.loc[i, "cascade_delay"] = cumulative

    return df


# ─── Performance Indices ──────────────────────────────────────────────────────

def compute_earned_value(projects_df: pd.DataFrame, kpi_df: pd.DataFrame) -> pd.DataFrame:
    """Compute EVM metrics: EV, PV, AC, SPI, CPI, EAC, VAC."""
    results = []
    for _, proj in projects_df.iterrows():
        pid = proj["project_id"]
        budget = proj["budget_m_usd"]
        spend = proj["spend_to_date_m_usd"]
        pct = proj["completion_pct"] / 100

        ev = budget * pct                   # Earned Value
        pv = budget * 0.85                  # Planned Value (assume 85% planned by now)
        ac = spend                          # Actual Cost
        spi = round(ev / pv, 3) if pv else 0
        cpi = round(ev / ac, 3) if ac else 0
        eac = round(budget / cpi, 2) if cpi else budget  # Estimate at Completion
        vac = round(budget - eac, 2)        # Variance at Completion

        results.append({
            "project_id": pid,
            "cable_name": proj["cable_name"],
            "budget_m": budget,
            "ev_m": round(ev, 2),
            "pv_m": round(pv, 2),
            "ac_m": round(ac, 2),
            "spi": spi,
            "cpi": cpi,
            "eac_m": eac,
            "vac_m": vac,
            "completion_pct": proj["completion_pct"],
            "status": proj["status"],
            "evm_health": "Green" if spi >= 0.95 and cpi >= 0.95 else ("Yellow" if min(spi, cpi) >= 0.85 else "Red"),
        })
    return pd.DataFrame(results)


# ─── Risk Analysis ────────────────────────────────────────────────────────────

def score_risks(risks_df: pd.DataFrame) -> pd.DataFrame:
    """Compute composite risk scores and prioritize mitigation."""
    df = risks_df.copy()
    df["composite_score"] = df["probability"] * df["impact"]

    # Pareto ranking: top 20% risks drive 80% of exposure
    df = df.sort_values("composite_score", ascending=False)
    df["rank"] = range(1, len(df) + 1)
    total_score = df["composite_score"].sum()
    df["cumulative_pct"] = df["composite_score"].cumsum() / total_score * 100
    df["is_pareto_top20"] = df["cumulative_pct"] <= 80

    # Expected monetary value
    avg_budget = 100  # $M placeholder
    df["emv_m"] = (df["probability"] * df["impact"] * avg_budget).round(2)

    return df


def risk_heatmap_data(risks_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate risk scores into probability × impact grid for heatmap."""
    df = risks_df.copy()
    df["prob_bin"] = pd.cut(df["probability"], bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                            labels=["Very Low", "Low", "Medium", "High", "Very High"])
    df["impact_bin"] = pd.cut(df["impact"], bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                              labels=["Negligible", "Minor", "Moderate", "Major", "Severe"])
    heatmap = df.groupby(["prob_bin", "impact_bin"], observed=True).agg(
        count=("risk_id", "count"),
        avg_score=("composite_score", "mean")
    ).reset_index()
    return heatmap


# ─── Fiber Anomaly Detection ──────────────────────────────────────────────────

def detect_fiber_anomalies(fiber_df: pd.DataFrame) -> pd.DataFrame:
    """
    Statistical anomaly detection on fiber health metrics.
    Uses KS-Test to compare segment distributions vs. baseline.
    Uses PSI (Population Stability Index) to detect feature drift.
    """
    df = fiber_df.copy()

    # Reference distribution: theoretical ideal (from spec)
    ref_attenuation = np.random.normal(0.185, 0.003, 500)
    ref_osnr = np.random.normal(18.5, 0.5, 500)

    anomalies = []
    for cable, grp in df.groupby("cable_name"):
        # KS-Test: attenuation distribution vs. reference
        ks_stat, ks_pval = ks_2samp(grp["attenuation_db_km"].values, ref_attenuation)
        drift_detected = ks_pval < 0.05

        # PSI calculation for OSNR
        psi = _compute_psi(grp["osnr_db"].values, ref_osnr, bins=10)

        anomalies.append({
            "cable_name": cable,
            "ks_statistic": round(ks_stat, 4),
            "ks_pvalue": round(ks_pval, 4),
            "distribution_drift": drift_detected,
            "psi_osnr": round(psi, 4),
            "psi_alert": psi > 0.2,  # PSI > 0.2 = significant shift
            "anomalous_segments": int(grp["anomaly_flag"].sum()),
            "total_segments": len(grp),
            "anomaly_rate_pct": round(grp["anomaly_flag"].mean() * 100, 2),
            "mean_attenuation": round(grp["attenuation_db_km"].mean(), 4),
            "mean_osnr_db": round(grp["osnr_db"].mean(), 2),
            "health_score": round(100 - grp["anomaly_flag"].mean() * 100, 1),
        })

    return pd.DataFrame(anomalies)


def _compute_psi(actual: np.ndarray, expected: np.ndarray, bins: int = 10) -> float:
    """Population Stability Index: measures distribution shift."""
    breaks = np.percentile(expected, np.linspace(0, 100, bins + 1))
    breaks[0] -= 1e-9
    breaks[-1] += 1e-9

    actual_counts = np.histogram(actual, bins=breaks)[0]
    expected_counts = np.histogram(expected, bins=breaks)[0]

    actual_pct = actual_counts / actual_counts.sum()
    expected_pct = expected_counts / expected_counts.sum()

    # Avoid division by zero
    actual_pct = np.where(actual_pct == 0, 0.0001, actual_pct)
    expected_pct = np.where(expected_pct == 0, 0.0001, expected_pct)

    psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
    return float(psi)


# ─── Bottleneck Detection ─────────────────────────────────────────────────────

def identify_bottlenecks(milestones_df: pd.DataFrame, risks_df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify operational bottlenecks by combining:
    - Milestone delay frequency per category
    - Risk score concentration
    """
    cp = milestones_df[milestones_df["is_critical_path"]].copy()
    cp["delay_days"] = cp["delay_days"].fillna(0)

    # Group delays by milestone type
    bottlenecks = cp.groupby("milestone").agg(
        avg_delay=("delay_days", "mean"),
        max_delay=("delay_days", "max"),
        projects_affected=("project_id", "nunique"),
    ).reset_index()

    bottlenecks["bottleneck_score"] = (
        bottlenecks["avg_delay"] * bottlenecks["projects_affected"]
    ).round(1)

    bottlenecks = bottlenecks.sort_values("bottleneck_score", ascending=False)
    bottlenecks["rank"] = range(1, len(bottlenecks) + 1)
    return bottlenecks


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os
    data_dir = "/home/claude/gsn-tpm-project/data"

    projects = pd.read_csv(f"{data_dir}/projects.csv")
    milestones = pd.read_csv(f"{data_dir}/milestones.csv")
    risks = pd.read_csv(f"{data_dir}/risk_log.csv")
    kpis = pd.read_csv(f"{data_dir}/kpi_timeseries.csv")
    fiber = pd.read_csv(f"{data_dir}/fiber_health.csv")

    cp = compute_critical_path(milestones)
    evm = compute_earned_value(projects, kpis)
    risk_scored = score_risks(risks)
    fiber_health = detect_fiber_anomalies(fiber)
    bottlenecks = identify_bottlenecks(cp, risk_scored)

    cp.to_csv(f"{data_dir}/critical_path.csv", index=False)
    evm.to_csv(f"{data_dir}/evm_metrics.csv", index=False)
    risk_scored.to_csv(f"{data_dir}/risks_scored.csv", index=False)
    fiber_health.to_csv(f"{data_dir}/fiber_anomalies.csv", index=False)
    bottlenecks.to_csv(f"{data_dir}/bottlenecks.csv", index=False)

    print("✅ Analytics complete")
    print(f"\nEVM Summary:\n{evm[['cable_name','spi','cpi','evm_health']].to_string(index=False)}")
    print(f"\nFiber Health:\n{fiber_health[['cable_name','health_score','anomaly_rate_pct','psi_alert']].to_string(index=False)}")
    print(f"\nTop Bottlenecks:\n{bottlenecks.head(5)[['milestone','avg_delay','bottleneck_score']].to_string(index=False)}")
