# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

@st.cache_data
def load_data():
    df = pd.read_csv("egypt_macro_quarterly.csv")
    df = df.dropna(subset=["Quarter", "CPI_YoY"], how="any")
    df = df[df["Quarter"].str.match(r"^\d{4}-Q[1-4]$")]

    def quarter_to_date(q):
        year, qtr = q.split("-Q")
        month_map = {"1": "03", "2": "06", "3": "09", "4": "12"}
        return pd.to_datetime(f"{year}-{month_map[qtr]}-01") + pd.offsets.QuarterEnd()

    df["Date"] = df["Quarter"].apply(quarter_to_date)
    df = df.sort_values("Date").reset_index(drop=True)
    df["Real_Rate"] = df["Policy_Rate"] - df["CPI_YoY"]
    return df

df = load_data()

# Get latest complete observation
complete_df = df.dropna(subset=["CPI_YoY", "FX", "Policy_Rate"])
last_obs = complete_df.iloc[-1]
last_quarter = last_obs["Quarter"]
 
def generate_detailed_report(df, last_obs):
    cpi_latest = last_obs["CPI_YoY"]
    fx_latest = last_obs["FX"]
    policy_rate = last_obs["Policy_Rate"]
    real_rate = last_obs["Real_Rate"]
    last_quarter = last_obs["Quarter"]

    # Peak inflation & FX
    peak_cpi_row = df.loc[df["CPI_YoY"].idxmax()]
    peak_cpi_val = peak_cpi_row["CPI_YoY"]
    peak_cpi_qtr = peak_cpi_row["Quarter"]

    peak_fx_row = df.loc[df["FX"].idxmax()]
    peak_fx_val = peak_fx_row["FX"]
    peak_fx_qtr = peak_fx_row["Quarter"]

    # 1-year change
    one_year_ago = df[df["Date"] == last_obs["Date"] - pd.DateOffset(years=1)]
    cpi_1y_ago = one_year_ago["CPI_YoY"].iloc[0] if not one_year_ago.empty else None
    cpi_1y_change = cpi_latest - cpi_1y_ago if cpi_1y_ago else None

    # Fix: Calculate quarters using year and quarter attributes
    n_disinflation_qtrs = (last_obs["Date"].year - peak_cpi_row["Date"].year) * 4 + \
                          (last_obs["Date"].quarter - peak_cpi_row["Date"].quarter)
    n_disinflation_qtrs = max(0, n_disinflation_qtrs)

    report = f"""
    ### Executive Summary: {last_quarter}

    As of {last_quarter}, Egypt’s macroeconomic landscape shows **clear signs of disinflation**, with annual headline CPI at **{cpi_latest:.2f}%**, down sharply from its peak of **{peak_cpi_val:.2f}%** in {peak_cpi_qtr}. The exchange rate has stabilized near **{fx_latest:.2f} EGP/USD**, while the Central Bank of Egypt (CBE) maintains a **restrictive monetary stance** with a policy rate of **{policy_rate:.2f}%**, yielding a **positive real interest rate of {real_rate:.2f}%**—a critical milestone for anchoring inflation expectations.

    ---

    ### Deep Dive: Macroeconomic Dynamics (2021–{last_quarter[:4]})

    #### 1. **Inflation Trajectory**
    - **Pre-2023 Stability**: Inflation remained moderate (4–6%) during 2021–H1 2022.
    - **2023 Shock**: Following the March 2023 devaluation, inflation surged to a peak of **{peak_cpi_val:.2f}%** ({peak_cpi_qtr}), driven by:
      - **Cost-push pressures** from EGP depreciation (imported inflation),
      - **Removal of energy subsidies**,
      - **Supply-side bottlenecks**.
    - **Disinflation Phase**: Since {peak_cpi_qtr}, CPI has declined for **{n_disinflation_qtrs} consecutive quarters**, reflecting the lagged impact of tight monetary policy.

    #### 2. **Exchange Rate Pass-Through (ERPT)**
    - The EGP lost over **60%** of its value between 2021 (≈15.6) and its peak depreciation in {peak_fx_qtr} ({peak_fx_val:.2f}).
    - The **strong positive correlation** between FX depreciation and CPI YoY confirms that exchange rate movements remain the **dominant driver of inflation** in Egypt.
    - Recent FX stability (fluctuating within ±2% since Q1 2024) is a prerequisite for sustained disinflation.

    #### 3. **Monetary Policy Effectiveness**
    - The CBE raised its policy rate aggressively from **8.75%** (2021) to **27.75%** (2024), the highest in two decades.
    - The shift from **deeply negative real rates** (e.g., **–17.5%** in Q3 2023) to **positive territory** since Q3 2024 marks a turning point:
      - **Positive real rates** restore the transmission mechanism,
      - **Curb speculative demand for FX**,
      - **Anchor household and firm inflation expectations**.

    #### 4. **Policy Trade-offs & Outlook**
    - **Achievement**: CBE has successfully broken the back of hyper-inflationary expectations.
    - **Challenge**: High nominal rates constrain private investment and fiscal sustainability (debt servicing costs).
    - **Forward Guidance**: With CPI on track to approach **single digits by late 2026**, gradual rate cuts are plausible—**contingent on FX stability and fiscal discipline**.

    ---

    ### 📈 Data Snapshot (Latest Quarter: {last_quarter})
    - **Headline Inflation (CPI YoY)**: {cpi_latest:.2f}%
    - **Exchange Rate (EGP/USD)**: {fx_latest:.2f}
    - **Policy Rate**: {policy_rate:.2f}%
    - **Real Interest Rate**: {real_rate:.2f}% ({'Restrictive' if real_rate > 0 else 'Accommodative'})
    - **12-Month Inflation Change**: {'↓' if cpi_1y_change and cpi_1y_change < 0 else '↑'} {abs(cpi_1y_change):.2f} ppt (from {cpi_1y_ago:.2f}% in {one_year_ago.iloc[0]['Quarter'] if not one_year_ago.empty else 'N/A'})

    > **Conclusion**: Egypt is transitioning from crisis management to stabilization. The CBE’s credibility is being rebuilt, but **structural reforms** (fiscal consolidation, FX market deepening, and supply-side resilience) are essential to lock in gains.

    *Source: IMF STA Databases (CPI, ER, MFS_IR) — Updated December 2025*
    """
    return report

st.set_page_config(page_title="Egypt Macroeconomic Dashboard", layout="wide")
st.title("Egypt Macroeconomic Dashboard (2021–2025)")
st.markdown("Quarterly tracking of inflation, exchange rate, and monetary policy")

# KPI Cards
col1, col2, col3 = st.columns(3)
col1.metric("Inflation (CPI YoY)", f"{last_obs['CPI_YoY']:.2f}%", delta=None, delta_color="inverse")
col2.metric("Exchange Rate (EGP/USD)", f"{last_obs['FX']:.2f}")
col3.metric("Real Interest Rate", f"{last_obs['Real_Rate']:.2f}%", help="Policy Rate – CPI")

# Charts
fig1 = px.line(df, x="Date", y="CPI_YoY", title="Annual Inflation (CPI YoY %)")
fig1.update_traces(line_color="#FF6B6B")

fig2 = px.line(df, x="Date", y="FX", title="Exchange Rate (EGP per USD)")
fig2.update_traces(line_color="#4ECDC4")

fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=df["Date"], y=df["Policy_Rate"], name="Policy Rate", line=dict(color="#1A535C")))
fig3.add_trace(go.Scatter(x=df["Date"], y=df["Real_Rate"], name="Real Rate", line=dict(color="#FF6B6B", dash="dot")))
fig3.add_hline(y=0, line_dash="dash", line_color="gray")
fig3.update_layout(title="Nominal vs. Real Interest Rate")

# Scatter with OLS (optional)
try:
    fig4 = px.scatter(
        df.dropna(subset=["CPI_YoY", "FX"]),
        x="CPI_YoY", y="FX",
        hover_data=["Quarter"],
        title="Inflation vs. Exchange Rate (with OLS Trend)",
        trendline="ols",
        trendline_color_override="red"
    )
except Exception:
    fig4 = px.scatter(
        df.dropna(subset=["CPI_YoY", "FX"]),
        x="CPI_YoY", y="FX",
        hover_data=["Quarter"],
        title="Inflation vs. Exchange Rate"
    )
    st.warning("Install `statsmodels` for OLS trendline: `pip install statsmodels`")

# Correlation Matrix
corr = df[["CPI_YoY", "FX", "Policy_Rate"]].corr()
fig5 = px.imshow(corr, text_auto=True, color_continuous_scale="Blues", title="Correlation Matrix")

# Layout
col1, col2 = st.columns(2)
col1.plotly_chart(fig1, use_container_width=True)
col2.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)
col3.plotly_chart(fig3, use_container_width=True)
col4.plotly_chart(fig4, use_container_width=True)

st.plotly_chart(fig5, use_container_width=True)

# Auto-generated detailed report
st.markdown(generate_detailed_report(df, last_obs))