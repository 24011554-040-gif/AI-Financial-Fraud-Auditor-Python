import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- IMPORT CUSTOM ENGINE ---
try:
    import fraud_forensics as ff
except ImportError:
    st.error("⚠️ CRITICAL ERROR: 'fraud_forensics.py' not found.")
    st.stop()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Forensic Audit Pro | AI-Powered Fraud Detection",
    page_icon="🕵️‍♀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; font-family: 'Inter', sans-serif; }
    .main-header { font-size: 2.5rem; font-weight: 700; color: #0d47a1; }
    .sub-header { font-size: 1.2rem; color: #495057; margin-bottom: 20px; }
    div[data-testid="stMetric"] > div {
        background-color: #ffffff; border-radius: 10px; padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #1e88e5;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="main-header">🕵️‍♀️ Forensic Audit Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Risk Assessment for Corporate Finance</div>', unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.header("⚙️ Audit Controls")

# 🔐 ADMIN ACCESS CONTROL
admin_password = st.sidebar.text_input("Admin Access Key", type="password", help="Enter key to unlock full processing")
is_admin = admin_password == "AliAudit2025"  # <--- YOUR SECRET PASSWORD

if is_admin:
    st.sidebar.success("🔓 Admin Mode Unlocked")
else:
    st.sidebar.info("🔒 Public Mode (50 Row Limit)")

uploaded_file = st.sidebar.file_uploader("Upload Transaction CSV", type=['csv'])
st.sidebar.markdown("---")
contamination = st.sidebar.slider("Anomaly Sensitivity (ML)", 0.001, 0.05, 0.01, format="%.3f")

# --- MAIN LOGIC ---
if uploaded_file:
    try:
        # 1. READ THE FILE
        df = pd.read_csv(uploaded_file)
        
        # 🛑 2. THE GATEKEEPER (MUST BE HERE)
        ROW_LIMIT = 50
        
        if len(df) > ROW_LIMIT and not is_admin:
            st.warning(f"🔒 **Free Tier Limit Reached:** This file has {len(df)} transactions.")
            st.info(f"The public demo is limited to the first {ROW_LIMIT} rows.")
            
            with st.expander("🚀 Unlock Full Audit Service"):
                st.markdown("""
                **Need to audit the full dataset?**
                I offer professional forensic audits for large datasets using this proprietary AI engine.
                * **Contact:** Ali Haider
                * **Email:** alihaiderfinance.cfo@gmail.com
                """)
            
            # CRITICAL: SLICE THE DATA NOW
            df = df.head(ROW_LIMIT)
            st.write(f"**Analyzing first {ROW_LIMIT} rows only...**")
            st.markdown("---")

        # 3. PROCESSING (Now using the sliced dataframe 'df')
        # ... identifying columns ...
        cols = df.columns.str.lower()
        date_col = df.columns[cols.str.contains('date') | cols.str.contains('time')][0] if any(cols.str.contains('date') | cols.str.contains('time')) else None
        amount_col = df.columns[cols.str.contains('amount') | cols.str.contains('value')][0] if any(cols.str.contains('amount') | cols.str.contains('value')) else None
        
        if not amount_col:
            st.error("❌ ERROR: Could not automatically find an 'Amount' column.")
            st.stop()

        with st.spinner('Running Advanced Forensic Engine...'):
            # Because we sliced 'df' above, this only runs on 50 rows
            df_features = ff.prepare_features(df, time_col=date_col, amount_col=amount_col, id_cols=['Vendor'])
            df_scored = ff.run_detectors(df_features, contamination=contamination)
            df_final = ff.ensemble_scores(df_scored, score_cols=[c for c in df_scored.columns if c.endswith('_score')])
            alerts = ff.rules_engine(df_final, amount_col=amount_col, round_threshold=500.0, high_amount_thresh=5000.0)
            graph_alerts = ff.graph_collusion_detector(df_final, tx_id_col='tx_id', node_cols=['Vendor'])

        # --- DASHBOARD DISPLAY ---
        st.subheader(f"Audit Results for {uploaded_file.name}")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Volume Audited", f"${df[amount_col].sum():,.2f}")
        col2.metric("Transactions", len(df)) # This will show 50
        col3.metric("Rule Violations", len(alerts), delta_color="inverse")
        col4.metric("ML Anomalies", sum(df_final['risk_score'] > 0.5), delta_color="inverse")
        
        st.markdown("---")

        tab1, tab2, tab3 = st.tabs(["📊 Executive Summary", "🧠 ML Analysis", "🕸️ Network"])

        with tab1:
            st.dataframe(
                df_final.sort_values('risk_score', ascending=False).head(10)
                .style.background_gradient(subset=['risk_score'], cmap='Reds'),
                use_container_width=True
            )
            if alerts:
                st.warning(f"Found {len(alerts)} rule violations.")
                st.dataframe(pd.DataFrame(alerts))
            else:
                st.success("✅ No rule violations found in this sample.")

        with tab2:
            col_a, col_b = st.columns(2)
            with col_a:
                fig_hist = px.histogram(df_final, x='risk_score', nbins=50, title="Risk Score Distribution", color_discrete_sequence=['#1e88e5'])
                st.plotly_chart(fig_hist, use_container_width=True)
            with col_b:
                if date_col:
                    fig_time = px.scatter(df_final, x=date_col, y=amount_col, color='risk_score', size='risk_score', title="Risk Over Time", color_continuous_scale='Reds')
                    st.plotly_chart(fig_time, use_container_width=True)

        with tab3:
            if graph_alerts:
                st.error("🔴 Suspicious Collusion Rings Detected!")
                for cluster in graph_alerts:
                    with st.expander(f"Cluster Found (Size: {cluster['component_size']})"):
                        st.write(f"**Entities:** {cluster['entities']}")
            else:
                st.success("✅ No suspicious graph clusters detected.")

    except Exception as e:
        st.error(f"An error occurred: {e}")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 Forensic Audit Pro")
st.sidebar.markdown("[Contact for Full Audit](mailto:alihaiderfinance.cfo@gmail.com)")