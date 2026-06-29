# 🌊 GSN TPM Intelligence Platform
### Global Submarine Networks — Technical Program Manager Portfolio Project

> **Author:** Nithyashree Babu  
> **Skills Demonstrated:** Subsea infrastructure analytics · Critical path management · EVM · Statistical anomaly detection · Executive dashboards

---

## 📌 Project Overview

This end-to-end analytics platform mirrors the real-world responsibilities of a **Technical Program Manager**, covering:

<img width="1440" height="1246" alt="image" src="https://github.com/user-attachments/assets/92694834-17d4-41a5-844b-a9c280ca97a2" />


## 🏗️ Architecture

```
gsn-tpm-project/
├── src/
│   ├── data_generator.py      # Synthetic subsea cable project data
│   └── analytics.py           # Critical path, EVM, KS-Test, PSI, bottleneck detection
├── data/                      # Generated CSVs (auto-created on run)
│   ├── projects.csv
│   ├── milestones.csv
│   ├── risk_log.csv / risks_scored.csv
│   ├── kpi_timeseries.csv
│   ├── fiber_health.csv / fiber_anomalies.csv
│   ├── critical_path.csv
│   ├── evm_metrics.csv
│   └── bottlenecks.csv
├── dashboard/
│   └── app.py                 # Streamlit multi-page dashboard
├── notebooks/
│   └── gsn_analysis.ipynb     # Analytical narrative for portfolio
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

```bash
# 1. Clone & install
git clone https://github.com/<your-username>/gsn-tpm-project.git
cd gsn-tpm-project
pip install -r requirements.txt

# 2. Generate synthetic data
python src/data_generator.py

# 3. Run analytics engine
python src/analytics.py

# 4. Launch dashboard
streamlit run dashboard/app.py
```

Dashboard opens at **http://localhost:8501**

---

## 📊 Dashboard Pages

| Page | What It Shows |
|---|---|
| **Portfolio Overview** | Gantt timeline · Budget vs Spend · Status distribution · KPI cards |
| **Critical Path** | Milestone completion · Cascade delay heatmap · Top bottlenecks |
| **Risk Intelligence** | Probability × Impact scatter · EMV by category · Live RAID log |
| **Fiber Health** | KS-Test & PSI anomaly results · Attenuation profile by segment |
| **EVM & Forecasting** | SPI/CPI quadrant · EAC/VAC · Performance trending over 18 months |

---

## 🔬 Key Analytical Methods

### Critical Path & Cascade Delay
- Identifies CP milestones (Shore Landing, Wet Testing, RFS, etc.)
- Propagates delay forward: if one CP milestone slips, all downstream milestones shift
- Outputs bottleneck score = `avg_delay × projects_affected`

### Earned Value Management (EVM)
- **SPI** (Schedule Performance Index) = EV / PV
- **CPI** (Cost Performance Index) = EV / AC
- **EAC** (Estimate at Completion) = Budget / CPI
- **VAC** (Variance at Completion) = Budget − EAC
- Red/Yellow/Green health: SPI & CPI both ≥ 0.95 = Green

### Fiber Anomaly Detection
- **KS-Test** (`scipy.stats.ks_2samp`): tests whether live segment attenuation distribution matches reference spec
  - p < 0.05 → distribution shift detected → alert
- **PSI** (Population Stability Index): monitors OSNR feature drift
  - PSI > 0.20 = significant shift (model/signal degradation alert)

### Risk Scoring
- Composite score = Probability × Impact
- EMV = P × I × Average Budget
- Pareto: top 20% risks driving 80% of exposure flagged

---

## 🌐 Subsea Domain Knowledge Demonstrated

- **Cable systems**: EURASIA-1, AFRICA-WEST, MEDLINK-2, NORDIC-CONNECT, INDO-PACIFIC-3
- **Milestones**: Marine licensing → cable manufacturing → ship mobilization → burial → repeater deployment → shore landing → wet testing → RFS
- **Fiber metrics**: Attenuation (dB/km), OSNR (dB), Bit Error Rate
- **Suppliers**: SubCom, Alcatel Submarine Networks, NEC Corporation, HMN Technologies, Prysmian Group
- **EMEA carrier networks**: UK, Norway, France, Egypt, Nigeria, India routing

---

## 📁 Data Dictionary

### projects.csv
| Field | Description |
|---|---|
| project_id | Unique GSN project identifier |
| cable_name | Submarine cable system name |
| length_km | Total cable length |
| capacity_tbps | Design capacity in Tbps |
| delay_days | Schedule overrun vs. planned RFS |
| spi / cpi | Schedule/Cost Performance Indices |
| status | On Track / At Risk / Delayed |

### fiber_health.csv
| Field | Description |
|---|---|
| attenuation_db_km | Signal loss per km (spec: ~0.185 dB/km) |
| osnr_db | Optical Signal-to-Noise Ratio |
| bit_error_rate | BER (target: < 1e-12) |
| anomaly_flag | KS/PSI-triggered anomaly |

---

## 👩‍💻 About the Author

**Nithyashree Babu** is an MSc Business Analytics & Decision Sciences candidate at the University of Leeds, with 7+ years of experience as a Technical Program Manager and Data Analyst. This project demonstrates her ability to apply data-driven, investigative approaches to the complex, global infrastructure challenges faced by Google's GSN team.

- 📧 nithyashreebabu2000@gmail.com
- 📍 Leeds, United Kingdom
- 🔗 [LinkedIn](https://linkedin.com) | [GitHub](https://github.com) | [Portfolio](https://portfolio.com)
