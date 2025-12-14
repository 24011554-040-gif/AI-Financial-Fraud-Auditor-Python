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
    initial_sidebar_state="collapsed"
)

# --- ADVANCED CUSTOM CSS (THE "PREMIUM SAAS" LOOK) ---
CUSTOM_CSS = """
<style>
    /* 1. TYPOGRAPHY IMPORT */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Poppins:wght@500;600;700;800&display=swap');

    /* 2. ROOT VARIABLES */
    :root {
        --primary: #0066FF;
        --primary-glow: rgba(0, 102, 255, 0.4);
        --secondary: #00D4AA;
        --danger: #FF6B6B;
        --bg-gradient-start: #F8FAFF;
        --bg-gradient-end: #FFFFFF;
        --text-dark: #0F172A;
        --text-gray: #64748B;
        --glass-bg: rgba(255, 255, 255, 0.65);
        --glass-border: 1px solid rgba(255, 255, 255, 0.9);
        --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        --card-radius: 24px;
    }

    /* 3. GLOBAL RESET & BODY */
    .stApp {
        background: radial-gradient(circle at top left, #F0F4FF, #FFFFFF, #F0FFF9);
        font-family: 'Inter', sans-serif;
        color: var(--text-dark);
    }
    
    h1, h2, h3 {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: var(--text-dark);
    }

    /* 4. HIDE STREAMLIT DEFAULT ELEMENTS */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* 5. HERO SECTION */
    .hero-container {
        text-align: center;
        padding: 4rem 0 3rem 0;
        animation: fadeIn 1s ease-out;
    }
    
    .hero-title {
        font-size: 4.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0F172A 0%, #0066FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        line-height: 1.1;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: var(--text-gray);
        max-width: 600px;
        margin: 0 auto;
        font-weight: 400;
    }

    /* 6. GLASSMORPHISM CARDS */
    .glass-panel {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: var(--glass-border);
        border-radius: var(--card-radius);
        box-shadow: var(--glass-shadow);
        padding: 2rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .glass-panel:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.15);
    }

    /* 7. CUSTOM FILE UPLOADER STYLE */
    .stFileUploader {
        padding: 2rem;
        border: 2px dashed rgba(0, 102, 255, 0.2);
        border-radius: var(--card-radius);
        background: rgba(255,255,255,0.5);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: var(--primary);
        background: rgba(0, 102, 255, 0.02);
    }
    
    /* 8. METRIC CARDS (COCKPIT) */
    .metric-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    
    .metric-value {
        font-family: 'Poppins', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        line-height: 1.2;
        background: linear-gradient(180deg, var(--text-dark) 0%, #334155 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-gray);
        font-weight: 600;
        margin-top: 0.5rem;
    }

    /* 9. DATAFRAME STYLING */
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(0,0,0,0.05);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* 10. ANIMATIONS */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-enter {
        animation: fadeIn 0.8s ease-out forwards;
    }

    /* 11. CUSTOM BUTTONS */
    .stButton > button {
        background: var(--primary);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        letter-spacing: 0.02em;
        box-shadow: 0 4px 14px 0 rgba(0, 102, 255, 0.39);
        transition: all 0.2s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: #0055D4;
        transform: scale(1.02);
        box-shadow: 0 6px 20px 0 rgba(0, 102, 255, 0.23);
    }

    /* 12. TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
        padding-bottom: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 12px;
        color: var(--text-gray);
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        border: none;
        padding: 0 20px;
    }

    .stTabs [aria-selected="true"] {
        background-color: white;
        color: var(--primary);
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* REMOVE PADDING TOP */
    .block-container {
        padding-top: 2rem !important;
    }
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

# --- UI COMPONENTS ---

def render_hero():
    st.markdown("""
        <div class="hero-container">
            <div class="hero-title">FraudGuard AI</div>
            <div class="hero-subtitle">Next-Gen Forensic Audit & Anomaly Detection. <br> Precision engineered for the modern enterprise.</div>
        </div>
    """, unsafe_allow_html=True)

def render_metric_card(label, value, color=None, subtext=None):
    color_style = f"color: {color};" if color else ""
    st.markdown(f"""
        <div class="glass-panel metric-container animate-enter">
            <div class="metric-value" style="{color_style}">{value}</div>
            <div class="metric-label">{label}</div>
            {f'<div style="font-size:0.75rem; color:#94A3B8; margin-top:4px;">{subtext}</div>' if subtext else ''}
        </div>
    """, unsafe_allow_html=True)

def render_scanning_animation():
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    phases = [
        "Initializing Neural Networks...",
        "Normalizing Transaction Vectors...",
        "Running Isolation Forest...",
        "Calculating Local Outlier Factors...",
        "Detecting Collusion Patterns...",
        "Finalizing Risk Scores..."
    ]
    
    for i, phase in enumerate(phases):
        # Update text with a nice styled HTML
        status_text.markdown(f"""
            <div style="text-align: center; margin-top: 20px; animation: fadeIn 0.5s;">
                <span style="font-family: 'Roboto Mono', monospace; color: #0066FF; font-weight: 600;">
                    {phase}
                </span>
            </div>
        """, unsafe_allow_html=True)
        
        # Smooth progress update
        for p in range(0, 101, 20):
            time.sleep(0.05)
            progress_val = min((i * 100 // len(phases)) + (p // len(phases)), 100)
            progress_bar.progress(progress_val)
            
    progress_bar.progress(100)
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()

# --- MAIN APP LOGIC ---

render_hero()

# Main Container using columns for layout centered
with st.container():
    # File Uploader Section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="text-align: center; margin-bottom: 10px; font-weight: 600; color: #64748B;">UPLOAD TRANSACTION LEDGER</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("", type=['csv', 'xlsx'], label_visibility="collapsed")
        
        # Demo Data Link
        if not uploaded_file:
            st.download_button(
                label="No data? Download Demo CSV",
                data=generate_sample_csv(),
                file_name="demo_fraud_data.csv",
                mime="text/csv",
                use_container_width=True
            )

# Process Data if available
if uploaded_file:
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
            
        # Auto-map columns (simplified for UX)
        cols = df.columns.str.lower()
        date_col = next((c for c in df.columns if 'date' in c.lower() or 'time' in c.lower()), None)
        amount_col = next((c for c in df.columns if 'amount' in c.lower() or 'value' in c.lower() or 'cost' in c.lower()), None)
        vendor_col = next((c for c in df.columns if 'vendor' in c.lower() or 'desc' in c.lower() or 'merchant' in c.lower()), None)
        
        if not (date_col and amount_col):
            st.warning("Could not auto-detect columns. Please rename columns to 'Date', 'Amount', 'Vendor'.")
            st.stop()
            
        # Run Analysis
        render_scanning_animation()
        
        # Fraud Logic
        df_features = ff.prepare_features(df, time_col=date_col, amount_col=amount_col, id_cols=[vendor_col] if vendor_col else None)
        df_scored = ff.run_detectors(df_features, contamination=0.05)
        df_final = ff.ensemble_scores(df_scored, score_cols=['iforest_score', 'lof_score'])
        alerts = ff.rules_engine(df_final, amount_col=amount_col, vendor_col=vendor_col)
        
        # --- DASHBOARD COCKPIT ---
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Stats Calculation
        total_tx = len(df)
        high_risk_tx = df_final[df_final['risk_score'] > 0.7]
        high_risk_count = len(high_risk_tx)
        total_vol = df[amount_col].sum()
        risk_vol = high_risk_tx[amount_col].sum()
        
        # 4 Metric Cards
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            render_metric_card("Transactions", f"{total_tx:,}", subtext="Total Rows Processed")
        with m2:
            render_metric_card("Total Volume", f"${total_vol:,.0f}", color="#0066FF")
        with m3:
            render_metric_card("High Risk", f"{high_risk_count}", color="#FF6B6B", subtext=f"{len(alerts)} Rule Violations")
        with m4:
            render_metric_card("Risk Exposure", f"${risk_vol:,.0f}", color="#FF6B6B")

        st.markdown("<br><br>", unsafe_allow_html=True)

        # --- VISUALIZATION SUITE ---
        tabs = st.tabs(["🔎 Forensic Explorer", "📊 3D Risk Landscape", "📈 Anomaly Timeline"])
        
        with tabs[0]:
            # Highlighted Dataframe
            st.markdown("### 📋 High Priority Investigations")
            
            # Filter to show risky items first
            df_display = df_final.sort_values('risk_score', ascending=False).head(100)
            
            # Custom Column Config
            st.dataframe(
                df_display[[date_col, vendor_col, amount_col, 'risk_score', 'risk_explainer']],
                column_config={
                    "risk_score": st.column_config.ProgressColumn(
                        "Risk Score",
                        help="AI Confidence 0-100%",
                        format="%.2f",
                        min_value=0,
                        max_value=1,
                    ),
                    amount_col: st.column_config.NumberColumn(
                        "Amount",
                        format="$%.2f"
                    )
                },
                use_container_width=True,
                height=400
            )
            
        with tabs[1]:
            # 3D SCATTER PLOT
            if 'hour' in df_final.columns:
                st.markdown("### 🌐 Multidimensional Anomaly Vector")
                
                fig = px.scatter_3d(
                    df_final,
                    x='hour',
                    y=amount_col,
                    z='risk_score',
                    color='risk_score',
                    color_continuous_scale=[[0, '#00D4AA'], [0.5, '#0066FF'], [1, '#FF6B6B']],
                    opacity=0.8,
                    hover_data=[vendor_col],
                    height=600
                )
                
                fig.update_layout(
                    scene=dict(
                        xaxis=dict(title='Hour of Day', backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(0,0,0,0.1)", showbackground=False),
                        yaxis=dict(title='Amount', backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(0,0,0,0.1)", showbackground=False),
                        zaxis=dict(title='Risk Score', backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(0,0,0,0.1)", showbackground=False),
                        bgcolor='rgba(0,0,0,0)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, b=0, t=0)
                )
                st.plotly_chart(fig, use_container_width=True)
                
        with tabs[2]:
            # TIMELINE SCATTER
            st.markdown("### ⏱️ Temporal Risk Distribution")
            fig2 = px.scatter(
                df_final,
                x=date_col,
                y=amount_col,
                size='risk_score',
                color='risk_score',
                color_continuous_scale=[[0, '#00D4AA'], [1, '#FF6B6B']],
                hover_data=[vendor_col]
            )
            fig2.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(255,255,255,0.4)',
                font={'color': '#64748B'},
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor='rgba(0,0,0,0.05)')
            )
            st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"Processing Error: {e}")
        st.markdown("""<div style="text-align:center; padding: 2rem; color: #94A3B8;">
        Ensure your file has <strong>Date</strong>, <strong>Amount</strong>, and <strong>Vendor</strong> columns.
        </div>""", unsafe_allow_html=True)
else:
    # EMPTY STATE HERO
    st.markdown("""
        <div style="text-align: center; margin-top: 3rem; opacity: 0.6;">
            <div style="font-size: 5rem; margin-bottom: 1rem;">📂</div>
            <p style="font-size: 1.1rem; color: #64748B;">Drag and drop your transaction ledger to begin forensic analysis.</p>
        </div>
    """, unsafe_allow_html=True)
