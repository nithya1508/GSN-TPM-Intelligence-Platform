"""
Synthetic Data Generator for Global Submarine Networks (GSN) TPM Dashboard
Generates realistic subsea cable project data for analytics and visualization.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
import os

np.random.seed(42)
random.seed(42)

# === CONFIG ===
CABLE_SYSTEMS = [
    {"name": "EURASIA-1", "route": "UK–France–Egypt–India", "length_km": 14200, "capacity_tbps": 240, "region": "EMEA"},
    {"name": "AFRICA-WEST", "route": "Portugal–Morocco–Nigeria–Angola", "length_km": 8700, "capacity_tbps": 180, "region": "EMEA"},
    {"name": "MEDLINK-2", "route": "Spain–Italy–Cyprus–Israel", "length_km": 5400, "capacity_tbps": 120, "region": "EMEA"},
    {"name": "NORDIC-CONNECT", "route": "UK–Norway–Denmark–Finland", "length_km": 3200, "capacity_tbps": 96, "region": "EMEA"},
    {"name": "INDO-PACIFIC-3", "route": "India–Singapore–Japan–Korea", "length_km": 17800, "capacity_tbps": 360, "region": "APAC"},
]

MILESTONES = [
    "Survey Complete", "Environmental Impact Assessment", "Marine License Granted",
    "Cable Manufacturing Start", "Cable Ship Mobilization", "Shore Landing – Point A",
    "Burial Complete – Segment 1", "Burial Complete – Segment 2", "Repeater Deployment",
    "Shore Landing – Point B", "Power Feed Equipment Install", "Wet Testing",
    "System Acceptance Test", "Ready for Service (RFS)"
]

RISK_CATEGORIES = ["Weather Delay", "Permitting", "Supplier", "Environmental",
                   "Geopolitical", "Technical", "Cost Overrun", "Schedule Slip"]

REGIONS = ["UK", "France", "Norway", "Egypt", "Nigeria", "India", "Singapore", "Japan"]
SUPPLIERS = ["SubCom", "Alcatel Submarine Networks", "NEC Corporation",
             "HMN Technologies", "Prysmian Group"]


def generate_projects():
    """Generate cable system project records."""
    records = []
    base_date = datetime(2023, 1, 1)
    for i, cable in enumerate(CABLE_SYSTEMS):
        start = base_date + timedelta(days=i * 60)
        duration_days = int(cable["length_km"] / 14200 * 900 + 400)
        planned_end = start + timedelta(days=duration_days)
        delay_days = np.random.choice([0, 0, 15, 30, 45, 90], p=[0.3, 0.2, 0.2, 0.15, 0.1, 0.05])
        actual_end = planned_end + timedelta(days=int(delay_days))
        budget_m = round(cable["length_km"] * 0.08 + np.random.uniform(-5, 10), 1)
        spend_pct = np.random.uniform(0.55, 0.95)
        records.append({
            "project_id": f"GSN-{2024+i:04d}",
            "cable_name": cable["name"],
            "route": cable["route"],
            "region": cable["region"],
            "length_km": cable["length_km"],
            "capacity_tbps": cable["capacity_tbps"],
            "supplier": random.choice(SUPPLIERS),
            "start_date": start.strftime("%Y-%m-%d"),
            "planned_rfs": planned_end.strftime("%Y-%m-%d"),
            "forecast_rfs": actual_end.strftime("%Y-%m-%d"),
            "delay_days": int(delay_days),
            "budget_m_usd": budget_m,
            "spend_to_date_m_usd": round(budget_m * spend_pct, 1),
            "completion_pct": round(spend_pct * 100 + np.random.uniform(-5, 5), 1),
            "status": "On Track" if delay_days == 0 else ("At Risk" if delay_days <= 30 else "Delayed"),
        })
    return pd.DataFrame(records)


def generate_milestones(projects_df):
    """Generate milestone tracking data for each project."""
    records = []
    for _, proj in projects_df.iterrows():
        start = datetime.strptime(proj["start_date"], "%Y-%m-%d")
        n = len(MILESTONES)
        for idx, milestone in enumerate(MILESTONES):
            planned = start + timedelta(days=int((idx / n) * 600 + 10))
            jitter = int(np.random.normal(proj["delay_days"] * (idx / n), 7))
            actual_offset = max(0, jitter)
            actual = planned + timedelta(days=actual_offset) if planned < datetime.now() else None
            status = "Complete" if actual else ("In Progress" if idx == int(proj["completion_pct"] / 7) else "Pending")
            records.append({
                "project_id": proj["project_id"],
                "cable_name": proj["cable_name"],
                "milestone": milestone,
                "milestone_idx": idx,
                "planned_date": planned.strftime("%Y-%m-%d"),
                "actual_date": actual.strftime("%Y-%m-%d") if actual else None,
                "delay_days": actual_offset if actual else 0,
                "status": status,
                "is_critical_path": idx in [0, 2, 4, 5, 9, 12, 13],
            })
    return pd.DataFrame(records)


def generate_risk_log(projects_df):
    """Generate RAID risk log."""
    records = []
    risk_id = 1
    for _, proj in projects_df.iterrows():
        n_risks = random.randint(4, 9)
        for _ in range(n_risks):
            category = random.choice(RISK_CATEGORIES)
            prob = round(np.random.uniform(0.1, 0.8), 2)
            impact = round(np.random.uniform(0.2, 0.9), 2)
            score = round(prob * impact, 3)
            records.append({
                "risk_id": f"R-{risk_id:04d}",
                "project_id": proj["project_id"],
                "cable_name": proj["cable_name"],
                "category": category,
                "description": f"{category} risk affecting {proj['cable_name']} deployment",
                "probability": prob,
                "impact": impact,
                "risk_score": score,
                "severity": "Critical" if score > 0.5 else ("High" if score > 0.3 else ("Medium" if score > 0.15 else "Low")),
                "mitigation": f"Contingency plan activated for {category.lower()} scenario",
                "owner": random.choice(["TPM Lead", "Engineering", "Legal", "Procurement"]),
                "status": random.choice(["Open", "Open", "Mitigated", "Closed"]),
                "raised_date": (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 400))).strftime("%Y-%m-%d"),
            })
            risk_id += 1
    return pd.DataFrame(records)


def generate_kpi_timeseries(projects_df):
    """Generate monthly KPI time series data."""
    records = []
    months = pd.date_range("2024-01-01", periods=18, freq="MS")
    for _, proj in projects_df.iterrows():
        base_completion = 0
        for month in months:
            increment = np.random.uniform(3, 9)
            base_completion = min(100, base_completion + increment)
            spi = round(np.random.normal(0.95, 0.08), 3)  # Schedule Performance Index
            cpi = round(np.random.normal(0.97, 0.06), 3)  # Cost Performance Index
            records.append({
                "project_id": proj["project_id"],
                "cable_name": proj["cable_name"],
                "month": month.strftime("%Y-%m"),
                "completion_pct": round(base_completion, 1),
                "spi": max(0.6, min(1.3, spi)),
                "cpi": max(0.6, min(1.3, cpi)),
                "budget_utilization_pct": round(base_completion * np.random.uniform(0.9, 1.1), 1),
                "open_risks": random.randint(2, 12),
                "milestones_completed": int(base_completion / 7.5),
                "milestones_delayed": random.randint(0, 3),
            })
    return pd.DataFrame(records)


def generate_fiber_health():
    """Generate simulated fiber optic health metrics per cable segment."""
    records = []
    for cable in CABLE_SYSTEMS:
        n_segments = cable["length_km"] // 500
        for seg in range(int(n_segments)):
            depth = np.random.uniform(200, 6000)
            attenuation = round(np.random.normal(0.185, 0.005), 4)  # dB/km
            osnr = round(np.random.normal(18.5, 1.2), 2)  # dB
            anomaly = np.random.random() < 0.04
            records.append({
                "cable_name": cable["name"],
                "segment_id": f"{cable['name']}-SEG{seg+1:03d}",
                "segment_start_km": seg * 500,
                "segment_end_km": (seg + 1) * 500,
                "depth_m": round(depth, 0),
                "attenuation_db_km": attenuation + (0.02 if anomaly else 0),
                "osnr_db": osnr - (2.5 if anomaly else 0),
                "bit_error_rate": float(f"{np.random.uniform(1,9):.1f}e-{random.randint(10,13)}"),
                "anomaly_flag": anomaly,
                "last_test_date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
            })
    return pd.DataFrame(records)


if __name__ == "__main__":
    out = "/home/claude/gsn-tpm-project/data"
    os.makedirs(out, exist_ok=True)

    projects = generate_projects()
    milestones = generate_milestones(projects)
    risks = generate_risk_log(projects)
    kpis = generate_kpi_timeseries(projects)
    fiber = generate_fiber_health()

    projects.to_csv(f"{out}/projects.csv", index=False)
    milestones.to_csv(f"{out}/milestones.csv", index=False)
    risks.to_csv(f"{out}/risk_log.csv", index=False)
    kpis.to_csv(f"{out}/kpi_timeseries.csv", index=False)
    fiber.to_csv(f"{out}/fiber_health.csv", index=False)

    print(f"✅ Generated {len(projects)} projects, {len(milestones)} milestones, "
          f"{len(risks)} risks, {len(kpis)} KPI rows, {len(fiber)} fiber segments")
