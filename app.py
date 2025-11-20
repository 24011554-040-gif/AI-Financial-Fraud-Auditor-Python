import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- IMPORT YOUR CUSTOM ENGINE ---
try:
    import fraud_forensics as ff
except ImportError:
    st.error("⚠️ CRITICAL ERROR: 'fraud_forensics.py' not found. Please ensure both 'app.py' and 'fraud_forensics.py' are in the same directory.")
    st.stop()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Forensic Audit Pro | AI-Powered Fraud Detection",
    page_icon="🕵️‍♀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLING (Professional look with Inter font) ---
st.markdown("""
<style>
    /* Global styles */
    .stApp {
        background-color: #f8f9fa; /* Light Gray Background */
        font-family: 'Inter', sans-serif;
    }
    /* Main Header Styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0d47a1; /* Dark Blue */
        margin-bottom: 0.5rem;
    }
    /* Sub Header */
    .sub-header {
        font-size: 1.2rem;
        color: #495057; /* Gray */
        margin-bottom: 20px;
    }
    /* Streamlit widgets tweaks for rounded corners */
    .stButton>button, .stFileUploader, .stSlider {
        border-radius: 8px;
    }
    /* Metric Boxes - Enhanced */
    div[data-testid="stMetric"] > div {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #1e88e5; /* Blue Accent */
    }
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] button {
        background-color: #ffffff;
        border-radius: 8px 8px 0 0;
        border: 1px solid #dee2e6;
        padding: 10px 15px;
        margin: 0 5px;
    }
    /* High Risk Table Color */
    .risk-high { color: #d32f2f; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="main-header">🕵️‍♀️ Forensic Audit Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Risk Assessment for Corporate Finance</div>', unsafe_allow_html=True)

# --- INFO BOX ---
st.info("Upload your CSV file using the sidebar controls to begin the advanced forensic analysis.")

# --- SIDEBAR ---
st.sidebar.header("⚙️ Audit Controls")
uploaded_file = st.sidebar.file_uploader("Upload Transaction CSV", type=['csv'])
st.sidebar.markdown("---")
contamination = st.sidebar.slider("Anomaly Sensitivity (ML)", 0.001, 0.05, 0.01, format="%.3f", help="Adjusts the model's aggressiveness in detecting statistical outliers. Higher values flag more anomalies.")

# --- MAIN APP LOGIC ---
if uploaded_file:
    try:
        # 1. Load Data
        df = pd.read_csv(uploaded_file)

        # 2. Preprocessing & Feature Engineering
        cols = df.columns.str.lower()
        date_col = df.columns[cols.str.contains('date') | cols.str.contains('time')][0] if any(cols.str.contains('date') | cols.str.contains('time')) else None
        amount_col = df.columns[cols.str.contains('amount') | cols.str.contains('value')][0] if any(cols.str.contains('amount') | cols.str.contains('value')) else None
        
        if not amount_col:
            st.error("❌ ERROR: Could not automatically find an 'Amount' column. Please check your CSV format.")
            st.stop()
            
        with st.spinner('Running Advanced Forensic Engine...'):
            # A. Feature Engineering
            df_features = ff.prepare_features(df, time_col=date_col, amount_col=amount_col, id_cols=['Vendor'])
            
            # B. Run Detectors (Isolation Forest, LOF)
            df_scored = ff.run_detectors(df_features, contamination=contamination)
            
            # C. Ensemble Scoring
            df_final = ff.ensemble_scores(df_scored, score_cols=[c for c in df_scored.columns if c.endswith('_score')])
            
            # D. Rule Engine
            # Use 500.0 threshold for round numbers, 5000.0 for high value
            alerts = ff.rules_engine(df_final, amount_col=amount_col, round_threshold=500.0, high_amount_thresh=5000.0)
            
            # E. Graph Analysis
            # We'll use a placeholder for now as the simple test data won't generate graph clusters
            graph_alerts = ff.graph_collusion_detector(df_final, tx_id_col='tx_id', node_cols=['Vendor'])
            
        # --- DASHBOARD LAYOUT ---
        st.subheader(f"Audit Results for {uploaded_file.name}")
        
        # KPI ROW
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Volume Audited", f"${df[amount_col].sum():,.2f}")
        col2.metric("Total Transactions", len(df))
        col3.metric("Rule Violations", len(alerts), delta_color="inverse")
        col4.metric("ML Anomalies Found", sum(df_final['risk_score'] > 0.5), delta_color="inverse")
        
        st.markdown("---")

        tab1, tab2, tab3 = st.tabs(["📊 Executive Summary & Rules", "🧠 Machine Learning Anomaly Analysis", "🕸️ Network Forensics"])

        with tab1:
            st.markdown("#### Top 10 Highest Risk Transactions (ML Score)")
            top_risk = df_final.sort_values('risk_score', ascending=False).head(10)
            display_cols = ['tx_id', date_col, 'Vendor', amount_col, 'risk_score', 'risk_explainer']
            final_cols = [c for c in display_cols if c in df_final.columns]
            
            # Use background_gradient for professional visual emphasis
            st.dataframe(
                top_risk[final_cols].style
                .background_gradient(subset=['risk_score'], cmap='Reds')
                .format({'risk_score': "{:.3f}", amount_col: "${:,.2f}"})
                .set_table_styles([{'selector': 'th', 'props': [('background-color', '#e9ecef')]}]),
                use_container_width=True
            )
            st.caption("Transactions are ranked by their composite Machine Learning Risk Score (0-1).")

            if alerts:
                st.markdown("---")
                st.markdown("#### Deterministic Rule Violations (Classic Fraud/Error)")
                alert_df = pd.DataFrame(alerts)
                # Simple color based on severity
                def color_severity(val):
                    if val == 'high': return 'background-color: #f8d7da'
                    if val == 'medium': return 'background-color: #fff3cd'
                    return ''
                st.dataframe(
                    alert_df.style.applymap(color_severity, subset=['severity']),
                    use_container_width=True
                )
            else:
                st.success("✅ No simple rule violations (Duplicates, Round Numbers) found based on thresholds.")


        with tab2:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("#### Risk Score Distribution")
                # Ensure risk_score is numeric before histogram
                df_final['risk_score'] = pd.to_numeric(df_final['risk_score'], errors='coerce').fillna(0)
                fig_hist = px.histogram(df_final, x='risk_score', nbins=50, title="Frequency of Risk Scores", color_discrete_sequence=['#1e88e5'])
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col_b:
                if date_col:
                    st.markdown("#### Risk Over Time vs. Amount")
                    fig_time = px.scatter(df_final, x=date_col, y=amount_col, color='risk_score', size='risk_score', 
                                          title="Transactions by Time and Risk", color_continuous_scale='Reds')
                    st.plotly_chart(fig_time, use_container_width=True)
                
            st.markdown("---")
            st.markdown("#### Interpreting Machine Learning Results")
            st.info("The Risk Score is generated by two unsupervised models (Isolation Forest and Local Outlier Factor). It measures how unusual a transaction is based on its **time, amount, vendor frequency, and relationship to the global average.**")
            
        with tab3:
            st.markdown("#### Collusion & Entity Graph Analysis")
            st.caption("Requires additional columns (e.g., Card_ID, IP_Address) in the CSV to detect shared entities or fraudulent networks.")
            
            if graph_alerts:
                st.error("🔴 Suspicious Collusion Rings Detected!")
                for cluster in graph_alerts:
                    with st.expander(f"Cluster Found (Size: {cluster['component_size']} Transactions)"):
                        st.write(f"**Entities involved:** {cluster['entities']}")
                        st.write(f"**Transaction Examples:** {cluster['tx_examples']}")
            else:
                st.success("✅ No dense, suspicious graph clusters (collusion rings) detected.")
                st.markdown("---")
                st.warning("To test Network Forensics, ensure your CSV contains entity columns like 'Card', 'Account', or 'IP'.")
                
        # Optional: Raw Data Viewer
        with st.expander("🔬 View Full Raw Data with Engineered Features"):
             st.dataframe(df_final)

    except Exception as e:
        st.error(f"An error occurred during analysis: {e}")
        st.warning("Please ensure your CSV data is clean and contains 'Date', 'Vendor', and 'Amount' columns.")
        
# --- END OF MAIN APP LOGIC ---

# --- BOTTOM SECTION (Footer) ---
st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 Forensic Audit Pro - Built by Ali Haider")
st.sidebar.markdown(f"[View Source Code on GitHub](https://github.com/24011554-040-gif/AI-Financial-Fraud-Auditor-Python.gitHUB)")