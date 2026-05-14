"""
NITROBANK EXECUTIVE PULSE: LATAM MICROCREDIT DASHBOARD
------------------------------------------------------
PURPOSE: Provides segmentation of microcredit portfolios
         across Brazil, Mexico, and Colombia.
TECH STACK: Streamlit, Databricks (Delta Lake), Plotly Express.
KEY FEATURES:
    - Automated Portfolio Tiering (Prime, Nitro, Risk, Ghost)
    - Live KPI Monitoring from Databricks Gold Tables
    - Real-time Credit Advisor Simulator
"""

import streamlit as st
import pandas as pd
from databricks import sql
import plotly.express as px
import os

# ------------------------------------------
# CONFIGURATION: SWITCH BETWEEN MODES HERE
# ------------------------------------------
# Set to True for the "Blazing Fast" portfolio experience
# Set to False to use the live Databricks Lakehouse connection
USE_CSV_MODE = True

# 1. PAGE SETUP & ICON
st.set_page_config(
    page_title="Executive Pulse",
    page_icon=":material/monitoring:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. DATA ENGINE: METHOD A (Databricks Connection)
@st.cache_data(ttl=600)
def fetch_lakehouse_data(query_string):
    """Original method for live production environments."""
    try:
        conn = sql.connect(
            server_hostname=st.secrets["DATABRICKS_HOST"],
            http_path=st.secrets["DATABRICKS_HTTP_PATH"],
            access_token=st.secrets["DATABRICKS_TOKEN"]
        )
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            data = cursor.fetchall()
            dataframe = pd.DataFrame([row.asDict() for row in data])
        conn.close()
        return dataframe
    except Exception as e:
        st.error(f"Databricks Connection Failed: {e}")
        return pd.DataFrame()


# 2. DATA ENGINE: METHOD B (Local CSV Snapshot)
@st.cache_data
def fetch_csv_data():
    """High-performance method for portfolio showcase."""
    try:
        # 1. Main portfolio tier data
        csv_path = os.path.join(os.path.dirname(__file__), "executive_pulse_data.csv")
        dataframe = pd.read_csv(csv_path)

        # 2. User growth trend data
        trend_csv_path = os.path.join(os.path.dirname(__file__), "user_growth_trend.csv")
        df_trend = pd.read_csv(trend_csv_path)

        # 3. TPV trend data
        tpv_csv_path = os.path.join(os.path.dirname(__file__), "AVG_TPV.csv")
        df_tpv_trend = pd.read_csv(tpv_csv_path)

        return dataframe, df_trend, df_tpv_trend
    except Exception as e:
        st.error(f"CSV Loading Failed: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


# 3. THE DATA PIPELINE WRAPPER
def run_data_pipeline():
    """
    Orchestrates the data flow.
    Toggle USE_CSV_MODE at the top of the file to switch sources.
    """
    if USE_CSV_MODE:
        return fetch_csv_data()
    else:
        DATA_QUERY = """
            SELECT DISTINCT
                credit_product_tier AS RawName,
                COUNT(*) OVER (PARTITION BY credit_product_tier) AS Count,
                COUNT(*) OVER () AS total_customers,
                AVG(total_payment_volume_usd) OVER () AS global_avg_tpv
            FROM gold_user_credit_tiers
        """
        df = fetch_lakehouse_data(DATA_QUERY)

        # Fallback to local CSVs for trends in portfolio mode
        try:
            trend_csv_path = os.path.join(os.path.dirname(__file__), "user_growth_trend.csv")
            df_trend = pd.read_csv(trend_csv_path)
        except:
            df_trend = pd.DataFrame()

        try:
            tpv_csv_path = os.path.join(os.path.dirname(__file__), "AVG_TPV.csv")
            df_tpv_trend = pd.read_csv(tpv_csv_path)
        except:
            df_tpv_trend = pd.DataFrame()

        return df, df_trend, df_tpv_trend
# 4. HEADER & LOGO
logo_col, title_col = st.columns(2)

with logo_col:
    logo_path = os.path.join(os.path.dirname(__file__), "nitrobank_logo.png")
    try:
        st.image(logo_path, width=200)
    except Exception:
        st.markdown("<h2 style='color:#00F5FF; margin-top:0;'>🏦 NITRO</h2>", unsafe_allow_html=True)
        st.error("Could not find 'nitrobank_logo.png'.")

with title_col:
    st.markdown("""
        <div style="margin-top: 25px; margin-bottom: 20px;">
            <h1 style='color: #00F5FF; margin: 0px; font-size: 2.2rem;'>Customer Risk Profile Intelligence</h1>
            <p style='color: #E0B0FF; margin: -15px 0px 0px 0px; font-size: 1.1rem; font-weight: 500;'>
                Strategic Audit Period: Q1 2024 — Q4 2025
            </p>
        </div>
    """, unsafe_allow_html=True)

# EXECUTE PIPELINE
df, df_trend, df_tpv_trend = run_data_pipeline()

if not df.empty:
    st.markdown("<br>", unsafe_allow_html=True)

    # 5. KPI ROW
    c1, c2, c3, c4 = st.columns(4)

    total_cust = int(df['total_customers'].iloc[0]) if 'total_customers' in df.columns and not df.empty else 0
    avg_tpv_val = float(df['global_avg_tpv'].iloc[0]) if 'global_avg_tpv' in df.columns and not df.empty else 0

    with c1:
        with st.container(border=True):
            st.metric(label="👥 Total Registered Customers", value=f"{total_cust:,}")

            # Sparkline integration
            if not df_trend.empty and 'month' in df_trend.columns and 'users' in df_trend.columns:
                fig_spark = px.line(df_trend, x='month', y='users')
                fig_spark.update_traces(line_color='#00F5FF', line_width=3)
                fig_spark.update_layout(
                    showlegend=False,
                    xaxis=dict(visible=False, fixedrange=True),
                    yaxis=dict(visible=False, fixedrange=True),
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=40,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    hovermode='x unified'
                )
                st.plotly_chart(fig_spark, use_container_width=True, config={'displayModeBar': False})

                # HTML label row injected right beneath the chart
                st.markdown("""
                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #FFFFFF; margin-top: -12px;">
                        <span>Q1'24</span>
                        <span>Q4'25</span>
                    </div>
                """, unsafe_allow_html=True)
    with c2:
        with st.container(border=True):
            st.metric(label="💸 Avg Total Payment Volume (USD)", value=f"${avg_tpv_val:,.2f}")

            # Sparkline integration
            if not df_tpv_trend.empty and 'month' in df_tpv_trend.columns and 'avg_TPV' in df_tpv_trend.columns:
                fig_tpv_spark = px.line(df_tpv_trend, x='month', y='avg_TPV')
                fig_tpv_spark.update_traces(line_color='#E0B0FF', line_width=3)
                fig_tpv_spark.update_layout(
                    showlegend=False,
                    xaxis=dict(visible=False, fixedrange=True),
                    yaxis=dict(visible=False, fixedrange=True),
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=40,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    hovermode='x unified'
                )
                st.plotly_chart(fig_tpv_spark, use_container_width=True, config={'displayModeBar': False})

                # HTML label row injected right beneath the chart
                st.markdown("""
                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #FFFFFF; margin-top: -12px;">
                        <span>Q1'24</span>
                        <span>Q4'25</span>
                    </div>
                """, unsafe_allow_html=True)
    with c3:
        with st.container(border=True):
            # Focuses on the size of the pool and their high profitability
            st.metric(
                label="💳 Pre-Approved Loan Candidates",
                value="123K",
                delta="$476 Avg. Total Payment Volume"
            )

           
    with c4:
        with st.container(border=True):
            st.metric(label="🌎 Operating Market", value="LATAM")
            # Using HTML to force real image rendering
            st.markdown("""
                <div style="display: flex; align-items: center; gap: 7px; font-size: 0.85rem; color: #808495; margin-top: -10px;">
                    <span> </span>
                    <img src="https://flagcdn.com/w20/br.png" width="18"> Brazil /
                    <img src="https://flagcdn.com/w20/mx.png" width="18"> Mexico /
                    <img src="https://flagcdn.com/w20/co.png" width="18"> Colombia
                </div>
            """, unsafe_allow_html=True)

    st.divider()


    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("<h3 style='color: #5D3FD3;'>👥 Customer Distribution by Risk Segmentation</h3>",
                    unsafe_allow_html=True)

        nitro_palette = {'Prime': '#00F5FF', 'Nitro Reserve': '#5D3FD3', 'Risk': '#E0B0FF', 'Ghost': '#FF3366'}

        if 'RawName' in df.columns:
            plot_df = df[['RawName', 'Count']].copy()

            def get_clean_tier(raw_str):
                val = str(raw_str).lower()
                if 'prime' in val or 'tier 1' in val: return 'Prime'
                if 'nitro' in val or 'tier 2' in val: return 'Nitro Reserve'
                if 'risk' in val or 'tier 3' in val: return 'Risk'
                if 'ghost' in val or 'tier 4' in val: return 'Ghost'
                return str(raw_str)

            plot_df['Tier'] = plot_df['RawName'].apply(get_clean_tier)
            plot_df['Label'] = plot_df['Count'].apply(lambda x: f"{x / 1000:.0f}k" if x >= 1000 else str(x))

            fig = px.bar(
                plot_df, x='Count', y='Tier', orientation='h',
                color='Tier', color_discrete_map=nitro_palette,
                text='Label', template="plotly_dark"
            )

            fig.update_traces(
                textposition='outside',
                marker_cornerradius=15,
                textfont=dict(size=18, color='white'),
                cliponaxis=False
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                xaxis=dict(showticklabels=False, showgrid=False, title=None),
                yaxis=dict(categoryorder='total ascending', title=None, tickfont=dict(size=20, color='white')),
                margin=dict(l=10, r=100, t=10, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)

        with st.expander("ℹ️ Understanding Portfolio Tiers"):
            st.markdown("""
                <div style="line-height: 1.8;">
                    <p><strong style="color:#00F5FF;">Prime:</strong> <span style="color:white;">High value clients (Total Payment Volume > $400) with near-zero declines. These are the bank's most stable revenue assets.</span></p>
                    <p><strong style="color:#5D3FD3;">Nitro Reserve:</strong> <span style="color:white;">Active users utilizing micro-credit to bridge liquidity. High growth potential with a solid repayment history.</span></p>
                    <p><strong style="color:#E0B0FF;">Risk:</strong> <span style="color:white;">Users showing signs of financial stress with frequent insufficient fund declines. Requires strict monitoring.</span></p>
                    <p><strong style="color:#FF3366;">Ghost:</strong> <span style="color:white;">Inactive accounts or users with insufficient data to establish a risk profile.</span></p>
                </div>
                """, unsafe_allow_html=True)

    with right_col:
        st.markdown("<h3 style='color: #5D3FD3;'>💳 Credit Advisor Simulator</h3>", unsafe_allow_html=True)
        st.write("Determine product eligibility based on performance.")

        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            input_tpv = st.number_input("Enter Total Payment Volume (USD)", min_value=0.0, value=0.0, step=10.0)
        with sim_col2:
            input_dec = st.number_input("Enter Historical Declines (0 to 5)", min_value=0, max_value=5, value=0)

        # Logic engine
        if input_tpv == 0:
            st.info("👻 **Ghost Account Detected**")
            st.caption("Criteria: No transaction history found.")
        elif input_tpv >= 400 and input_dec == 0:
            st.success("🏆 **Approved for Prime Credit**")
            st.caption("Criteria: High Volume & Zero Risk Profile")
        elif input_tpv >= 300 and input_dec <= 2:
            st.warning("⚡ **Approved for Nitro Micro-Credit**")
            st.caption("Criteria: Emerging User & Managed Risk")
        else:
            st.error("🚫 **Credit Restricted**")
            st.caption("Criteria: Insufficient Volume or High Decline Rate")
else:
    st.info("Awaiting connection to Data Pipeline...")
    st.info("Awaiting connection to Databricks Lakehouse...")
