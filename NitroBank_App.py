import streamlit as st
import pandas as pd
from databricks import sql
import plotly.express as px
import os

# 1. PAGE SETUP & ICON (Improvement 6 Applied)
st.set_page_config(
    page_title="Executive Pulse",
    page_icon=":material/monitoring:",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# 2. DATA ENGINE (Databricks Connection)
@st.cache_data(ttl=600)
def fetch_lakehouse_data(query_string):
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
        st.error(f"Connection Failed: {e}")
        return pd.DataFrame()


# 3. HEADER & LOGO
logo_col, title_col = st.columns(2)

with logo_col:
    # This guarantees Streamlit looks in the exact same folder as this Python file
    logo_path = os.path.join(os.path.dirname(__file__), "nitrobank_logo.png")
    try:
        st.image(logo_path, width=200)
    except Exception:
        st.markdown("<h2 style='color:#00F5FF; margin-top:0;'>🏦 NITRO</h2>", unsafe_allow_html=True)
        st.error("Could not find 'nitrobank_logo.png'. Check spelling!")

with title_col:
    st.markdown("""
        <div style="margin-top: 30px; margin-bottom: 20px;">
            <h1 style='color: #5D3FD3; margin: 0px; padding: 0px; line-height: 1.1;'>Executive Pulse</h1>
            <h3 style='color: #5D3FD3; margin: 0px; padding: 0px; line-height: 1.1;'>Real-time Microcredit Segmentation (LATAM)</h3>
        </div>
    """, unsafe_allow_html=True)

# Fetch aggregated data from Delta Gold Table
DATA_QUERY = """
             WITH GlobalStats AS (SELECT COUNT(*) as total_customers, AVG(total_payment_volume_usd) as global_avg_tpv \
                                  FROM gold_user_credit_tiers),
                  TierStats AS (SELECT credit_product_tier as RawName, COUNT(*) as Count \
                                FROM gold_user_credit_tiers \
                                GROUP BY credit_product_tier)
             SELECT t.RawName, t.Count, g.total_customers, g.global_avg_tpv
             FROM TierStats t \
                      CROSS JOIN GlobalStats g \
             """
df = fetch_lakehouse_data(DATA_QUERY)

if not df.empty:
    st.markdown("<br>", unsafe_allow_html=True)

    # 4. KPI ROW
    c1, c2, c3, c4 = st.columns(4)

    total_cust = int(df['total_customers'].iloc[0]) if 'total_customers' in df.columns and not df.empty else 0
    avg_tpv_val = float(df['global_avg_tpv'].iloc[0]) if 'global_avg_tpv' in df.columns and not df.empty else 0

    with c1:
        with st.container(border=True):
            st.metric(label="👥 Total Customers", value=f"{total_cust:,}")
    with c2:
        with st.container(border=True):
            st.metric(label="💸 Avg TPV (USD)", value=f"${avg_tpv_val:,.2f}")
    with c3:
        with st.container(border=True):
            st.metric(label="📡 System Health", value="Optimal")
            st.caption("🟢 Status: Active & Routing")
    with c4:
        with st.container(border=True):
            st.metric(label="🌎 Market", value="LATAM")
            st.caption("📍 BR / MX / CO")

    st.divider()

    # 5. ANALYTICS & SIMULATOR
    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("<h3 style='color: #5D3FD3;'>📊 Portfolio Tier Distribution</h3>", unsafe_allow_html=True)

        nitro_palette = {
            'Prime': '#00F5FF',
            'Nitro Reserve': '#5D3FD3',
            'Risk': '#E0B0FF',
            'Ghost': '#FF3366'
        }

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
                plot_df,
                x='Count',
                y='Tier',
                orientation='h',
                color='Tier',
                color_discrete_map=nitro_palette,
                text='Label',
                template="plotly_dark"
            )

            fig.update_traces(
                textposition='outside',
                textfont=dict(size=16, color='white'),
                marker_cornerradius=15,
                cliponaxis=False
            )

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, title=None),
                yaxis=dict(
                    categoryorder='total ascending',
                    title=None,
                    gridcolor='rgba(255,255,255,0.05)',
                    tickfont=dict(size=18, color='white')
                ),
                margin=dict(l=10, r=80, t=10, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)

        with st.expander("ℹ️ Understanding Portfolio Tiers"):
            st.markdown(f"""
            <div style="line-height: 1.8;">
                <p><strong style="color:#00F5FF;">Prime:</strong> <span style="color:white;">High value clients (Total Payment Volume > $1000) with near-zero declines. These are the bank's most stable revenue assets.</span></p>
                <p><strong style="color:#5D3FD3;">Nitro Reserve:</strong> <span style="color:white;">Active users utilizing micro-credit to bridge liquidity. High growth potential with a solid repayment history.</span></p>
                <p><strong style="color:#E0B0FF;">Risk:</strong> <span style="color:white;">Users showing signs of financial stress with frequent insufficient fund declines. Requires strict monitoring.</span></p>
                <p><strong style="color:#FF3366;">Ghost:</strong> <span style="color:white;">Inactive accounts or users with insufficient data to establish a risk profile.</span></p>
            </div>
            """, unsafe_allow_html=True)
        with right_col:
            # Icon and Title in one clean line, no divider/underline
            st.markdown("<h3 style='color: #5D3FD3;'>💳 Credit Advisor Simulator</h3>", unsafe_allow_html=True)
            st.write("Determine product eligibility based on real-time performance.")

            # Simulator fields placed side-by-side
            sim_col1, sim_col2 = st.columns(2)

            with sim_col1:
                input_tpv = st.number_input("Enter Total Payment Volume (USD)", min_value=0.0, value=0.0, step=10.0)
            with sim_col2:
                input_dec = st.number_input("Enter Historical Declines (0 to 5)", min_value=0, max_value=5, value=0,
                                            step=1)

            # If you also want to remove the line between the inputs and the result,
            # delete or comment out the line below in your script:
            # st.markdown("---")

            if input_tpv >= 400 and input_dec <= 1:
                st.success("🏆 **Approved for Prime Credit**")
            elif input_tpv >= 200 and input_dec <= 5:
                st.warning("⚡ **Approved for Nitro Micro-Credit**")
            else:
                st.error("🚫 **Credit Restricted**")

else:
    st.info("Awaiting connection to Databricks Lakehouse...")