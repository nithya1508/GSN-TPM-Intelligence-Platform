"""
GSN TPM Intelligence Dashboard
Streamlit app for Google Global Submarine Networks project analytics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

st.set_page_config(
    page_title="GSN TPM Intelligence Dashboard",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Data Loading ─────────────────────────────────────────────────────────────
DATA = os.path.join(os.path.dirname(__file__), '..', 'data')

@st.cache_data
def load_data():
    return {
        "projects":   pd.read_csv(f"{DATA}/projects.csv"),
        "milestones": pd.read_csv(f"{DATA}/milestones.csv"),
        "risks":      pd.read_csv(f"{DATA}/risks_scored.csv"),
        "kpis":       pd.read_csv(f"{DATA}/kpi_timeseries.csv"),
        "fiber":      pd.read_csv(f"{DATA}/fiber_health.csv"),
        "evm":        pd.read_csv(f"{DATA}/evm_metrics.csv"),
        "cp":         pd.read_csv(f"{DATA}/critical_path.csv"),
        "fiber_anom": pd.read_csv(f"{DATA}/fiber_anomalies.csv"),
        "bottlenecks":pd.read_csv(f"{DATA}/bottlenecks.csv"),
    }

d = load_data()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.image("https://www.gstatic.com/images/branding/googlelogo/svg/googlelogo_clr_74x24px.svg", width=120)
st.sidebar.title("GSN TPM Dashboard")
st.sidebar.markdown("**Global Submarine Networks**")
st.sidebar.divider()

selected_cable = st.sidebar.multiselect(
    "Cable System", d["projects"]["cable_name"].tolist(),
    default=d["projects"]["cable_name"].tolist()
)
page = st.sidebar.radio("View", [
    "📊 Portfolio Overview",
    "🗺️ Critical Path",
    "⚠️ Risk Intelligence",
    "📡 Fiber Health",
    "📈 EVM & Forecasting",
])
st.sidebar.divider()
st.sidebar.caption("Nithyashree Babu · GSN TPM Portfolio · 2025")

# Filter
proj_f = d["projects"][d["projects"]["cable_name"].isin(selected_cable)]
evm_f  = d["evm"][d["evm"]["cable_name"].isin(selected_cable)]
kpi_f  = d["kpis"][d["kpis"]["cable_name"].isin(selected_cable)]
risk_f = d["risks"][d["risks"]["cable_name"].isin(selected_cable)]
cp_f   = d["cp"][d["cp"]["cable_name"].isin(selected_cable)]

# ─── COLORS ──────────────────────────────────────────────────────────────────
STATUS_COLORS = {"On Track": "#34a853", "At Risk": "#fbbc04", "Delayed": "#ea4335"}
GOOGLE_PALETTE = ["#4285f4", "#34a853", "#fbbc04", "#ea4335", "#9c27b0"]

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1: Portfolio Overview
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📊 Portfolio Overview":
    st.title("🌊 GSN Portfolio Overview")
    st.caption("Real-time program health across global submarine cable deployments")

    # KPI Cards
    total_budget = proj_f["budget_m_usd"].sum()
    total_spend  = proj_f["spend_to_date_m_usd"].sum()
    avg_complete = proj_f["completion_pct"].mean()
    on_track     = (proj_f["status"] == "On Track").sum()
    total_delay  = proj_f["delay_days"].sum()
    total_km     = proj_f["length_km"].sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("💰 Total Budget", f"${total_budget:.0f}M", delta=f"-${total_spend:.0f}M spent")
    c2.metric("✅ Avg Completion", f"{avg_complete:.1f}%", delta=f"{on_track}/{len(proj_f)} on track")
    c3.metric("📅 Portfolio Delay", f"{total_delay} days", delta=f"{total_delay/len(proj_f):.0f} avg/project", delta_color="inverse")
    c4.metric("🌐 Cable Deployed", f"{total_km:,} km")
    c5.metric("⚠️ Open Risks", str(len(risk_f[risk_f["status"] == "Open"])))

    st.divider()

    col1, col2 = st.columns([3, 2])
    with col1:
        # Gantt-style project timeline
        st.subheader("Project Timeline (Gantt)")
        gantt_data = []
        for _, r in proj_f.iterrows():
            gantt_data.append(dict(Task=r["cable_name"], Start=r["start_date"],
                                   Finish=r["planned_rfs"], Status="Planned", Color="#4285f4"))
            if r["delay_days"] > 0:
                gantt_data.append(dict(Task=r["cable_name"], Start=r["planned_rfs"],
                                       Finish=r["forecast_rfs"], Status="Delay", Color="#ea4335"))
        gantt_df = pd.DataFrame(gantt_data)
        fig = px.timeline(gantt_df, x_start="Start", x_end="Finish", y="Task",
                          color="Status", color_discrete_map={"Planned": "#4285f4", "Delay": "#ea4335"},
                          height=300)
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Status Distribution")
        status_counts = proj_f["status"].value_counts().reset_index()
        fig2 = px.pie(status_counts, values="count", names="status",
                      color="status", color_discrete_map=STATUS_COLORS,
                      height=300, hole=0.45)
        fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig2, use_container_width=True)

    # Budget vs Spend
    st.subheader("Budget vs. Spend by Project")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name="Budget", x=proj_f["cable_name"], y=proj_f["budget_m_usd"],
                          marker_color="#4285f4"))
    fig3.add_trace(go.Bar(name="Spend", x=proj_f["cable_name"], y=proj_f["spend_to_date_m_usd"],
                          marker_color="#34a853"))
    fig3.update_layout(barmode="group", height=320, margin=dict(l=0, r=0, t=10, b=0),
                       yaxis_title="$M USD")
    st.plotly_chart(fig3, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2: Critical Path
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🗺️ Critical Path":
    st.title("🗺️ Critical Path Intelligence")
    st.caption("Milestone tracking, cascade delay analysis, and bottleneck identification")

    bottlenecks = d["bottlenecks"]
    cp_proj = cp_f[cp_f["is_critical_path"]]

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Milestone Completion by Project")
        milestone_agg = cp_f.groupby(["cable_name", "status"]).size().reset_index(name="count")
        fig = px.bar(milestone_agg, x="cable_name", y="count", color="status",
                     color_discrete_map={"Complete": "#34a853", "In Progress": "#fbbc04", "Pending": "#9aa0a6"},
                     height=360, barmode="stack")
        fig.update_layout(margin=dict(l=0,r=0,t=10,b=0), yaxis_title="Milestones")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top Bottlenecks")
        for _, row in bottlenecks.head(5).iterrows():
            score = row["bottleneck_score"]
            color = "#ea4335" if score > 30 else ("#fbbc04" if score > 10 else "#34a853")
            st.markdown(f"""
            <div style="background:#f8f9fa;border-left:4px solid {color};
                        padding:8px 12px;margin-bottom:8px;border-radius:4px;">
                <b>{row['milestone']}</b><br>
                <small>Avg delay: {row['avg_delay']:.1f}d · Score: {score}</small>
            </div>""", unsafe_allow_html=True)

    st.subheader("Cascade Delay Heatmap (Critical Path Milestones)")
    cp_heat = cp_f[cp_f["is_critical_path"]].pivot_table(
        index="milestone", columns="cable_name", values="cascade_delay", aggfunc="mean"
    ).fillna(0)
    fig2 = px.imshow(cp_heat, color_continuous_scale="RdYlGn_r",
                     labels=dict(color="Cascade Days"), height=420, aspect="auto")
    fig2.update_layout(margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig2, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3: Risk Intelligence
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "⚠️ Risk Intelligence":
    st.title("⚠️ Risk Intelligence")
    st.caption("RAID log · Risk heatmap · Pareto analysis · EMV exposure")

    open_risks  = risk_f[risk_f["status"] == "Open"]
    critical    = risk_f[risk_f["severity"] == "Critical"]
    total_emv   = risk_f["emv_m"].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open Risks", len(open_risks))
    c2.metric("Critical Risks", len(critical))
    c3.metric("EMV Exposure", f"${total_emv:.1f}M")
    c4.metric("Top Category", risk_f.groupby("category")["composite_score"].sum().idxmax())

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Risk Heatmap (Probability × Impact)")
        scatter = risk_f[risk_f["status"] == "Open"]
        fig = px.scatter(scatter, x="probability", y="impact",
                         color="severity", size="composite_score",
                         color_discrete_map={"Critical": "#ea4335", "High": "#fbbc04",
                                             "Medium": "#4285f4", "Low": "#34a853"},
                         hover_data=["cable_name", "category", "description"],
                         height=380)
        # Risk zones
        fig.add_shape(type="rect", x0=0.6, y0=0.6, x1=1, y1=1,
                      fillcolor="rgba(234,67,53,0.1)", line_width=0)
        fig.update_layout(margin=dict(l=0,r=0,t=10,b=0),
                          xaxis_title="Probability", yaxis_title="Impact")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Risk by Category (EMV)")
        cat_emv = risk_f.groupby("category")["emv_m"].sum().sort_values(ascending=False).reset_index()
        fig2 = px.bar(cat_emv, x="emv_m", y="category", orientation="h",
                      color="emv_m", color_continuous_scale="Reds", height=380)
        fig2.update_layout(margin=dict(l=0,r=0,t=10,b=0), xaxis_title="EMV ($M)",
                           coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("RAID Log — Open & Critical")
    display_cols = ["risk_id","cable_name","category","severity","probability","impact",
                    "composite_score","mitigation","owner","status"]
    styled = open_risks[display_cols].sort_values("composite_score", ascending=False)
    st.dataframe(styled, use_container_width=True, hide_index=True,
                 column_config={"composite_score": st.column_config.ProgressColumn(
                     "Risk Score", min_value=0, max_value=1, format="%.2f")})


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4: Fiber Health
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📡 Fiber Health":
    st.title("📡 Fiber Optic Health Monitor")
    st.caption("Statistical anomaly detection using KS-Test & PSI · Real-time segment analysis")

    fa = d["fiber_anom"]
    fiber_raw = d["fiber"][d["fiber"]["cable_name"].isin(selected_cable)]

    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Health Score", f"{fa['health_score'].mean():.1f}%")
    c2.metric("PSI Alerts", str(fa["psi_alert"].sum()), help="PSI > 0.2 = significant distribution shift")
    c3.metric("Anomalous Segments", str(fa["anomalous_segments"].sum()))

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Health Score by Cable")
        fig = px.bar(fa, x="cable_name", y="health_score",
                     color="health_score", color_continuous_scale="RdYlGn",
                     range_color=[70, 100], height=320)
        fig.update_layout(margin=dict(l=0,r=0,t=10,b=0), yaxis_range=[0,105])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("KS-Test & PSI Metrics")
        st.dataframe(fa[["cable_name","ks_statistic","ks_pvalue","psi_osnr",
                          "anomaly_rate_pct","health_score"]].round(3),
                     use_container_width=True, hide_index=True)

    st.subheader("Attenuation Profile — Segment Level")
    if not fiber_raw.empty:
        sel_cable = st.selectbox("Select cable", fiber_raw["cable_name"].unique())
        seg_data = fiber_raw[fiber_raw["cable_name"] == sel_cable].sort_values("segment_start_km")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=seg_data["segment_start_km"], y=seg_data["attenuation_db_km"],
            mode="lines+markers",
            marker=dict(color=seg_data["anomaly_flag"].map({True: "#ea4335", False: "#4285f4"}),
                        size=8),
            line=dict(color="#4285f4", width=1.5),
            name="Attenuation (dB/km)"
        ))
        fig2.add_hline(y=0.195, line_dash="dash", line_color="#ea4335",
                       annotation_text="Alarm threshold (0.195 dB/km)")
        fig2.update_layout(height=340, margin=dict(l=0,r=0,t=10,b=0),
                           xaxis_title="Distance (km)", yaxis_title="Attenuation (dB/km)")
        st.plotly_chart(fig2, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5: EVM & Forecasting
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📈 EVM & Forecasting":
    st.title("📈 Earned Value Management & Forecasting")
    st.caption("SPI · CPI · EAC · VAC · Schedule performance trending")

    col1, col2, col3, col4 = st.columns(4)
    avg_spi = evm_f["spi"].mean()
    avg_cpi = evm_f["cpi"].mean()
    total_vac = evm_f["vac_m"].sum()
    total_eac = evm_f["eac_m"].sum()

    col1.metric("Avg SPI", f"{avg_spi:.3f}", delta="Schedule efficiency",
                delta_color="normal" if avg_spi >= 1 else "inverse")
    col2.metric("Avg CPI", f"{avg_cpi:.3f}", delta="Cost efficiency",
                delta_color="normal" if avg_cpi >= 1 else "inverse")
    col3.metric("Portfolio EAC", f"${total_eac:.0f}M")
    col4.metric("VAC", f"${total_vac:+.1f}M", delta_color="inverse" if total_vac < 0 else "normal")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("SPI vs CPI Scatter")
        fig = px.scatter(evm_f, x="spi", y="cpi", text="cable_name",
                         color="evm_health", size="budget_m",
                         color_discrete_map={"Green": "#34a853", "Yellow": "#fbbc04", "Red": "#ea4335"},
                         height=360)
        fig.add_vline(x=1.0, line_dash="dash", line_color="gray")
        fig.add_hline(y=1.0, line_dash="dash", line_color="gray")
        fig.update_traces(textposition="top center")
        fig.update_layout(margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("EVM Health by Project")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Budget", x=evm_f["cable_name"], y=evm_f["budget_m"],
                              marker_color="#4285f4"))
        fig2.add_trace(go.Bar(name="EAC", x=evm_f["cable_name"], y=evm_f["eac_m"],
                              marker_color="#ea4335"))
        fig2.add_trace(go.Scatter(name="EV", x=evm_f["cable_name"], y=evm_f["ev_m"],
                                  mode="markers+lines", marker_color="#34a853", marker_size=10))
        fig2.update_layout(barmode="group", height=360, margin=dict(l=0,r=0,t=10,b=0),
                           yaxis_title="$M USD")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("KPI Trend — SPI & Completion Over Time")
    kpi_trend = kpi_f.groupby("month").agg(
        avg_spi=("spi", "mean"), avg_completion=("completion_pct", "mean"),
        avg_cpi=("cpi", "mean")
    ).reset_index()
    fig3 = make_subplots(specs=[[{"secondary_y": True}]])
    fig3.add_trace(go.Scatter(x=kpi_trend["month"], y=kpi_trend["avg_spi"],
                              name="Avg SPI", line=dict(color="#4285f4")), secondary_y=False)
    fig3.add_trace(go.Scatter(x=kpi_trend["month"], y=kpi_trend["avg_cpi"],
                              name="Avg CPI", line=dict(color="#34a853", dash="dash")), secondary_y=False)
    fig3.add_trace(go.Bar(x=kpi_trend["month"], y=kpi_trend["avg_completion"],
                          name="Completion %", marker_color="rgba(251,188,4,0.4)"), secondary_y=True)
    fig3.add_hline(y=1.0, line_dash="dot", line_color="gray", secondary_y=False)
    fig3.update_layout(height=360, margin=dict(l=0,r=0,t=10,b=0))
    fig3.update_yaxes(title_text="Performance Index", secondary_y=False)
    fig3.update_yaxes(title_text="Completion %", secondary_y=True)
    st.plotly_chart(fig3, use_container_width=True)
