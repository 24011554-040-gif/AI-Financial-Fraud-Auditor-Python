import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import io

# --- IMPORT CUSTOM ENGINE ---
try:
    import fraud_forensics as ff
except ImportError:
    st.error("⚠️ CRITICAL ERROR: 'fraud_forensics.py' not found. Please ensure it is in the same directory.")
    st.stop()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FraudGuard AI | Next-Gen Forensic Audit",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ADVANCED CUSTOM CSS (THE "NIKE/GOOGLE" LOOK) ---
st.markdown("""
<style>
    /* IMPORTS */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Poppins:wght@500;600;700;800&family=Roboto+Mono:wght@400;500&display=swap');

    /* VARIABLES */
    :root {
        --primary: #0066FF;
        --secondary: #00D4AA;
        --accent: #FF6B6B;
        --bg-color: #F8FAFF;
        --text-dark: #0F172A;
        --text-gray: #64748B;
        --glass-bg: rgba(255, 255, 255, 0.7);
        --glass-border: rgba(255, 255, 255, 0.5);
        --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }

    /* GLOBAL RESET & TYPOGRAPHY */
    .stApp {
        background-color: var(--bg-color);
        background-image: 
            radial-gradient(at 0% 0%, rgba(0, 102, 255, 0.05) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(0, 212, 170, 0.05) 0px, transparent 50%);
        background-attachment: fixed;
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Poppins', sans-serif;
        color: var(--text-dark);
        letter-spacing: -0.02em;
    }
    
    h1 {
        font-weight: 800;
        font-size: 3.5rem;
        background: linear-gradient(135deg, #0F172A 0%, #334155 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    p, li {
        color: var(--text-gray);
        line-height: 1.6;
    }

    /* GLASSMORPHISM CARDS */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: var(--shadow-sm);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 1.5rem;
        position: relative;
    }
    
    .glass-card:hover {
        transform: translateY(-5px) scale(1.01);
        box-shadow: var(--shadow-lg);
        border-color: rgba(0, 102, 255, 0.2);
    }

    /* METRIC CARDS */
    .metric-value {
        font-family: 'Poppins', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary);
        line-height: 1.2;
    }
    
    .metric-label {
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        color: var(--text-gray);
    }

    /* SIDEBAR STYLING */
    section[data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid rgba(0,0,0,0.05);
    }

    /* CUSTOM BUTTONS */
    .stButton button {
        background: linear-gradient(135deg, var(--primary) 0%, #0052CC 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 102, 255, 0.2);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 102, 255, 0.3);
    }

    /* ALERTS & STATUS PILLS */
    .status-pill {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .status-high { background: rgba(255, 107, 107, 0.15); color: #D63031; border: 1px solid rgba(255, 107, 107, 0.2); }
    .status-safe { background: rgba(0, 212, 170, 0.15); color: #009688; border: 1px solid rgba(0, 212, 170, 0.2); }

    /* ANIMATIONS */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-enter {
        animation: fadeInUp 0.6s ease-out forwards;
    }

    /* TAB STYLING */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 0;
        color: var(--text-gray);
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        border-bottom: 2px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--primary);
        border-bottom: 2px solid var(--primary);
    }

</style>
""", unsafe_allow_html=True)

# --- HTML CONTENT CONSTANTS (UNINDENTED FOR MARKDOWN SAFETY) ---

HTML_HERO_SECTION = """
<div class="animate-enter" style="text-align: center; margin-bottom: 4rem; padding: 2rem 0;">
<h1>Uncover the Invisible.</h1>
<p style="font-size: 1.25rem; max-width: 700px; margin: 0 auto; color: #64748B;">
Advanced AI forensics to detect anomalies, duplicates, and fraud in your financial data.
Fast. Secure. Precise.
</p>
</div>
"""

HTML_DATA_INGESTION_CARD = """
<div class="glass-card">
<h3>📂 Data Ingestion</h3>
<p style="font-size: 0.9rem;">Drag & Drop your transaction ledger (CSV/Excel).</p>
</div>
"""

HTML_EMPTY_STATE = """
<div class="glass-card" style="height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; border-style: dashed; border-color: #CBD5E1;">
<div>
<div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;">📊</div>
<h3 style="color: #94A3B8;">Awaiting Dataset</h3>
<p style="color: #94A3B8; font-size: 0.9rem;">Upload file to trigger the Neural Engine.</p>
<br>
<div style="text-align: left; background: #F1F5F9; padding: 15px; border-radius: 8px; font-size: 0.85rem; color: #64748B;">
<strong>Required Columns:</strong>
<ul style="margin-top: 5px; margin-bottom: 0;">
<li>📅 <strong>Date</strong> (e.g., 'Transaction Date', 'Time')</li>
<li>💰 <strong>Amount</strong> (e.g., 'Value', 'Cost', 'Price')</li>
<li>🏢 <strong>Vendor</strong> (Optional, e.g., 'Merchant', 'Description')</li>
</ul>
</div>
</div>
</div>
"""

HTML_METHODOLOGY_HEADER = """
<div style="max-width: 800px; margin: 0 auto; padding-top: 2rem;">
<h1>The Engine Under the Hood</h1>
<p>Our hybrid detection system combines traditional rule-based forensic accounting with state-of-the-art unsupervised machine learning.</p>
</div>
"""

HTML_METHODOLOGY_CARD_1 = """
<div class="glass-card">
<h3>1. Ensemble Machine Learning</h3>
<p>We do not rely on a single model. We aggregate votes from:</p>
<ul>
<li><strong>Isolation Forests:</strong> Efficiently isolates anomalies by randomly selecting a feature and split value.</li>
<li><strong>Local Outlier Factor (LOF):</strong> Measures the local density deviation of a data point with respect to its neighbors.</li>
</ul>
</div>
"""

HTML_METHODOLOGY_CARD_2 = """
<div class="glass-card">
<h3>2. Digital Fingerprinting</h3>
<p>We generate a 15-dimensional vector for every transaction, analyzing:</p>
<ul>
<li><strong>Velocity:</strong> Frequency of transactions per time window.</li>
<li><strong>Benford's Law:</strong> Distribution of leading digits.</li>
<li><strong>Global & Local Z-Scores:</strong> Deviation from both the vendor's history and the global ledger.</li>
</ul>
</div>
"""

HTML_PRIVACY_HEADER = """
<div style="max-width: 800px; margin: 0 auto; padding-top: 2rem;">
<h1>Data Privacy & Terms</h1>
<div class="glass-card" style="border-left: 5px solid #00D4AA;">
<h3>🔐 Zero-Retention Policy</h3>
<p>This application operates on a <strong>"Compute & Destroy"</strong> architecture.</p>
<ul>
<li>Your data exists in the server's RAM <strong>only</strong> during the active session.</li>
<li>No database persistence. No S3 storage. No logs containing PII.</li>
<li>Once you close this tab, the data is irretrievably lost.</li>
</ul>
</div>
<br>
<div class="glass-card">
<h3>Disclaimer</h3>
<p>This tool is an automated analytical aid and does not constitute a certified financial audit or legal opinion. FraudGuard Analytics accepts no liability for decisions made based on these outputs.</p>
</div>
</div>
"""

# --- HELPER FUNCTIONS ---
def generate_sample_csv():
    # Expanded sample data for better visuals
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

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='text-align: left; color: #0066FF;'>🛡️ FraudGuard <span style='font-size:0.5em; color:#00D4AA'>AI</span></h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    menu = st.radio("MAIN MENU", ["Dashboard", "Methodology", "Privacy Policy"], index=0)
    
    st.markdown("---")
    st.markdown("### ⚙️ Control Center")
    
    # Admin Panel
    with st.expander("Admin Access"):
        admin_password = st.text_input("Security Key", type="password")
        is_admin = admin_password == "AliAudit2025"
        if is_admin:
            st.success("🔓 Authenticated")
        
        # Sensitivity UX Improvements
        st.markdown("**🔍 Detection Sensitivity**")
        sensitivity = st.slider("", 0.01, 0.20, 0.05, 0.01, help="Higher sensitivity detects more subtle anomalies but may increase false positives.")
        
        # Dynamic label for sensitivity
        if sensitivity <= 0.05:
            sens_label = "🟢 Conservative (Low False Positives)"
            sens_desc = "Flags only the most obvious anomalies."
        elif sensitivity <= 0.10:
            sens_label = "🟡 Balanced (Recommended)"
            sens_desc = "Good balance between detection and noise."
        else:
            sens_label = "🔴 Aggressive (Maximum Detection)"
            sens_desc = "Flags everything unusual. Expect some false alarms."
            
        st.caption(f"{sens_label}\n\n*{sens_desc}*")
        
    st.markdown("---")
    st.markdown("""
<div style='background: #EFF6FF; padding: 15px; border-radius: 10px;'>
<small style='color: #1E3A8A; font-weight: 600;'>STATUS</small><br>
<span class='status-pill status-safe'>● System Online</span>
</div>
""", unsafe_allow_html=True)

# --- MAIN APPLICATION LOGIC ---

if menu == "Dashboard":
    # HERO SECTION
    st.markdown(HTML_HERO_SECTION, unsafe_allow_html=True)

    # DATA INPUT SECTION
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(HTML_DATA_INGESTION_CARD, unsafe_allow_html=True)
        uploaded_file = st.file_uploader("", type=['csv', 'xlsx', 'xls'], label_visibility="collapsed")
        
        st.download_button(
            "📥 Get Demo Data",
            data=generate_sample_csv(),
            file_name="demo_fraud_data.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        if not uploaded_file:
            # EMPTY STATE WITH ILLUSTRATION PLACEHOLDER
            st.markdown(HTML_EMPTY_STATE, unsafe_allow_html=True)
        else:
            # PROCESSING & DASHBOARD
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                # Validation
                if df.empty:
                    st.error("❌ The file appears to be empty.")
                    st.stop()

                total_rows = len(df)
                ROW_LIMIT = 60 # UPDATED LIMIT
                
                # Freemium Logic
                display_df = df.copy()
                is_limited = False
                
                if total_rows > ROW_LIMIT and not is_admin:
                    is_limited = True
                    display_df = df.head(ROW_LIMIT)
                    # We do not stop here, we process the limited data but warn the user

                # --- SMART COLUMN MAPPING ---
                # Attempt to find standard columns automatically
                cols = display_df.columns.str.lower()
                
                # 1. DATE Mapping
                possible_date = [c for c in display_df.columns if 'date' in c.lower() or 'time' in c.lower() or 'day' in c.lower()]
                date_col = possible_date[0] if possible_date else None
                
                # 2. AMOUNT Mapping
                possible_amount = [c for c in display_df.columns if 'amount' in c.lower() or 'value' in c.lower() or 'cost' in c.lower() or 'price' in c.lower()]
                amount_col = possible_amount[0] if possible_amount else None
                
                # 3. VENDOR Mapping
                possible_vendor = [c for c in display_df.columns if 'vendor' in c.lower() or 'desc' in c.lower() or 'merchant' in c.lower() or 'party' in c.lower()]
                vendor_col = possible_vendor[0] if possible_vendor else None

                # Fallback: Manual Column Selector if Auto-detection fails
                if not date_col or not amount_col:
                    st.warning("⚠️ Could not automatically detect required columns. Please map them manually below.")
                    with st.expander("🔧 Manual Column Mapping", expanded=True):
                        c_map1, c_map2, c_map3 = st.columns(3)
                        date_col = c_map1.selectbox("Date Column", display_df.columns, index=display_df.columns.get_loc(date_col) if date_col else 0)
                        amount_col = c_map2.selectbox("Amount Column", display_df.columns, index=display_df.columns.get_loc(amount_col) if amount_col else 0)
                        vendor_col = c_map3.selectbox("Vendor/Description Column", display_df.columns, index=display_df.columns.get_loc(vendor_col) if vendor_col else 0)
                
                if not amount_col:
                    st.error("❌ Cannot proceed without an Amount column.")
                    st.stop()

                # --- AI EXECUTION ---
                with st.spinner('⚡ Neural Engine analyzing patterns...'):
                    df_features = ff.prepare_features(display_df, time_col=date_col, amount_col=amount_col, id_cols=[vendor_col] if vendor_col else None)
                    df_scored = ff.run_detectors(df_features, contamination=sensitivity)
                    df_final = ff.ensemble_scores(df_scored, score_cols=['iforest_score', 'lof_score'])
                    # Pass vendor_col dynamically to rules_engine
                    alerts = ff.rules_engine(df_final, amount_col=amount_col, vendor_col=vendor_col)

                # --- COCKPIT DASHBOARD ---
                
                # 1. METRICS ROW
                m1, m2, m3, m4 = st.columns(4)
                
                high_risk_count = len(df_final[df_final['risk_score'] > 0.7])
                duplicate_count = len([a for a in alerts if a['type'] == 'duplicate'])
                total_audited = len(df_final)
                avg_risk = df_final['risk_score'].mean() * 100
                
                with m1:
                    st.markdown(f"""<div class="glass-card" style="padding: 1.5rem; text-align: center;">
<div class="metric-label">Volume Processed</div>
<div class="metric-value">{total_audited}</div>
</div>""", unsafe_allow_html=True)
                with m2:
                    st.markdown(f"""<div class="glass-card" style="padding: 1.5rem; text-align: center;">
<div class="metric-label">High Risk Flags</div>
<div class="metric-value" style="color: #FF6B6B;">{high_risk_count}</div>
</div>""", unsafe_allow_html=True)
                with m3:
                    st.markdown(f"""<div class="glass-card" style="padding: 1.5rem; text-align: center;">
<div class="metric-label">Rule Violations</div>
<div class="metric-value" style="color: #FFA500;">{len(alerts)}</div>
</div>""", unsafe_allow_html=True)
                with m4:
                    st.markdown(f"""<div class="glass-card" style="padding: 1.5rem; text-align: center;">
<div class="metric-label">Avg Anomaly Score</div>
<div class="metric-value">{avg_risk:.1f}%</div>
</div>""", unsafe_allow_html=True)

                # 2. RESTRICTED ACCESS NOTIFICATION
                if is_limited:
                     st.markdown("""
<div class="glass-card" style="border: 1px solid #10B981; background: rgba(16, 185, 129, 0.05);">
<div style="text-align: center;">
<h3 style="color: #047857; margin-top: 0;">🔓 Unlock Enterprise Capability</h3>
<p style="color: #065F46;">
Preview Mode limited to 60 transactions. Your file contains <strong>{total}</strong> rows.
</p>
<div style="margin-top: 20px;">
<a href="https://www.linkedin.com/in/ali-haider-accountant/" target="_blank" 
style="background-color: #059669; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; box-shadow: 0 4px 6px rgba(5, 150, 105, 0.2);">
Contact for Full Audit
</a>
<span style="margin: 0 15px; color: #065F46; font-weight: 500;">OR</span>
<a href="mailto:alihaiderfinance.cfo@gmail.com" 
style="color: #047857; text-decoration: underline; font-weight: 600;">
alihaiderfinance.cfo@gmail.com
</a>
</div>
</div>
</div>
""".format(total=total_rows), unsafe_allow_html=True)

                # 3. ADVANCED VISUALIZATIONS TABS
                tab1, tab2, tab3 = st.tabs(["🌐 3D Risk Landscape", "📊 Analytics Suite", "📋 Forensic Ledger"])
                
                with tab1:
                    st.markdown("### Multi-Dimensional Anomaly Detection")
                    st.caption("Interact with the model: Rotate, Zoom, and Hover to explore the relationship between Time, Amount, and Risk.")
                    
                    if 'hour' in df_final.columns:
                        # High-End 3D Plot
                        fig_3d = px.scatter_3d(
                            df_final, 
                            x='hour', 
                            y='risk_score', 
                            z=amount_col,
                            color='risk_score',
                            color_continuous_scale='RdBu_r', # Red-Blue reversed (Red = High Risk)
                            size='risk_score',
                            size_max=30,
                            opacity=0.8,
                            hover_data=[vendor_col] if vendor_col else None,
                            title=""
                        )
                        
                        fig_3d.update_layout(
                            scene=dict(
                                xaxis_title='Hour of Day',
                                yaxis_title='AI Risk Score',
                                zaxis_title='Transaction Amount',
                                bgcolor='rgba(0,0,0,0)'
                            ),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=0, r=0, b=0, t=0),
                            height=600
                        )
                        st.plotly_chart(fig_3d, use_container_width=True)
                    else:
                        st.info("Time data required for 3D visualization. Ensure your Date column is correctly mapped.")

                with tab2:
                    c1, c2 = st.columns(2)
                    
                    with c1:
                        st.markdown("""<div class="glass-card"><h4>Anomaly Distribution</h4></div>""", unsafe_allow_html=True)
                        fig_hist = px.histogram(
                            df_final, 
                            x='risk_score', 
                            nbins=30, 
                            color_discrete_sequence=['#0066FF'],
                            opacity=0.8
                        )
                        fig_hist.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)',
                            xaxis_title="Risk Score (0.0 - 1.0)",
                            yaxis_title="Count",
                            bargap=0.1
                        )
                        st.plotly_chart(fig_hist, use_container_width=True)
                        
                    with c2:
                        st.markdown("""<div class="glass-card"><h4>Top Risk Vendors</h4></div>""", unsafe_allow_html=True)
                        if vendor_col:
                            vendor_risk = df_final.groupby(vendor_col).agg({'risk_score': 'mean', amount_col: 'sum'}).sort_values('risk_score', ascending=False).head(10)
                            fig_bar = px.bar(
                                vendor_risk, 
                                x='risk_score', 
                                y=vendor_risk.index, 
                                orientation='h',
                                color='risk_score',
                                color_continuous_scale='Reds'
                            )
                            fig_bar.update_layout(
                                paper_bgcolor='rgba(0,0,0,0)', 
                                plot_bgcolor='rgba(0,0,0,0)',
                                yaxis={'categoryorder':'total ascending'}
                            )
                            st.plotly_chart(fig_bar, use_container_width=True)

                with tab3:
                    st.markdown("### Priority Investigation Queue")
                    
                    # Highlight high risk
                    def highlight_risk(row):
                        if row['risk_score'] > 0.7:
                            return ['background-color: rgba(255, 107, 107, 0.2); color: #8B0000'] * len(row)
                        return [''] * len(row)

                    show_cols = [c for c in [date_col, vendor_col, amount_col, 'risk_score', 'risk_explainer'] if c]
                    
                    st.dataframe(
                        df_final.sort_values('risk_score', ascending=False)[show_cols]
                        .style.apply(highlight_risk, axis=1)
                        .format({amount_col: "${:,.2f}", 'risk_score': "{:.3f}"}),
                        use_container_width=True,
                        height=500
                    )

            except Exception as e:
                st.error(f"Processing Error: {str(e)}")
                st.info("Ensure your file has valid columns. You can use the 'Manual Column Mapping' section if auto-detection fails.")

elif menu == "Methodology":
    st.markdown(HTML_METHODOLOGY_HEADER, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(HTML_METHODOLOGY_CARD_1, unsafe_allow_html=True)

    with col2:
        st.markdown(HTML_METHODOLOGY_CARD_2, unsafe_allow_html=True)

elif menu == "Privacy Policy":
    st.markdown(HTML_PRIVACY_HEADER, unsafe_allow_html=True)