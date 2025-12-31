import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time

# --- IMPORT CUSTOM ENGINE ---
try:
    import fraud_forensics as ff
except ImportError:
    st.error("⚠️ CRITICAL ERROR: 'fraud_forensics.py' not found. Please ensure it is in the same directory.")
    st.stop()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FraudGuard AI | Enterprise Forensic Audit",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE & SUBSCRIPTION ---
if 'subscription_tier' not in st.session_state:
    st.session_state.subscription_tier = 'Free' # Options: Free, Standard, Enterprise

def upgrade_tier(tier):
    st.session_state.subscription_tier = tier
    st.success(f"Successfully subscribed to {tier} Tier!")
    time.sleep(1)
    st.rerun()

# --- PREMIUM ENTERPRISE CSS ---
CUSTOM_CSS = """
<style>
    /* 1. GOOGLE FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@300;400;600&display=swap');

    /* 2. VARIABLES - MODERN FINTECH THEME */
    :root {
        --primary: #0F172A;
        --secondary: #1E293B;
        --accent: #3B82F6;       /* Vibrant Blue */
        --accent-glow: rgba(59, 130, 246, 0.5);
        --success: #10B981;
        --danger: #EF4444;
        --background: #F1F5F9;
        --surface: #FFFFFF;
        --border: #E2E8F0;
        --text-primary: #0F172A;
        --text-secondary: #64748B;
        --radius: 12px;
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --glass: rgba(255, 255, 255, 0.9);
    }

    /* DARK MODE SUPPORT (Optional auto-detect) */
    @media (prefers-color-scheme: dark) {
        :root {
            --background: #0B1120;
            --surface: #1E293B;
            --border: #334155;
            --text-primary: #F8FAFC;
            --text-secondary: #94A3B8;
            --glass: rgba(30, 41, 59, 0.9);
        }
    }

    /* 3. GLOBAL STYLES */
    .stApp {
        background-color: var(--background);
        font-family: 'Outfit', sans-serif; /* Premium modern font */
    }
    
    h1, h2, h3, h4, .brand-title {
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: -0.02em;
    }

    /* 4. HEADER / NAV - RESPONSIVE */
    .top-nav {
        background: var(--glass);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-bottom: 1px solid var(--border);
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        border-radius: 0 0 var(--radius) var(--radius);
        box-shadow: var(--shadow);
    }
    
    @media (max-width: 768px) {
        .top-nav {
            flex-direction: column;
            gap: 1rem;
            text-align: center;
            padding: 1rem;
        }
    }

    .brand-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    /* 5. CARDS & METRICS */
    .metric-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-color: var(--accent);
    }

    /* 6. BUTTONS & UI ELEMENTS */
    .stButton button {
        border-radius: var(--radius);
        font-weight: 600;
        transition: all 0.2s;
    }
    .stFileUploader {
        border: 2px dashed var(--border);
        border-radius: var(--radius);
        background: var(--surface);
    }
    .stFileUploader:hover {
        border-color: var(--accent);
        background: rgba(59, 130, 246, 0.05); /* Slight blue tint */
    }

    /* 7. PRICING CARDS */
    .pricing-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s;
    }
    .pricing-card.highlight {
        border: 2px solid var(--accent);
        box-shadow: 0 0 20px var(--accent-glow);
    }
    .price-tag {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 1rem 0;
    }
    
    /* 8. ALERTS & TABS */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 1px solid var(--border);
        gap: 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Outfit', sans-serif;
        font-weight: 500;
    }
    .alert-box {
        padding: 1rem;
        border-radius: var(--radius);
        margin-bottom: 1rem;
        border-left: 4px solid;
        background: var(--surface);
        box-shadow: var(--shadow);
    }
    
    /* CLEANUP */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding-top: 1rem !important;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def generate_sample_csv():
    # Standardized demo data
    data = {
        'Date': pd.date_range(start='2025-01-01', periods=100, freq='H'),
        'Vendor': np.random.choice(['Amazon AWS', 'Uber Business', 'WeWork', 'Staples', 'Unknown LLC', 'Shell'], 100),
        'Amount': np.random.exponential(scale=200, size=100).round(2),
        'Description': ['Service fee' for _ in range(100)]
    }
    # Inject Fraud
    data['Amount'][95] = 9500.00 # High value
    data['Vendor'][95] = 'Shell' # Unusual for gas
    data['Amount'][96] = 5000.00 # Round number
    data['Amount'][97] = 5000.00 # Duplicate
    
    df = pd.DataFrame(data)
    return df.to_csv(index=False).encode('utf-8')

# --- COMPONENTS ---

def render_header():
    st.markdown("""
        <div class="top-nav">
            <div class="brand-title">
                🛡️ FRUAUDGUARD <span style="font-weight:300;">AI</span>
            </div>
            <div style="font-size: 0.875rem; color: var(--text-secondary);">
                Enterprise Forensic Edition v2.1
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_metric(label, value, subtext=None, color=None):
    color_style = f"color: {color};" if color else ""
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{label}</div>
            <div class="metric-value" style="{color_style}">{value}</div>
            {f'<div class="metric-sub" style="{color_style}">{subtext}</div>' if subtext else ''}
        </div>
    """, unsafe_allow_html=True)

def render_scanning():
    with st.spinner('Running Forensic Algorithms & Benford Analysis...'):
        time.sleep(1.5) # Realism

# --- ADMIN SIDEBAR ---
# --- ADMIN & PRICING SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9131/9131546.png", width=50) # Generic Icon
    
    # Subscription Status
    current_tier = st.session_state.subscription_tier
    st.markdown(f"### Current Plan: **{current_tier}**")
    
    if current_tier == 'Free':
        st.info(f"Free Limit: 60 Rows")
        st.markdown("---")
        st.markdown("### 💎 Upgrade")
        if st.button("Standard Plan ($5/mo)"):
            upgrade_tier('Standard')
        if st.button("Enterprise Plan ($10/mo)"):
            upgrade_tier('Enterprise')
            
    elif current_tier == 'Standard':
        st.success(f"Standard Limit: 500 Rows")
        st.markdown("---")
        if st.button("Upgrade to Enterprise ($10)"):
            upgrade_tier('Enterprise')
            
    elif current_tier == 'Enterprise':
        st.success("✨ Unlimited Access Active")
        st.markdown("---")
        if st.button("Downgrade to Free"):
            upgrade_tier('Free')

    st.markdown("---")
    st.markdown("### Admin Panel")
    password = st.text_input("Access Key", type="password")
    is_admin = (password == "AliAudit2025")
    if is_admin:
        st.success("Authenticated")
    st.info("Benford's Law Module Active")

# --- MAIN APP ---

render_header()

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📂 Upload Transaction Ledger")
    uploaded_file = st.file_uploader("Upload CSV/Excel", type=['csv', 'xlsx'], label_visibility="collapsed")

with col2:
    if not uploaded_file:
        st.info("Don't have data?")
        st.download_button("Download Sample Data", generate_sample_csv(), "demo_data.csv", "text/csv")

if uploaded_file:
    # 1. LOAD
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.stop()
        
    # 2. VALIDATE
    if df.empty:
        st.error("File is empty")
        st.stop()
        
    # Auto-map columns
    cols = df.columns.str.lower()
    date_col = next((c for c in df.columns if 'date' in c.lower() or 'time' in c.lower()), None)
    amount_col = next((c for c in df.columns if 'amount' in c.lower() or 'value' in c.lower() or 'cost' in c.lower()), None)
    vendor_col = next((c for c in df.columns if 'vendor' in c.lower() or 'desc' in c.lower() or 'merchant' in c.lower()), None)
    
    if not (date_col and amount_col):
        st.warning("Could not auto-detect 'Date' and 'Amount' columns. Please rename your headers.")
        st.stop()
        
    # Subscription Tier Limit
    if st.session_state.subscription_tier == 'Enterprise':
        ROW_LIMIT = 1000000 # Effectively unlimited
    elif st.session_state.subscription_tier == 'Standard':
        ROW_LIMIT = 500
    else: # Free
        ROW_LIMIT = 60
        
    total_rows = len(df)
    is_limited = (total_rows > ROW_LIMIT) and (not is_admin)
    
    if is_limited:
        df = df.head(ROW_LIMIT)
        st.warning(f"⚠️ {st.session_state.subscription_tier.upper()} PLAN LIMIT: Analyzing first {ROW_LIMIT} of {total_rows} transactions. Upgrade in the sidebar for full audit.")
        
    # 3. PROCESS
    render_scanning()
    
    # Feature Engineering
    df_features = ff.prepare_features(df, time_col=date_col, amount_col=amount_col, id_cols=[vendor_col] if vendor_col else None)
    
    # Detection
    df_scored = ff.run_detectors(df_features, contamination=0.05)
    df_final = ff.ensemble_scores(df_scored, score_cols=['iforest_score', 'lof_score'])
    
    # Rules & Benford
    alerts = ff.rules_engine(df_final, amount_col=amount_col, vendor_col=vendor_col)
    benford_res = ff.benfords_law_analysis(df_final, amount_col=amount_col)
    
    # 4. DASHBOARD - METRICS
    st.markdown("### 📊 Executive Summary")
    
    total_vol = df[amount_col].sum()
    high_risk = df_final[df_final['risk_score'] > 0.7]
    risk_vol = high_risk[amount_col].sum()
    
    m1, m2, m3, m4 = st.columns(4)
    with m1: render_metric("Total Volume", f"${total_vol:,.0f}", "Analyzed Spend")
    with m2: render_metric("Transactions", f"{len(df):,}", "Total Count")
    with m3: render_metric("Rule Violations", f"{len(alerts)}", "Specific Flags", color="#DC2626")
    with m4: render_metric("Risk Exposure", f"${risk_vol:,.0f}", f"{len(high_risk)} High Risk Tx", color="#DC2626")
    
    st.markdown("---")
    
    # 5. VISUALIZATION TABS
    tab1, tab2, tab3 = st.tabs(["🔍 Forensic Insights", "📉 Benford's Law", "📄 Detail View"])
    
    with tab1:
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader("Timeline of Risk")
            # 2D Scatter of Time vs Amount, colored by Risk
            fig_time = px.scatter(
                df_final, 
                x=date_col, 
                y=amount_col, 
                color='risk_score',
                size='amount_log', # Use log amount for size so outliers don't dwarf everything
                color_continuous_scale='Reds',
                hover_data=[vendor_col, 'risk_explainer'],
                title="Transaction Risk Timeline"
            )
            fig_time.update_layout(template="plotly_white", height=400)
            st.plotly_chart(fig_time, use_container_width=True)
            
        with c2:
            st.subheader("Top Risky Vendors")
            if vendor_col:
                # Group by vendor, avg risk
                ven_risk = df_final.groupby(vendor_col)[['risk_score', amount_col]].agg({'risk_score':'mean', amount_col:'sum'}).reset_index()
                ven_risk = ven_risk.sort_values('risk_score', ascending=False).head(10)
                
                fig_ven = px.bar(
                    ven_risk,
                    x='risk_score',
                    y=vendor_col,
                    orientation='h',
                    color='risk_score',
                    color_continuous_scale='Reds',
                    title="Vendor Risk Leaderboard"
                )
                fig_ven.update_layout(template="plotly_white", height=400, yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_ven, use_container_width=True)
            else:
                st.info("No Vendor column detected for aggregation.")

    with tab2:
        st.subheader("Benford's Law Analysis")
        st.markdown("""
        **Benford's Law** states that in naturally occurring financial datasets, the leading digit is likely to be small. 
        Deviations usually indicate **manipulated data**.
        """)
        
        if benford_res:
            bf_df = benford_res['distribution']
            
            # Dual line/bar chart
            fig_bf = go.Figure()
            
            # Expected
            fig_bf.add_trace(go.Scatter(
                x=bf_df['digit'], 
                y=bf_df['expected'],
                mode='lines+markers',
                name='Expected (Benford)',
                line=dict(color='#2563EB', width=3, dash='dash')
            ))
            
            # Actual
            fig_bf.add_trace(go.Bar(
                x=bf_df['digit'], 
                y=bf_df['actual'],
                name='Actual Data',
                marker_color='#0F172A',
                opacity=0.7
            ))
            
            fig_bf.update_layout(
                template="plotly_white",
                title="First Digit Distribution",
                xaxis_title="First Digit (1-9)",
                yaxis_title="Frequency",
                height=500,
                xaxis=dict(tickmode='linear', tick0=1, dtick=1)
            )
            
            st.plotly_chart(fig_bf, use_container_width=True)
            
            # Interpretation (Simple MAD equivalent check)
            max_delta = bf_df['delta'].abs().max()
            if max_delta > 0.05:
                st.error(f"⚠️ Critical Deviation Detected: Max deviation of {max_delta:.1%} suggests potential manipulation.")
            elif max_delta > 0.02:
                st.warning(f"⚠️ Mild Deviation: Max deviation of {max_delta:.1%}.")
            else:
                st.success("✅ Data conforms to Benford's Law (Natural Distribution).")
        else:
            st.warning("Insufficient data for Benford Analysis.")

    with tab3:
        st.subheader("Transaction Ledger")
        
        # Alerts First
        if alerts:
            st.markdown("#### 🚨 Active Alerts")
            for alert in alerts:
                sev_class = "alert-high" if alert['severity'].lower() == 'high' else "alert-medium"
                
                st.markdown(f"""
                <div class="alert-box {sev_class}">
                    <strong>{alert['type']}</strong>: {alert['note']}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("#### Full Data")
        # Style the dataframe
        st.dataframe(
            df_final.sort_values('risk_score', ascending=False),
            column_config={
                "risk_score": st.column_config.ProgressColumn(
                    "Risk",
                    min_value=0,
                    max_value=1,
                    format="%.2f",
                ),
                amount_col: st.column_config.NumberColumn(
                    "Amount",
                    format="$%.2f"
                )
            },
            use_container_width=True,
            height=600
        )