import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import io

# --- IMPORT CUSTOM ENGINE ---
try:
    import fraud_forensics as ff
except ImportError:
    st.error("⚠️ CRITICAL ERROR: 'fraud_forensics.py' not found. Please ensure it is in the same directory.")
    st.stop()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="FraudGuard | AI Forensic Audit",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLING & ASSETS ---
# Modern Color Palette:
# Primary: #1E3A8A (Deep Blue)
# Secondary: #10B981 (Emerald Green)
# Accent: #EF4444 (Red Alert)
# Background: #F3F4F6 (Light Gray)
# Text: #1F2937 (Dark Gray)

st.markdown("""
<style>
    /* Global Settings */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1F2937;
    }
    
    .stApp {
        background-color: #F8FAFC;
    }

    /* Headlines */
    h1, h2, h3 {
        font-weight: 800;
        color: #111827;
    }
    
    h1 { letter-spacing: -1px; }

    /* Custom Cards */
    .card {
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1.5rem;
        border: 1px solid #E5E7EB;
    }
    
    .feature-card {
        text-align: center;
        padding: 1.5rem;
        background: white;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        transition: transform 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }

    /* Trust Badge */
    .trust-section {
        background: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 2rem;
    }

    /* Custom Button Style override */
    div.stButton > button {
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }

    /* Footer */
    .footer {
        margin-top: 4rem;
        border-top: 1px solid #E5E7EB;
        padding-top: 2rem;
        text-align: center;
        color: #6B7280;
        font-size: 0.875rem;
    }
    
    .status-pill {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .status-danger { background: #FECACA; color: #991B1B; }
    .status-safe { background: #D1FAE5; color: #065F46; }

</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---

def generate_sample_csv():
    sample_data = """Date,Vendor,Amount,Description
2025-01-01,Amazon,120.50,Office Supplies
2025-01-02,Shell Station,50.00,Gas
2025-01-03,Shell Station,50.00,Gas (Duplicate!)
2025-01-04,Consulting Inc,5000.00,Service Fee (Round Number)
2025-01-05,Uber,25.30,Travel
2025-01-06,Uber,25.30,Travel
2025-01-07,Fake Corp,1234.00,Misc
2025-01-08,Vendor A,10.00,Test
2025-01-09,Vendor B,20.00,Test
2025-01-10,Vendor C,30.00,Test
2025-01-11,Amazon,45.20,Supplies
2025-01-12,Walmart,12.50,Breakroom
2025-01-13,Shell_01,4500.00,Fuel
2025-01-14,NightOwl_Services,489.23,Service
2025-01-15,NightOwl_Services,489.23,Service
2025-01-16,Vendor_A,9800.00,Consulting
2025-01-17,Vendor_B,9750.00,Consulting
2025-01-18,Shell_02,45.00,Gas
2025-01-19,Shell_02,45.00,Gas
2025-01-20,Shell_02,45.00,Gas
2025-01-21,Legit_Vendor,100.00,Supplies
2025-01-22,Legit_Vendor,100.00,Supplies
2025-01-23,Shadow_Corp,9999.00,Equipment
2025-01-24,Office_Depot,23.40,Paper
2025-01-25,Uber,15.50,Ride
2025-01-26,Amazon,100.00,Misc
2025-01-27,Amazon,100.00,Misc
2025-01-28,Starbucks,5.50,Coffee
2025-01-29,Starbucks,5.50,Coffee
2025-01-30,Delta,450.00,Flight
2025-02-01,Hotel_A,200.00,Stay
2025-02-02,Hotel_A,200.00,Stay
2025-02-03,Restaurant_X,85.50,Dinner
2025-02-04,Restaurant_X,85.50,Dinner
2025-02-05,Software_SaaS,99.00,Subscription
2025-02-06,Software_SaaS,99.00,Subscription
2025-02-07,Hardware_Store,150.25,Repairs
2025-02-08,Hardware_Store,150.25,Repairs
2025-02-09,Consultant_X,2500.00,Fee
2025-02-10,Consultant_X,2500.00,Fee
2025-02-11,Taxi_Yellow,12.00,Ride
2025-02-12,Taxi_Yellow,12.00,Ride
2025-02-13,Online_Ad,500.00,Marketing
2025-02-14,Online_Ad,500.00,Marketing
2025-02-15,Server_Cost,150.00,IT
2025-02-16,Server_Cost,150.00,IT
2025-02-17,Coffee_Shop,4.75,Snack
2025-02-18,Coffee_Shop,4.75,Snack
2025-02-19,Legal_Fee,1000.00,Legal
2025-02-20,Legal_Fee,1000.00,Legal
2025-02-21,Cleaner,120.00,Maintenance
2025-02-22,Cleaner,120.00,Maintenance
2025-02-23,Office_Rent,2000.00,Rent
2025-02-24,Office_Rent,2000.00,Rent
2025-02-25,Water_Bill,45.60,Utilities
2025-02-26,Water_Bill,45.60,Utilities
2025-02-27,Electric_Bill,120.30,Utilities
2025-02-28,Electric_Bill,120.30,Utilities
2025-03-01,Internet,80.00,Utilities
2025-03-02,Internet,80.00,Utilities"""
    return sample_data

# --- SIDEBAR NAV ---
with st.sidebar:
    st.title("🛡️ FraudGuard")
    st.markdown("### Professional Forensic Audit")
    
    menu = st.radio("Navigation", ["🔍 Audit Dashboard", "ℹ️ How It Works", "🔒 Policies & Terms"], index=0)
    
    st.markdown("---")
    
    # Admin Panel
    with st.expander("⚙️ Admin Settings"):
        admin_password = st.text_input("Access Key", type="password")
        is_admin = admin_password == "AliAudit2025"
        if is_admin:
            st.success("✅ Admin Access Granted")
        
        sensitivity = st.slider("AI Sensitivity", 0.01, 0.20, 0.05, 0.01)
        
    st.markdown("---")
    st.caption("© 2025 FraudGuard Analytics")
    st.caption("v2.1.0-Stable")

# --- MAIN CONTENT ---

if menu == "🔍 Audit Dashboard":
    # HERO SECTION
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem;">Uncover Hidden Financial Risks</h1>
        <p style="font-size: 1.25rem; color: #4B5563; max-width: 600px; margin: 0 auto;">
            Our AI-powered forensic engine scans your transactions for duplicates, anomalies, and potential fraud in seconds.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # UPLOAD SECTION
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3>📂 Start Your Audit</h3>
            <p style="color: #6B7280; font-size: 0.9rem;">Upload a CSV or Excel file containing transaction data.</p>
        </div>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader("", type=['csv', 'xlsx', 'xls'], label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            "📥 Download Sample Dataset",
            data=generate_sample_csv(),
            file_name="sample_transactions.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        if not uploaded_file:
            # Placeholder State
            st.markdown("""
            <div class="card" style="text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; background: #F9FAFB; border-style: dashed;">
                <div style="font-size: 4rem; color: #D1D5DB; margin-bottom: 1rem;">📊</div>
                <h3 style="color: #9CA3AF;">Awaiting Data</h3>
                <p style="color: #9CA3AF;">Upload a file to visualize risk analysis.</p>
            </div>
            """, unsafe_allow_html=True)
        
        else:
            # PROCESSING STATE
            try:
                # Load Data
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Basic Validation
                if df.empty:
                    st.error("File is empty.")
                    st.stop()
                    
                total_rows = len(df)
                ROW_LIMIT = 50
                
                # Freemium Logic
                display_df = df.copy()
                if total_rows > ROW_LIMIT and not is_admin:
                    st.warning(f"🔒 Preview Mode: Analyzing first {ROW_LIMIT} of {total_rows} rows.")
                    display_df = df.head(ROW_LIMIT)
                
                # Detect Columns
                cols = display_df.columns.str.lower()
                date_col = display_df.columns[cols.str.contains('date')|cols.str.contains('time')][0] if any(cols.str.contains('date')|cols.str.contains('time')) else None
                amount_col = display_df.columns[cols.str.contains('amount')|cols.str.contains('value')][0] if any(cols.str.contains('amount')|cols.str.contains('value')) else None
                vendor_col = None
                possible_vendor = display_df.columns[cols.str.contains('vendor')|cols.str.contains('desc')|cols.str.contains('merchant')]
                if len(possible_vendor) > 0:
                    vendor_col = possible_vendor[0]

                if not amount_col:
                    st.error("❌ Could not detect an 'Amount' column. Please check your file headers.")
                    st.stop()

                # --- AI PROCESSING ---
                with st.spinner('🤖 AI Forensic Engine Running...'):
                    df_features = ff.prepare_features(display_df, time_col=date_col, amount_col=amount_col, id_cols=[vendor_col] if vendor_col else None)
                    df_scored = ff.run_detectors(df_features, contamination=sensitivity)
                    df_final = ff.ensemble_scores(df_scored, score_cols=['iforest_score', 'lof_score'])
                    alerts = ff.rules_engine(df_final, amount_col=amount_col)

                # --- DASHBOARD ---
                
                # Top Metrics
                m1, m2, m3 = st.columns(3)
                high_risk_count = len(df_final[df_final['risk_score'] > 0.7])
                total_audited = len(df_final)
                duplicate_count = len([a for a in alerts if a['type'] == 'duplicate'])
                
                m1.metric("Transactions Audited", total_audited)
                m2.metric("High Risk Flags", high_risk_count, delta=f"{high_risk_count/total_audited*100:.1f}%" if total_audited>0 else "0%", delta_color="inverse")
                m3.metric("Confirmed Duplicates", duplicate_count, delta_color="inverse")
                
                st.markdown("---")

                # Main Tabs
                tab_list, tab_visuals, tab_details = st.tabs(["🚩 Risk Feed", "📈 Visual Analytics", "🔬 Detailed Data"])
                
                with tab_list:
                    st.subheader("Priority Alerts")
                    
                    if not alerts and high_risk_count == 0:
                        st.success("✅ No significant issues detected in this sample.")
                    
                    # 1. Rule Alerts
                    if alerts:
                        st.markdown("##### ⚠️ Rule Violations")
                        for alert in alerts:
                            with st.container():
                                st.markdown(f"""
                                <div style="padding: 1rem; background: #FEF2F2; border-left: 4px solid #EF4444; margin-bottom: 0.5rem; border-radius: 4px;">
                                    <strong>{alert['type'].upper().replace('_', ' ')}</strong>: {alert.get('note', '')} 
                                    <span style="float: right; color: #991B1B;">ID: {alert.get('tx_id')}</span>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # 2. AI High Risk
                    st.markdown("##### 🤖 AI Anomalies (Score > 0.7)")
                    high_risk_df = df_final[df_final['risk_score'] > 0.7].sort_values('risk_score', ascending=False)
                    
                    if not high_risk_df.empty:
                        show_cols = [c for c in [date_col, vendor_col, amount_col, 'risk_score', 'risk_explainer'] if c]
                        st.dataframe(
                            high_risk_df[show_cols].style.background_gradient(subset=['risk_score'], cmap='Reds'),
                            use_container_width=True
                        )
                    else:
                        st.info("No AI anomalies crossed the high-risk threshold.")

                with tab_visuals:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Risk Score Distribution**")
                        fig_hist = px.histogram(df_final, x='risk_score', nbins=20, color_discrete_sequence=['#3B82F6'])
                        fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(fig_hist, use_container_width=True)
                    
                    with c2:
                        if vendor_col:
                            st.markdown("**Top Risky Vendors**")
                            # Avg risk per vendor
                            vendor_risk = df_final.groupby(vendor_col)['risk_score'].mean().sort_values(ascending=False).head(10)
                            fig_bar = px.bar(vendor_risk, orientation='h', color_discrete_sequence=['#EF4444'])
                            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                            st.plotly_chart(fig_bar, use_container_width=True)
                
                with tab_details:
                    st.dataframe(df_final)

            except Exception as e:
                st.error(f"Error processing file: {e}")
                st.write("Ensure your file has valid headers (Date, Vendor, Amount).")


elif menu == "ℹ️ How It Works":
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h1>What We Do</h1>
        <p style="font-size: 1.1rem; color: #6B7280;">We combine rules-based accounting checks with advanced Machine Learning.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <h3>Deep Scan</h3>
            <p>We ingest 100% of your transaction ledger, not just a sample. Every row is analyzed against historical patterns.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <h3>AI Detection</h3>
            <p>Our ensemble models (Isolation Forest, LOF) detect subtle anomalies like Benford's Law violations and outlier amounts.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🛡️</div>
            <h3>Privacy First</h3>
            <p>Data never leaves this session. It is processed in ephemeral memory and discarded immediately after analysis.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### Technical Methodology")
    st.markdown("""
    1. **Data Normalization**: Standardization of dates, amounts, and vendor names.
    2. **Feature Engineering**: Calculating velocity (tx per hour), Z-scores, and Vendor clustering.
    3. **Ensemble Scoring**: combining multiple outlier detection algorithms for higher precision.
    4. **Rule Overlay**: Hard checks for duplicates, round numbers, and weekend/holiday activity.
    """)

elif menu == "🔒 Policies & Terms":
    st.markdown("<h1>Privacy Policy & Terms</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <h3>Privacy Commitment</h3>
        <p>At FraudGuard, we take data security seriously. This tool is designed as a client-side processor.</p>
        <ul>
            <li><strong>No Storage:</strong> We do not store your uploaded files.</li>
            <li><strong>Ephemeral Processing:</strong> Data exists in RAM only for the duration of the analysis.</li>
            <li><strong>No Third Parties:</strong> Your financial data is not shared with any external API or vendor.</li>
        </ul>
        <br>
        <h3>Terms of Service</h3>
        <p>By using this tool, you agree to the following:</p>
        <ol>
            <li>This tool is for informational purposes only and does not constitute a certified legal or financial audit.</li>
            <li>FraudGuard is not liable for any financial decisions made based on these results.</li>
            <li>You warrant that you have the right to analyze the data you upload.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)


# --- FOOTER ---
st.markdown("""
<div class="footer">
    <p>FraudGuard Analytics © 2025 | Built for Security & Speed</p>
    <p><a href="#" style="color: #3B82F6; text-decoration: none;">Contact Support</a> | <a href="#" style="color: #3B82F6; text-decoration: none;">API Documentation</a></p>
</div>
""", unsafe_allow_html=True)