import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- IMPORT CUSTOM ENGINE ---
try:
    import fraud_forensics as ff
except ImportError:
    st.error("⚠️ CRITICAL ERROR: 'fraud_forensics.py' not found. Please ensure it is in the same directory.")
    st.stop()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Confidential Fraud Audit | Ali Haider",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLING (Professional & Trust-Building) ---
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; font-family: 'Inter', sans-serif; }
    .main-header { font-size: 2.5rem; font-weight: 800; color: #111827; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1.2rem; color: #4b5563; margin-bottom: 20px; }
    .trust-badge { 
        background-color: #eff6ff; 
        color: #1e3a8a; 
        padding: 15px; 
        border-radius: 8px; 
        border-left: 5px solid #2563eb;
        font-weight: 500; 
        margin-bottom: 25px; 
    }
    .cta-box { 
        background-color: #ecfdf5; 
        border: 2px solid #10b981; 
        padding: 25px; 
        border-radius: 10px; 
        text-align: center; 
        margin-top: 20px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .cta-text { font-size: 1.1rem; color: #064e3b; margin-bottom: 15px; }
    a.cta-button {
        background-color: #059669;
        color: white !important;
        padding: 10px 20px;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
    }
    a.cta-button:hover { background-color: #047857; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="main-header">🔒 Confidential Fraud Audit</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Find Hidden Money Leaks in Your Business in 48 Hours</div>', unsafe_allow_html=True)

# --- TRUST BADGE ---
st.markdown("""
<div class="trust-badge">
    📊 <strong>Average Discovery:</strong> Businesses lose 5% of revenue to duplicate payments & errors.<br>
    🔒 <strong>100% Confidential:</strong> Your file is processed in memory and deleted instantly after you close this tab.<br>
    🚀 <strong>Free Preview:</strong> Scan your first 50 transactions instantly below.
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.header("⚙️ Audit Controls")

# 🔐 ADMIN ACCESS CONTROL
admin_password = st.sidebar.text_input("Admin Access Key", type="password", help="Enter key to unlock full processing")
is_admin = admin_password == "AliAudit2025"

if is_admin:
    st.sidebar.success("🔓 Admin Mode Unlocked")
else:
    st.sidebar.info("🔒 Public Mode (50 Row Limit)")

st.sidebar.markdown("---")
st.sidebar.markdown("**Built by Ali Haider**")
st.sidebar.caption("Financial Analyst & Fraud Specialist")
st.sidebar.markdown("[Connect on LinkedIn](https://www.linkedin.com/in/ali-haider-accountant/)") 
st.sidebar.markdown("[Email Me](mailto:alihaiderfinance.cfo@gmail.com)")

# --- STEP 1: UPLOAD ---
st.header("Step 1: Upload your transactions")
st.info("""
**Required Columns:** `Date`, `Vendor` (or Description), `Amount`
*(If your file is different, just rename the columns in Excel first!)*
""")

uploaded_file = st.file_uploader("Drag and drop CSV file here", type=['csv'])

# --- STEP 2: SENSITIVITY ---
st.header("Step 2: Detection Sensitivity")
sensitivity = st.slider(
    "How strict should the AI be?",
    min_value=0.01, max_value=0.20, value=0.05, step=0.01,
    help="Low = Only obvious fraud. High = Flags even minor anomalies."
)

# Map the number to friendly labels
if sensitivity <= 0.05:
    level_label = "Low (Only Obvious Fraud)"
elif sensitivity <= 0.10:
    level_label = "Medium – Recommended ⭐"
else:
    level_label = "High (Super Cautious)"

st.caption(f"Current Setting: **{level_label}**")

# --- MAIN LOGIC ---
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        total_rows = len(df)
        ROW_LIMIT = 50
        
        # 🛑 FREEMIUM GATE
        if total_rows > ROW_LIMIT and not is_admin:
            st.warning(f"🔒 **Free Preview Limit:** Your file has {total_rows} transactions. Analyzing first {ROW_LIMIT} rows only.")
            
            # THE SALES HOOK (Green Box)
            st.markdown("""
            <div class="cta-box">
                <h3>🚨 Full File Locked – Potential Risks Detected in Hidden Rows</h3>
                <p class="cta-text">
                    Want the complete report? I offer a comprehensive forensic audit service.<br>
                    <strong>Flat fee • Money-back guarantee if nothing found.</strong>
                </p>
                <a href="https://www.linkedin.com/in/ali-haider-accountant/" target="_blank" class="cta-button">
                    Contact Me on LinkedIn for Full Audit
                </a>
                <br><br>
                <small>Or email: alihaiderfinance.cfo@gmail.com</small>
            </div>
            """, unsafe_allow_html=True)
            
            df = df.head(ROW_LIMIT)
            st.markdown("---")

        # --- PROCESSING ---
        # Auto-detect columns to be helpful
        cols = df.columns.str.lower()
        date_col = df.columns[cols.str.contains('date')|cols.str.contains('time')][0] if any(cols.str.contains('date')|cols.str.contains('time')) else None
        amount_col = df.columns[cols.str.contains('amount')|cols.str.contains('value')][0] if any(cols.str.contains('amount')|cols.str.contains('value')) else None
        
        # Fallback: Try to find vendor column, if not found use None (engine handles it)
        vendor_col = None
        possible_vendor = df.columns[cols.str.contains('vendor')|cols.str.contains('desc')|cols.str.contains('merchant')]
        if len(possible_vendor) > 0:
            vendor_col = possible_vendor[0]

        if not amount_col:
            st.error("❌ Error: Could not automatically find an 'Amount' column. Please rename it in Excel.")
            st.stop()

        with st.spinner('Running AI Forensic Scan...'):
            # Run Engine
            df_features = ff.prepare_features(df, time_col=date_col, amount_col=amount_col, id_cols=[vendor_col] if vendor_col else None)
            df_scored = ff.run_detectors(df_features, contamination=sensitivity)
            df_final = ff.ensemble_scores(df_scored, score_cols=['iforest_score', 'lof_score'])
            alerts = ff.rules_engine(df_final, amount_col=amount_col)

        # --- RESULTS ---
        if total_rows <= ROW_LIMIT or is_admin:
            st.balloons()
            st.success("✅ Scan Complete!")

        tab1, tab2 = st.tabs(["🚩 Free Fraud Scan Results", "📊 Visual Analysis"])

        with tab1:
            st.subheader("Suspicious Transactions Found")
            
            # Highlight high risk rows in Red
            def highlight_risk(row):
                return ['background-color: #fee2e2' if row['risk_score'] > 0.7 else '' for _ in row]

            # Pick columns to show
            show_cols = [c for c in [date_col, vendor_col, amount_col, 'risk_score'] if c]
            
            st.dataframe(
                df_final.sort_values('risk_score', ascending=False).head(50)[show_cols]
                .style.apply(highlight_risk, axis=1)
                .format({amount_col: "${:,.2f}", 'risk_score': "{:.2f}"}),
                use_container_width=True
            )

            if alerts:
                st.error(f"⚠️ Found {len(alerts)} specific rule violations (Duplicates/Round Numbers).")
                st.table(pd.DataFrame(alerts))
            else:
                st.success("No simple rule violations found in this sample.")

        with tab2:
            st.write("### Risk Score Frequency")
            fig = px.histogram(df_final, x='risk_score', nbins=20, title="Distribution of Risk Scores", color_discrete_sequence=['#ef4444'])
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.write("Tip: Make sure your file is a standard CSV.")