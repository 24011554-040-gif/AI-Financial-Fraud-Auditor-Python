import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time
from datetime import datetime, timedelta
import io
import base64

# --- IMPORT CUSTOM ENGINE ---
try:
    import fraud_forensics as ff
    FRAUD_ENGINE_AVAILABLE = True
except ImportError:
    FRAUD_ENGINE_AVAILABLE = False

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                           PAGE CONFIGURATION                                   ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

st.set_page_config(
    page_title="FraudGuard AI | Enterprise Forensic Audit Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://fraudguard.ai/help',
        'Report a bug': 'https://fraudguard.ai/support',
        'About': '# FraudGuard AI v2.0\nEnterprise-grade fraud detection powered by AI.'
    }
)

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                           SESSION STATE INIT                                   ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'dark_mode': False,
        'df': None,
        'df_analyzed': None,
        'alerts': None,
        'analysis_complete': False,
        'show_onboarding': True,
        'selected_risk_filter': 'All',
        'min_amount': 0.0,
        'max_amount': 1000000.0,
        'date_range': None,
        'selected_vendors': [],
        'export_format': 'CSV',
        'notifications': [],
        'analysis_history': [],
        'current_view': 'dashboard',
        'contamination_rate': 0.05,
        'show_advanced_settings': False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                           THEME SYSTEM                                         ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def get_theme_css():
    """Generate CSS based on current theme"""
    if st.session_state.dark_mode:
        return """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
            
            :root {
                --primary: #3B82F6;
                --primary-light: #60A5FA;
                --primary-dark: #1D4ED8;
                --primary-glow: rgba(59, 130, 246, 0.5);
                --secondary: #10B981;
                --secondary-glow: rgba(16, 185, 129, 0.3);
                --danger: #EF4444;
                --danger-glow: rgba(239, 68, 68, 0.3);
                --warning: #F59E0B;
                --warning-glow: rgba(245, 158, 11, 0.3);
                --success: #10B981;
                --info: #06B6D4;
                
                --bg-primary: #0F172A;
                --bg-secondary: #1E293B;
                --bg-tertiary: #334155;
                --bg-card: rgba(30, 41, 59, 0.8);
                --bg-hover: rgba(51, 65, 85, 0.5);
                
                --text-primary: #F8FAFC;
                --text-secondary: #94A3B8;
                --text-muted: #64748B;
                
                --border-color: rgba(148, 163, 184, 0.1);
                --border-glow: rgba(59, 130, 246, 0.3);
                
                --glass-bg: rgba(30, 41, 59, 0.7);
                --glass-border: 1px solid rgba(148, 163, 184, 0.1);
                --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                
                --gradient-primary: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
                --gradient-success: linear-gradient(135deg, #10B981 0%, #06B6D4 100%);
                --gradient-danger: linear-gradient(135deg, #EF4444 0%, #F59E0B 100%);
                --gradient-bg: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
                
                --card-radius: 20px;
                --btn-radius: 12px;
                --input-radius: 10px;
            }
            
            .stApp {
                background: var(--gradient-bg);
            }
            
            /* Animated background particles */
            .stApp::before {
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: 
                    radial-gradient(circle at 20% 80%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 40% 40%, rgba(16, 185, 129, 0.05) 0%, transparent 40%);
                pointer-events: none;
                z-index: 0;
            }
        </style>
        """
    else:
        return """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
            
            :root {
                --primary: #2563EB;
                --primary-light: #3B82F6;
                --primary-dark: #1D4ED8;
                --primary-glow: rgba(37, 99, 235, 0.4);
                --secondary: #059669;
                --secondary-glow: rgba(5, 150, 105, 0.2);
                --danger: #DC2626;
                --danger-glow: rgba(220, 38, 38, 0.2);
                --warning: #D97706;
                --warning-glow: rgba(217, 119, 6, 0.2);
                --success: #059669;
                --info: #0891B2;
                
                --bg-primary: #FFFFFF;
                --bg-secondary: #F8FAFC;
                --bg-tertiary: #F1F5F9;
                --bg-card: rgba(255, 255, 255, 0.9);
                --bg-hover: rgba(241, 245, 249, 0.8);
                
                --text-primary: #0F172A;
                --text-secondary: #475569;
                --text-muted: #94A3B8;
                
                --border-color: rgba(0, 0, 0, 0.06);
                --border-glow: rgba(37, 99, 235, 0.2);
                
                --glass-bg: rgba(255, 255, 255, 0.7);
                --glass-border: 1px solid rgba(255, 255, 255, 0.9);
                --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
                
                --gradient-primary: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
                --gradient-success: linear-gradient(135deg, #059669 0%, #0891B2 100%);
                --gradient-danger: linear-gradient(135deg, #DC2626 0%, #D97706 100%);
                --gradient-bg: linear-gradient(135deg, #F8FAFC 0%, #FFFFFF 50%, #F0F9FF 100%);
                
                --card-radius: 20px;
                --btn-radius: 12px;
                --input-radius: 10px;
            }
            
            .stApp {
                background: var(--gradient-bg);
            }
            
            .stApp::before {
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: 
                    radial-gradient(circle at 10% 90%, rgba(37, 99, 235, 0.08) 0%, transparent 50%),
                    radial-gradient(circle at 90% 10%, rgba(124, 58, 237, 0.08) 0%, transparent 50%),
                    radial-gradient(circle at 50% 50%, rgba(5, 150, 105, 0.03) 0%, transparent 50%);
                pointer-events: none;
                z-index: 0;
            }
        </style>
        """

SHARED_CSS = """
<style>
    /* ═══════════════════════════════════════════════════════════════════════════
       GLOBAL STYLES
    ═══════════════════════════════════════════════════════════════════════════ */
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        color: var(--text-primary);
    }
    
    code, pre, .stCode {
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header, .stDeployButton {
        visibility: hidden !important;
        display: none !important;
    }
    
    .block-container {
        padding: 1rem 2rem 2rem 2rem !important;
        max-width: 1600px;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       HERO SECTION
    ═══════════════════════════════════════════════════════════════════════════ */
    
    .hero-section {
        text-align: center;
        padding: 2.5rem 1rem 2rem 1rem;
        position: relative;
        z-index: 1;
    }
    
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: var(--gradient-primary);
        color: white;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 6px 16px;
        border-radius: 50px;
        margin-bottom: 1.5rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        box-shadow: 0 4px 20px var(--primary-glow);
        animation: pulse-glow 2s ease-in-out infinite;
    }
    
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 4px 20px var(--primary-glow); }
        50% { box-shadow: 0 4px 40px var(--primary-glow); }
    }
    
    .hero-title {
        font-size: clamp(2.5rem, 6vw, 4.5rem);
        font-weight: 800;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        line-height: 1.1;
        animation: slideUp 0.8s ease-out;
    }
    
    .hero-subtitle {
        font-size: clamp(1rem, 2vw, 1.25rem);
        color: var(--text-secondary);
        max-width: 700px;
        margin: 0 auto 2rem auto;
        font-weight: 400;
        line-height: 1.6;
        animation: slideUp 0.8s ease-out 0.1s backwards;
    }
    
    .hero-stats {
        display: flex;
        justify-content: center;
        gap: 3rem;
        flex-wrap: wrap;
        animation: slideUp 0.8s ease-out 0.2s backwards;
    }
    
    .hero-stat {
        text-align: center;
    }
    
    .hero-stat-value {
        font-family: 'Poppins', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary);
    }
    
    .hero-stat-label {
        font-size: 0.8rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       GLASS CARDS
    ═══════════════════════════════════════════════════════════════════════════ */
    
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: var(--glass-border);
        border-radius: var(--card-radius);
        box-shadow: var(--glass-shadow);
        padding: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    }
    
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        border-color: var(--border-glow);
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       METRIC CARDS
    ═══════════════════════════════════════════════════════════════════════════ */
    
    .metric-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: var(--glass-border);
        border-radius: var(--card-radius);
        padding: 1.75rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: var(--metric-color, var(--gradient-primary));
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .metric-card:hover::after {
        opacity: 1;
    }
    
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
        opacity: 0.9;
    }
    
    .metric-value {
        font-family: 'Poppins', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 0.25rem;
    }
    
    .metric-value.primary { color: var(--primary); }
    .metric-value.success { color: var(--success); }
    .metric-value.danger { color: var(--danger); }
    .metric-value.warning { color: var(--warning); }
    
    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        font-weight: 600;
    }
    
    .metric-subtext {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 0.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
    }
    
    .metric-trend {
        display: inline-flex;
        align-items: center;
        gap: 2px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.7rem;
    }
    
    .metric-trend.up {
        background: var(--danger-glow);
        color: var(--danger);
    }
    
    .metric-trend.down {
        background: var(--secondary-glow);
        color: var(--success);
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       UPLOAD ZONE
    ═══════════════════════════════════════════════════════════════════════════ */
    
    .upload-zone {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border: 2px dashed var(--border-color);
        border-radius: var(--card-radius);
        padding: 3rem 2rem;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .upload-zone:hover {
        border-color: var(--primary);
        background: var(--primary-glow);
    }
    
    .upload-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .upload-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .upload-subtitle {
        font-size: 0.9rem;
        color: var(--text-muted);
    }
    
    .upload-formats {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    
    .format-badge {
        background: var(--bg-tertiary);
        color: var(--text-secondary);
        font-size: 0.7rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 20px;
        text-transform: uppercase;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       BUTTONS
    ═══════════════════════════════════════════════════════════════════════════ */
    
    .stButton > button {
        background: var(--gradient-primary) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: var(--btn-radius) !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.02em !important;
        box-shadow: 0 4px 20px var(--primary-glow) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px var(--primary-glow) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Secondary button */
    .stDownloadButton > button {
        background: transparent !important;
        color: var(--primary) !important;
        border: 2px solid var(--primary) !important;
        box-shadow: none !important;
    }
    
    .stDownloadButton > button:hover {
        background: var(--primary-glow) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       TABS
    ═══════════════════════════════════════════════════════════════════════════ */
    
    .stTabs {
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--bg-tertiary);
        padding: 6px;
        border-radius: 16px;
        justify-content: center;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: auto;
        background-color: transparent;
        border-radius: 12px;
        color: var(--text-secondary);
        font-weight: 600;
        font-size: 0.9rem;
        padding: 12px 24px;
        border: none;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary);
        background: var(--bg-hover);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--bg-card) !important;
        color: var(--primary) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }
    
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       DATAFRAME
    ═══════════════════════════════════════════════════════════════════════════ */
    
    .stDataFrame {
        border-radius: 16px !important;
        overflow: hidden !important;
        border: 1px solid var(--border-color) !important;
    }
    
    .stDataFrame [data-testid="stDataFrameResizable"] {
        border-radius: 16px !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       SIDEBAR
    ═══════════════════════════════════════════════════════════════════════════ */
    
    [data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-color);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: var(--text-primary);
    }
    
    .sidebar-section {
        background: var(--glass-bg);
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid var(--border-color);
    }
    
    .sidebar-title {
        font-family: 'Poppins', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-muted);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       ALERTS & NOTIFICATIONS
    ═══════════════════════════════════════════════════════════════════════════ */
    
    .alert-card {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        padding: 1rem 1.25rem;
        border-radius: 12px;
        margin-bottom: 0.75rem;
        border-left: 4px solid;
        transition: all 0.2s ease;
    }
    
    .alert-card:hover {
        transform: translateX(4px);
    }
    
    .alert-card.critical {
        background: var(--danger-glow);
        border-color: var(--danger);
    }
    
    .alert-card.warning {
        background: var(--warning-glow);
        border-color: var(--warning);
    }
    
    .alert-card.info {
        background: var(--primary-glow);
        border-color: var(--primary);
    }
    
    .alert-icon {
        font-size: 1.5rem;
        flex-shrink: 0;
    }
    
    .alert-content {
        flex: 1;
    }
    
    .alert-title {
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--text-primary);
        margin-bottom: 2px;
    }
    
    .alert-description {
        font-size: 0.85rem;
        color: var(--text-secondary);
    }
    
    .alert-meta {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 4px;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       PROGRESS & LOADING
    ═══════════════════════════════════════════════════════════════════════════ */
    
    .scanning-container {
        text-align: center;
        padding: 3rem 2rem;
    }
    
    .scanning-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .scanning-phase {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        color: var(--primary);
        margin-top: 1rem;
        padding: 0.75rem 1.5rem;
        background: var(--primary-glow);
        border-radius: 8px;
        display: inline-block;
    }
    
    .stProgress > div > div > div {
        background: var(--gradient-primary) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       FOOTER
    ═══════════════════════════════════════════════════════════════════════════ */
    
    .footer {
        text-align: center;
        padding: 2rem 1rem;
        margin-top: 3rem;
        border-top: 1px solid var(--border-color);
        color: var(--text-muted);
        font-size: 0.85rem;
    }
    
    .footer-brand {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        color: var(--primary);
    }
    
    .footer-links {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-top: 0.75rem;
    }
    
    .footer-link {
        color: var(--text-secondary);
        text-decoration: none;
        transition: color 0.2s ease;
    }
    
    .footer-link:hover {
        color: var(--primary);
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       RESPONSIVE
    ═══════════════════════════════════════════════════════════════════════════ */
    
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        
        .hero-stats {
            gap: 1.5rem;
        }
        
        .metric-value {
            font-size: 2rem;
        }
        
        .block-container {
            padding: 1rem !important;
        }
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       ANIMATIONS
    ═══════════════════════════════════════════════════════════════════════════ */
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    .skeleton {
        background: linear-gradient(90deg, var(--bg-tertiary) 25%, var(--bg-secondary) 50%, var(--bg-tertiary) 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 8px;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--text-muted);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-secondary);
    }
    
    /* Select boxes */
    .stSelectbox [data-baseweb="select"] {
        border-radius: var(--input-radius);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--glass-bg);
        border-radius: 12px;
        font-weight: 600;
    }
    
    /* Input fields */
    .stTextInput input, .stNumberInput input {
        border-radius: var(--input-radius) !important;
        border-color: var(--border-color) !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px var(--primary-glow) !important;
    }
</style>
"""

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                           UTILITY FUNCTIONS                                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

@st.cache_data
def generate_sample_csv(size=500):
    """Generate comprehensive demo dataset"""
    np.random.seed(42)
    
    vendors = [
        'Amazon AWS', 'Microsoft Azure', 'Google Cloud', 'Uber Business',
        'WeWork', 'Staples Office', 'Shell Gas', 'Delta Airlines',
        'Marriott Hotels', 'Sysco Foods', 'FedEx Express', 'Office Depot',
        'Costco Wholesale', 'Home Depot', 'Enterprise Rent', 'Unknown LLC',
        'ABC Consulting', 'XYZ Services', 'Cash Withdrawal', 'Wire Transfer'
    ]
    
    categories = ['Software', 'Travel', 'Office', 'Fuel', 'Meals', 'Supplies', 'Consulting', 'Other']
    
    dates = pd.date_range(start='2024-01-01', end='2025-01-15', freq='H')[:size]
    
    data = {
        'Transaction_ID': [f'TXN-{i:06d}' for i in range(size)],
        'Date': dates,
        'Vendor': np.random.choice(vendors, size),
        'Category': np.random.choice(categories, size),
        'Amount': np.random.exponential(scale=150, size=size).round(2),
        'Payment_Method': np.random.choice(['Corporate Card', 'Wire', 'ACH', 'Check', 'Cash'], size, p=[0.5, 0.2, 0.15, 0.1, 0.05]),
        'Employee_ID': np.random.choice([f'EMP-{i:04d}' for i in range(1, 51)], size),
        'Department': np.random.choice(['Engineering', 'Sales', 'Marketing', 'Operations', 'Finance', 'HR'], size),
        'Description': np.random.choice([
            'Monthly subscription', 'Travel expense', 'Office supplies',
            'Client dinner', 'Software license', 'Equipment purchase',
            'Consulting fee', 'Maintenance', 'Training', 'Conference'
        ], size)
    }
    
    # Inject realistic fraud patterns
    fraud_indices = [size-1, size-2, size-3, size-10, size-20, size-30, size-50]
    
    # Pattern 1: Unusually high amounts
    data['Amount'][fraud_indices[0]] = 9500.00
    data['Vendor'][fraud_indices[0]] = 'Unknown LLC'
    
    # Pattern 2: Round number fraud
    data['Amount'][fraud_indices[1]] = 5000.00
    data['Amount'][fraud_indices[2]] = 5000.00  # Duplicate
    
    # Pattern 3: Weekend transactions
    data['Amount'][fraud_indices[3]] = 2500.00
    
    # Pattern 4: Unusual vendor
    data['Amount'][fraud_indices[4]] = 3750.00
    data['Vendor'][fraud_indices[4]] = 'Cash Withdrawal'
    
    # Pattern 5: Late night transaction
    data['Amount'][fraud_indices[5]] = 1899.99
    
    # Pattern 6: Split transactions
    for i in range(5):
        if fraud_indices[6] + i < size:
            data['Amount'][fraud_indices[6] + i] = 999.00
            data['Vendor'][fraud_indices[6] + i] = 'XYZ Services'
    
    df = pd.DataFrame(data)
    return df.to_csv(index=False).encode('utf-8')

def format_currency(value):
    """Format number as currency"""
    if value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value/1_000:.1f}K"
    else:
        return f"${value:,.2f}"

def format_number(value):
    """Format large numbers with abbreviations"""
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K"
    else:
        return f"{value:,}"

def calculate_risk_score(amount, hour=None, is_weekend=False, vendor=None):
    """Calculate a simple risk score when fraud_forensics is not available"""
    score = 0.0
    
    # Amount-based scoring
    if amount > 5000:
        score += 0.3
    elif amount > 2000:
        score += 0.15
    elif amount > 1000:
        score += 0.05
    
    # Round number detection
    if amount == int(amount) and amount > 100:
        score += 0.15
    
    # Time-based scoring
    if hour is not None:
        if hour < 6 or hour > 22:
            score += 0.2
    
    # Weekend scoring
    if is_weekend:
        score += 0.1
    
    # Vendor-based scoring
    suspicious_vendors = ['unknown', 'cash', 'wire', 'llc']
    if vendor and any(s in str(vendor).lower() for s in suspicious_vendors):
        score += 0.25
    
    return min(score, 1.0)

def get_risk_explainer(row, amount_col):
    """Generate human-readable risk explanation"""
    reasons = []
    amount = row.get(amount_col, 0)
    
    if amount > 5000:
        reasons.append("High-value transaction")
    if amount == int(amount) and amount > 100:
        reasons.append("Round number")
    if 'hour' in row and (row['hour'] < 6 or row['hour'] > 22):
        reasons.append("Off-hours activity")
    if 'is_weekend' in row and row['is_weekend']:
        reasons.append("Weekend transaction")
    
    vendor = str(row.get('Vendor', '')).lower()
    if 'unknown' in vendor or 'cash' in vendor:
        reasons.append("Suspicious vendor")
    
    return "; ".join(reasons) if reasons else "Standard transaction"

def add_notification(message, type="info"):
    """Add a notification to session state"""
    st.session_state.notifications.append({
        'message': message,
        'type': type,
        'timestamp': datetime.now()
    })

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                           UI COMPONENTS                                        ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def render_hero():
    """Render the hero section"""
    st.markdown("""
        <div class="hero-section">
            <div class="hero-badge">
                <span>✨</span>
                <span>AI-Powered Fraud Detection</span>
            </div>
            <h1 class="hero-title">FraudGuard AI</h1>
            <p class="hero-subtitle">
                Enterprise-grade forensic audit platform powered by advanced machine learning.
                Detect anomalies, prevent fraud, and protect your organization in real-time.
            </p>
            <div class="hero-stats">
                <div class="hero-stat">
                    <div class="hero-stat-value">99.7%</div>
                    <div class="hero-stat-label">Detection Accuracy</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-value">&lt;50ms</div>
                    <div class="hero-stat-label">Analysis Speed</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-value">500K+</div>
                    <div class="hero-stat-label">Threats Blocked</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_metric_card(icon, value, label, color_class="primary", trend=None, trend_value=None, subtext=None):
    """Render a beautiful metric card"""
    trend_html = ""
    if trend and trend_value:
        trend_class = "up" if trend == "up" else "down"
        trend_icon = "↑" if trend == "up" else "↓"
        trend_html = f'<span class="metric-trend {trend_class}">{trend_icon} {trend_value}</span>'
    
    subtext_html = f'<div class="metric-subtext">{subtext} {trend_html}</div>' if subtext else ""
    
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-value {color_class}">{value}</div>
            <div class="metric-label">{label}</div>
            {subtext_html}
        </div>
    """, unsafe_allow_html=True)

def render_alert_card(severity, title, description, meta=""):
    """Render an alert notification card"""
    icons = {
        'critical': '🚨',
        'warning': '⚠️',
        'info': 'ℹ️'
    }
    
    st.markdown(f"""
        <div class="alert-card {severity}">
            <span class="alert-icon">{icons.get(severity, 'ℹ️')}</span>
            <div class="alert-content">
                <div class="alert-title">{title}</div>
                <div class="alert-description">{description}</div>
                <div class="alert-meta">{meta}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_upload_zone():
    """Render the file upload zone"""
    st.markdown("""
        <div class="upload-zone">
            <div class="upload-icon">📊</div>
            <div class="upload-title">Drop your transaction data here</div>
            <div class="upload-subtitle">or click to browse files</div>
            <div class="upload-formats">
                <span class="format-badge">CSV</span>
                <span class="format-badge">XLSX</span>
                <span class="format-badge">XLS</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_scanning_animation():
    """Render an enhanced scanning animation"""
    phases = [
        ("🔍", "Initializing AI Detection Engine..."),
        ("📊", "Parsing Transaction Data..."),
        ("🧮", "Computing Statistical Features..."),
        ("🌲", "Running Isolation Forest Algorithm..."),
        ("🎯", "Calculating Local Outlier Factors..."),
        ("🔗", "Detecting Collusion Patterns..."),
        ("⚡", "Applying Business Rules Engine..."),
        ("✅", "Finalizing Risk Assessments...")
    ]
    
    progress_container = st.container()
    
    with progress_container:
        st.markdown("""
            <div class="scanning-container">
                <div class="scanning-title">🛡️ Forensic Analysis in Progress</div>
            </div>
        """, unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, (icon, phase) in enumerate(phases):
            status_text.markdown(f"""
                <div class="scanning-phase">{icon} {phase}</div>
            """, unsafe_allow_html=True)
            
            steps = 100 // len(phases)
            for step in range(steps):
                time.sleep(0.03)
                progress = min(((i * steps) + step + 1), 100)
                progress_bar.progress(progress)
        
        progress_bar.progress(100)
        time.sleep(0.3)
        
    progress_bar.empty()
    status_text.empty()
    progress_container.empty()

def render_sidebar():
    """Render the enhanced sidebar"""
    with st.sidebar:
        # Logo and Brand
        st.markdown("""
            <div style="text-align: center; padding: 1rem 0 2rem 0;">
                <div style="font-size: 3rem;">🛡️</div>
                <div style="font-family: 'Poppins', sans-serif; font-size: 1.5rem; font-weight: 700; 
                            background: var(--gradient-primary); -webkit-background-clip: text; 
                            -webkit-text-fill-color: transparent;">FraudGuard AI</div>
                <div style="font-size: 0.75rem; color: var(--text-muted);">v2.0 Enterprise</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Theme Toggle
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">🎨 Appearance</div>', unsafe_allow_html=True)
        
        theme = st.toggle("Dark Mode", value=st.session_state.dark_mode, key="theme_toggle")
        if theme != st.session_state.dark_mode:
            st.session_state.dark_mode = theme
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick Actions
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">⚡ Quick Actions</div>', unsafe_allow_html=True)
        
        if st.button("📥 Download Sample Data", use_container_width=True):
            pass  # Handled below
        
        st.download_button(
            label="📋 Download Demo CSV",
            data=generate_sample_csv(),
            file_name=f"fraud_demo_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Analysis Settings (when data is loaded)
        if st.session_state.df is not None:
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown('<div class="sidebar-title">⚙️ Analysis Settings</div>', unsafe_allow_html=True)
            
            st.session_state.contamination_rate = st.slider(
                "Anomaly Sensitivity",
                min_value=0.01,
                max_value=0.20,
                value=st.session_state.contamination_rate,
                step=0.01,
                help="Higher values = more transactions flagged as anomalies"
            )
            
            if st.button("🔄 Re-run Analysis", use_container_width=True):
                st.session_state.analysis_complete = False
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Filters (when analysis is complete)
        if st.session_state.analysis_complete and st.session_state.df_analyzed is not None:
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown('<div class="sidebar-title">🔍 Filters</div>', unsafe_allow_html=True)
            
            st.session_state.selected_risk_filter = st.selectbox(
                "Risk Level",
                ["All", "Critical (>0.8)", "High (>0.6)", "Medium (>0.4)", "Low (≤0.4)"]
            )
            
            df = st.session_state.df_analyzed
            amount_col = st.session_state.get('amount_col', 'Amount')
            
            if amount_col in df.columns:
                min_amt = float(df[amount_col].min())
                max_amt = float(df[amount_col].max())
                
                amount_range = st.slider(
                    "Amount Range",
                    min_value=min_amt,
                    max_value=max_amt,
                    value=(min_amt, max_amt),
                    format="$%.0f"
                )
                st.session_state.min_amount = amount_range[0]
                st.session_state.max_amount = amount_range[1]
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Export Options
        if st.session_state.analysis_complete:
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown('<div class="sidebar-title">📤 Export</div>', unsafe_allow_html=True)
            
            export_format = st.selectbox(
                "Format",
                ["CSV", "Excel", "JSON"],
                key="export_format_select"
            )
            
            if st.button("📥 Export Report", use_container_width=True):
                df_export = st.session_state.df_analyzed
                
                if export_format == "CSV":
                    csv_data = df_export.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"fraud_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                elif export_format == "Excel":
                    buffer = io.BytesIO()
                    df_export.to_excel(buffer, index=False)
                    st.download_button(
                        label="Download Excel",
                        data=buffer.getvalue(),
                        file_name=f"fraud_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                elif export_format == "JSON":
                    json_data = df_export.to_json(orient='records', date_format='iso')
                    st.download_button(
                        label="Download JSON",
                        data=json_data,
                        file_name=f"fraud_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Help & Support
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">❓ Help & Support</div>', unsafe_allow_html=True)
        
        with st.expander("📖 Quick Guide"):
            st.markdown("""
                **Getting Started:**
                1. Upload your transaction data (CSV/Excel)
                2. Ensure columns include: Date, Amount, Vendor
                3. AI will automatically detect anomalies
                
                **Risk Levels:**
                - 🔴 **Critical** (>0.8): Immediate attention
                - 🟠 **High** (0.6-0.8): Priority review
                - 🟡 **Medium** (0.4-0.6): Standard review
                - 🟢 **Low** (<0.4): Normal activity
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer
        st.markdown("""
            <div style="text-align: center; padding: 2rem 0; color: var(--text-muted); font-size: 0.75rem;">
                <div>© 2025 FraudGuard AI</div>
                <div style="margin-top: 4px;">Enterprise Security Platform</div>
            </div>
        """, unsafe_allow_html=True)

def render_empty_state():
    """Render the empty state when no file is uploaded"""
    st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem;">
            <div style="font-size: 6rem; margin-bottom: 1.5rem; animation: float 3s ease-in-out infinite;">📊</div>
            <h2 style="font-size: 1.75rem; color: var(--text-primary); margin-bottom: 1rem;">
                Ready to Detect Fraud
            </h2>
            <p style="font-size: 1.1rem; color: var(--text-secondary); max-width: 500px; margin: 0 auto 2rem auto;">
                Upload your transaction ledger to begin AI-powered forensic analysis.
                We support CSV, Excel, and most common data formats.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="glass-card" style="text-align: center;">
                <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🤖</div>
                <h4 style="font-size: 1rem; margin-bottom: 0.5rem;">AI-Powered Detection</h4>
                <p style="font-size: 0.85rem; color: var(--text-secondary);">
                    Advanced machine learning algorithms identify subtle fraud patterns humans miss.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="glass-card" style="text-align: center;">
                <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">⚡</div>
                <h4 style="font-size: 1rem; margin-bottom: 0.5rem;">Real-Time Analysis</h4>
                <p style="font-size: 0.85rem; color: var(--text-secondary);">
                    Process thousands of transactions in seconds with instant risk scoring.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="glass-card" style="text-align: center;">
                <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">📈</div>
                <h4 style="font-size: 1rem; margin-bottom: 0.5rem;">Visual Insights</h4>
                <p style="font-size: 0.85rem; color: var(--text-secondary);">
                    Interactive 3D visualizations and drill-down analytics for deep investigation.
                </p>
            </div>
        """, unsafe_allow_html=True)

def render_footer():
    """Render the footer"""
    st.markdown("""
        <div class="footer">
            <div>Powered by <span class="footer-brand">FraudGuard AI</span> | Enterprise Security Platform</div>
            <div class="footer-links">
                <span>📧 support@fraudguard.ai</span>
                <span>📞 1-800-FRAUD-AI</span>
                <span>🔐 SOC 2 Type II Certified</span>
            </div>
            <div style="margin-top: 1rem; font-size: 0.75rem;">
                © 2025 FraudGuard AI. All rights reserved. | Privacy Policy | Terms of Service
            </div>
        </div>
    """, unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                           DATA PROCESSING                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def auto_detect_columns(df):
    """Auto-detect important columns in the dataframe"""
    columns = df.columns.tolist()
    lower_cols = [c.lower() for c in columns]
    
    # Date column detection
    date_keywords = ['date', 'time', 'datetime', 'timestamp', 'created', 'posted']
    date_col = None
    for kw in date_keywords:
        for i, col in enumerate(lower_cols):
            if kw in col:
                date_col = columns[i]
                break
        if date_col:
            break
    
    # Amount column detection
    amount_keywords = ['amount', 'value', 'total', 'cost', 'price', 'sum', 'charge']
    amount_col = None
    for kw in amount_keywords:
        for i, col in enumerate(lower_cols):
            if kw in col:
                amount_col = columns[i]
                break
        if amount_col:
            break
    
    # Vendor column detection
    vendor_keywords = ['vendor', 'merchant', 'payee', 'supplier', 'company', 'name', 'desc']
    vendor_col = None
    for kw in vendor_keywords:
        for i, col in enumerate(lower_cols):
            if kw in col:
                vendor_col = columns[i]
                break
        if vendor_col:
            break
    
    return date_col, amount_col, vendor_col

def process_data(df, date_col, amount_col, vendor_col):
    """Process data and calculate risk scores"""
    df_processed = df.copy()
    
    # Ensure amount is numeric
    df_processed[amount_col] = pd.to_numeric(df_processed[amount_col], errors='coerce').fillna(0)
    
    # Parse dates and extract features
    try:
        df_processed[date_col] = pd.to_datetime(df_processed[date_col], errors='coerce')
        df_processed['hour'] = df_processed[date_col].dt.hour
        df_processed['day_of_week'] = df_processed[date_col].dt.dayofweek
        df_processed['is_weekend'] = df_processed['day_of_week'].isin([5, 6])
        df_processed['month'] = df_processed[date_col].dt.month
    except Exception:
        df_processed['hour'] = 12
        df_processed['day_of_week'] = 0
        df_processed['is_weekend'] = False
        df_processed['month'] = 1
    
    if FRAUD_ENGINE_AVAILABLE:
        # Use the actual fraud forensics engine
        try:
            df_features = ff.prepare_features(
                df_processed, 
                time_col=date_col, 
                amount_col=amount_col, 
                id_cols=[vendor_col] if vendor_col else None
            )
            df_scored = ff.run_detectors(df_features, contamination=st.session_state.contamination_rate)
            df_final = ff.ensemble_scores(df_scored, score_cols=['iforest_score', 'lof_score'])
            alerts = ff.rules_engine(df_final, amount_col=amount_col, vendor_col=vendor_col)
            return df_final, alerts
        except Exception as e:
            st.warning(f"Fraud engine error: {e}. Using fallback analysis.")
    
    # Fallback: Simple risk scoring when fraud_forensics is not available
    df_processed['risk_score'] = df_processed.apply(
        lambda row: calculate_risk_score(
            amount=row[amount_col],
            hour=row.get('hour'),
            is_weekend=row.get('is_weekend', False),
            vendor=row.get(vendor_col) if vendor_col else None
        ),
        axis=1
    )
    
    df_processed['risk_explainer'] = df_processed.apply(
        lambda row: get_risk_explainer(row, amount_col),
        axis=1
    )
    
    # Generate alerts from high-risk transactions
    alerts = df_processed[df_processed['risk_score'] > 0.6].copy()
    
    return df_processed, alerts

def filter_dataframe(df, amount_col):
    """Apply filters from session state to dataframe"""
    df_filtered = df.copy()
    
    # Risk filter
    risk_filter = st.session_state.selected_risk_filter
    if risk_filter == "Critical (>0.8)":
        df_filtered = df_filtered[df_filtered['risk_score'] > 0.8]
    elif risk_filter == "High (>0.6)":
        df_filtered = df_filtered[df_filtered['risk_score'] > 0.6]
    elif risk_filter == "Medium (>0.4)":
        df_filtered = df_filtered[df_filtered['risk_score'] > 0.4]
    elif risk_filter == "Low (≤0.4)":
        df_filtered = df_filtered[df_filtered['risk_score'] <= 0.4]
    
    # Amount filter
    if amount_col in df_filtered.columns:
        df_filtered = df_filtered[
            (df_filtered[amount_col] >= st.session_state.min_amount) &
            (df_filtered[amount_col] <= st.session_state.max_amount)
        ]
    
    return df_filtered

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                           VISUALIZATION COMPONENTS                             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def create_risk_gauge(score):
    """Create a gauge chart for risk score"""
    color = "#10B981" if score < 0.4 else "#F59E0B" if score < 0.7 else "#EF4444"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 40], 'color': 'rgba(16, 185, 129, 0.2)'},
                {'range': [40, 70], 'color': 'rgba(245, 158, 11, 0.2)'},
                {'range': [70, 100], 'color': 'rgba(239, 68, 68, 0.2)'}
            ],
        },
        number={'suffix': '%', 'font': {'size': 40, 'color': color}}
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=200,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    
    return fig

def create_3d_scatter(df, date_col, amount_col, vendor_col):
    """Create an enhanced 3D scatter plot"""
    if 'hour' not in df.columns:
        df['hour'] = 12
    
    fig = px.scatter_3d(
        df.head(1000),  # Limit for performance
        x='hour',
        y=amount_col,
        z='risk_score',
        color='risk_score',
        color_continuous_scale=[
            [0, '#10B981'],
            [0.4, '#3B82F6'],
            [0.7, '#F59E0B'],
            [1, '#EF4444']
        ],
        opacity=0.8,
        hover_data=[vendor_col] if vendor_col else None,
        hover_name=vendor_col if vendor_col else None,
    )
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(
                title='Hour of Day',
                backgroundcolor="rgba(0,0,0,0)",
                gridcolor="rgba(100,100,100,0.2)",
                showbackground=True,
                zerolinecolor="rgba(100,100,100,0.2)"
            ),
            yaxis=dict(
                title='Amount ($)',
                backgroundcolor="rgba(0,0,0,0)",
                gridcolor="rgba(100,100,100,0.2)",
                showbackground=True
            ),
            zaxis=dict(
                title='Risk Score',
                backgroundcolor="rgba(0,0,0,0)",
                gridcolor="rgba(100,100,100,0.2)",
                showbackground=True
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=600,
        margin=dict(l=0, r=0, b=0, t=30),
        coloraxis_colorbar=dict(
            title="Risk",
            tickvals=[0, 0.25, 0.5, 0.75, 1],
            ticktext=['Low', '', 'Medium', '', 'High']
        )
    )
    
    return fig

def create_timeline_chart(df, date_col, amount_col, vendor_col):
    """Create an enhanced timeline scatter plot"""
    fig = px.scatter(
        df.head(500),
        x=date_col,
        y=amount_col,
        size='risk_score',
        color='risk_score',
        color_continuous_scale=[
            [0, '#10B981'],
            [0.5, '#3B82F6'],
            [1, '#EF4444']
        ],
        hover_data=[vendor_col, 'risk_score'] if vendor_col else ['risk_score'],
        size_max=25
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0.02)',
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(100,100,100,0.1)',
            title='Date'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(100,100,100,0.1)',
            title='Amount ($)'
        ),
        height=450,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    
    return fig

def create_vendor_heatmap(df, vendor_col, amount_col):
    """Create a vendor risk heatmap"""
    vendor_stats = df.groupby(vendor_col).agg({
        amount_col: ['sum', 'count', 'mean'],
        'risk_score': 'mean'
    }).round(2)
    vendor_stats.columns = ['Total Amount', 'Transaction Count', 'Avg Amount', 'Avg Risk']
    vendor_stats = vendor_stats.sort_values('Avg Risk', ascending=False).head(15)
    
    fig = px.bar(
        vendor_stats.reset_index(),
        x=vendor_col,
        y='Total Amount',
        color='Avg Risk',
        color_continuous_scale=[
            [0, '#10B981'],
            [0.5, '#F59E0B'],
            [1, '#EF4444']
        ],
        hover_data=['Transaction Count', 'Avg Amount', 'Avg Risk']
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(tickangle=45),
        height=400,
        margin=dict(l=20, r=20, t=30, b=100)
    )
    
    return fig

def create_risk_distribution(df):
    """Create a risk score distribution chart"""
    fig = px.histogram(
        df,
        x='risk_score',
        nbins=20,
        color_discrete_sequence=['#3B82F6']
    )
    
    # Add vertical lines for thresholds
    fig.add_vline(x=0.4, line_dash="dash", line_color="#F59E0B", annotation_text="Medium")
    fig.add_vline(x=0.7, line_dash="dash", line_color="#EF4444", annotation_text="High")
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title='Risk Score', gridcolor='rgba(100,100,100,0.1)'),
        yaxis=dict(title='Transaction Count', gridcolor='rgba(100,100,100,0.1)'),
        height=300,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    
    return fig

def create_hourly_heatmap(df, amount_col):
    """Create an hourly activity heatmap"""
    if 'hour' not in df.columns or 'day_of_week' not in df.columns:
        return None
    
    pivot = df.pivot_table(
        values='risk_score',
        index='day_of_week',
        columns='hour',
        aggfunc='mean'
    ).fillna(0)
    
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    fig = px.imshow(
        pivot,
        labels=dict(x="Hour", y="Day", color="Avg Risk"),
        x=[str(h) for h in range(24)],
        y=day_names[:len(pivot)],
        color_continuous_scale=[
            [0, '#10B981'],
            [0.5, '#F59E0B'],
            [1, '#EF4444']
        ],
        aspect='auto'
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=300,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    
    return fig

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                           MAIN APPLICATION                                     ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def main():
    """Main application entry point"""
    
    # Apply theme CSS
    st.markdown(get_theme_css(), unsafe_allow_html=True)
    st.markdown(SHARED_CSS, unsafe_allow_html=True)
    
    # Render sidebar
    render_sidebar()
    
    # Engine warning
    if not FRAUD_ENGINE_AVAILABLE:
        st.warning("⚠️ Advanced fraud detection engine not found. Using basic analysis mode. For full capabilities, ensure 'fraud_forensics.py' is in the same directory.")
    
    # Render hero section
    render_hero()
    
    # File Upload Section
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 1rem;">
                <span style="font-size: 0.85rem; font-weight: 600; color: var(--text-muted); 
                             text-transform: uppercase; letter-spacing: 0.1em;">
                    📤 Upload Transaction Data
                </span>
            </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Upload your transaction data",
            type=['csv', 'xlsx', 'xls'],
            label_visibility="collapsed",
            help="Supported formats: CSV, Excel (.xlsx, .xls)"
        )
    
    # Process uploaded file
    if uploaded_file:
        try:
            # Load data
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            if df.empty:
                st.error("❌ The uploaded file is empty. Please check your data.")
                st.stop()
            
            st.session_state.df = df
            
            # Auto-detect columns
            date_col, amount_col, vendor_col = auto_detect_columns(df)
            
            if not date_col or not amount_col:
                st.error("❌ Could not auto-detect required columns. Please ensure your data has Date and Amount columns.")
                
                with st.expander("🔧 Manual Column Mapping"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        date_col = st.selectbox("Date Column", df.columns.tolist())
                    with col2:
                        amount_col = st.selectbox("Amount Column", df.columns.tolist())
                    with col3:
                        vendor_col = st.selectbox("Vendor Column (optional)", ["None"] + df.columns.tolist())
                        if vendor_col == "None":
                            vendor_col = None
            
            # Store column mappings
            st.session_state.date_col = date_col
            st.session_state.amount_col = amount_col
            st.session_state.vendor_col = vendor_col
            
            # Run analysis if not already done
            if not st.session_state.analysis_complete:
                render_scanning_animation()
                
                df_analyzed, alerts = process_data(df, date_col, amount_col, vendor_col)
                
                st.session_state.df_analyzed = df_analyzed
                st.session_state.alerts = alerts
                st.session_state.analysis_complete = True
                
                # Add to history
                st.session_state.analysis_history.append({
                    'timestamp': datetime.now(),
                    'file_name': uploaded_file.name,
                    'transactions': len(df),
                    'high_risk': len(df_analyzed[df_analyzed['risk_score'] > 0.7])
                })
                
                st.rerun()
            
            # Get analyzed data
            df_analyzed = st.session_state.df_analyzed
            alerts = st.session_state.alerts
            
            # Apply filters
            df_filtered = filter_dataframe(df_analyzed, amount_col)
            
            # ═══════════════════════════════════════════════════════════════════
            # DASHBOARD METRICS
            # ═══════════════════════════════════════════════════════════════════
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Calculate statistics
            total_transactions = len(df_analyzed)
            total_volume = df_analyzed[amount_col].sum()
            high_risk_df = df_analyzed[df_analyzed['risk_score'] > 0.7]
            high_risk_count = len(high_risk_df)
            high_risk_volume = high_risk_df[amount_col].sum() if not high_risk_df.empty else 0
            avg_risk = df_analyzed['risk_score'].mean()
            critical_count = len(df_analyzed[df_analyzed['risk_score'] > 0.85])
            
            # Metric cards row
            m1, m2, m3, m4, m5 = st.columns(5)
            
            with m1:
                render_metric_card(
                    "📊", 
                    format_number(total_transactions),
                    "Transactions",
                    "primary",
                    subtext="Analyzed"
                )
            
            with m2:
                render_metric_card(
                    "💰",
                    format_currency(total_volume),
                    "Total Volume",
                    "primary"
                )
            
            with m3:
                render_metric_card(
                    "🚨",
                    str(high_risk_count),
                    "High Risk",
                    "danger",
                    trend="up" if high_risk_count > 5 else None,
                    trend_value=f"{(high_risk_count/total_transactions*100):.1f}%" if total_transactions > 0 else "0%"
                )
            
            with m4:
                render_metric_card(
                    "💸",
                    format_currency(high_risk_volume),
                    "At Risk",
                    "warning"
                )
            
            with m5:
                render_metric_card(
                    "🎯",
                    f"{avg_risk*100:.1f}%",
                    "Avg Risk Score",
                    "success" if avg_risk < 0.3 else "warning" if avg_risk < 0.5 else "danger"
                )
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # ═══════════════════════════════════════════════════════════════════
            # ALERTS SECTION
            # ═══════════════════════════════════════════════════════════════════
            
            if critical_count > 0:
                with st.expander(f"🚨 Critical Alerts ({critical_count})", expanded=True):
                    critical_df = df_analyzed[df_analyzed['risk_score'] > 0.85].head(5)
                    for _, row in critical_df.iterrows():
                        render_alert_card(
                            "critical",
                            f"High-Risk Transaction: {format_currency(row[amount_col])}",
                            row.get('risk_explainer', 'Multiple risk indicators detected'),
                            f"{vendor_col}: {row.get(vendor_col, 'Unknown')} | {row.get(date_col, 'N/A')}"
                        )
            
            # ═══════════════════════════════════════════════════════════════════
            # VISUALIZATION TABS
            # ═══════════════════════════════════════════════════════════════════
            
            tabs = st.tabs([
                "🔍 Forensic Explorer",
                "🌐 3D Risk Landscape", 
                "📈 Timeline Analysis",
                "🏢 Vendor Analytics",
                "📊 Risk Distribution",
                "🗓️ Activity Heatmap"
            ])
            
            # Tab 1: Forensic Explorer
            with tabs[0]:
                st.markdown("### 🔍 High Priority Investigations")
                st.markdown(f"*Showing {len(df_filtered):,} of {len(df_analyzed):,} transactions based on current filters*")
                
                # Sort by risk score
                df_display = df_filtered.sort_values('risk_score', ascending=False)
                
                # Select columns to display
                display_cols = [date_col, vendor_col, amount_col, 'risk_score', 'risk_explainer'] if vendor_col else [date_col, amount_col, 'risk_score', 'risk_explainer']
                display_cols = [c for c in display_cols if c in df_display.columns]
                
                st.dataframe(
                    df_display[display_cols].head(100),
                    column_config={
                        "risk_score": st.column_config.ProgressColumn(
                            "Risk Score",
                            help="AI-calculated risk probability (0-100%)",
                            format="%.0f%%",
                            min_value=0,
                            max_value=1,
                        ),
                        amount_col: st.column_config.NumberColumn(
                            "Amount",
                            format="$%.2f"
                        ),
                        date_col: st.column_config.DatetimeColumn(
                            "Date",
                            format="MMM DD, YYYY HH:mm"
                        ),
                        "risk_explainer": st.column_config.TextColumn(
                            "Risk Factors",
                            width="large"
                        )
                    },
                    use_container_width=True,
                    height=500,
                    hide_index=True
                )
            
            # Tab 2: 3D Risk Landscape
            with tabs[1]:
                st.markdown("### 🌐 Multidimensional Anomaly Visualization")
                st.markdown("*Explore transactions in 3D space: Hour × Amount × Risk Score*")
                
                fig_3d = create_3d_scatter(df_filtered, date_col, amount_col, vendor_col)
                st.plotly_chart(fig_3d, use_container_width=True)
            
            # Tab 3: Timeline Analysis
            with tabs[2]:
                st.markdown("### 📈 Temporal Risk Distribution")
                st.markdown("*Transaction amounts over time, sized by risk score*")
                
                fig_timeline = create_timeline_chart(df_filtered, date_col, amount_col, vendor_col)
                st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Tab 4: Vendor Analytics
            with tabs[3]:
                st.markdown("### 🏢 Vendor Risk Analysis")
                
                if vendor_col:
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        fig_vendor = create_vendor_heatmap(df_filtered, vendor_col, amount_col)
                        st.plotly_chart(fig_vendor, use_container_width=True)
                    
                    with col2:
                        st.markdown("#### Top Risk Vendors")
                        vendor_risk = df_filtered.groupby(vendor_col).agg({
                            'risk_score': 'mean',
                            amount_col: 'sum'
                        }).sort_values('risk_score', ascending=False).head(10)
                        
                        for vendor, data in vendor_risk.iterrows():
                            risk_color = "🔴" if data['risk_score'] > 0.7 else "🟡" if data['risk_score'] > 0.4 else "🟢"
                            st.markdown(f"""
                                <div style="padding: 0.5rem; margin-bottom: 0.5rem; 
                                            background: var(--glass-bg); border-radius: 8px;">
                                    <div style="font-weight: 600;">{risk_color} {vendor[:25]}</div>
                                    <div style="font-size: 0.8rem; color: var(--text-muted);">
                                        Risk: {data['risk_score']*100:.0f}% | Volume: {format_currency(data[amount_col])}
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("Vendor column not detected. Upload data with a Vendor/Merchant column for this analysis.")
            
            # Tab 5: Risk Distribution
            with tabs[4]:
                st.markdown("### 📊 Risk Score Distribution")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    fig_dist = create_risk_distribution(df_filtered)
                    st.plotly_chart(fig_dist, use_container_width=True)
                
                with col2:
                    st.markdown("#### Risk Breakdown")
                    
                    low_risk = len(df_filtered[df_filtered['risk_score'] <= 0.4])
                    med_risk = len(df_filtered[(df_filtered['risk_score'] > 0.4) & (df_filtered['risk_score'] <= 0.7)])
                    high_risk = len(df_filtered[df_filtered['risk_score'] > 0.7])
                    
                    st.markdown(f"""
                        <div class="glass-card">
                            <div style="margin-bottom: 1rem;">
                                <span style="color: #10B981; font-size: 1.5rem;">🟢</span>
                                <span style="font-weight: 600;">Low Risk</span>
                                <span style="float: right; font-weight: 700;">{low_risk:,}</span>
                            </div>
                            <div style="margin-bottom: 1rem;">
                                <span style="color: #F59E0B; font-size: 1.5rem;">🟡</span>
                                <span style="font-weight: 600;">Medium Risk</span>
                                <span style="float: right; font-weight: 700;">{med_risk:,}</span>
                            </div>
                            <div>
                                <span style="color: #EF4444; font-size: 1.5rem;">🔴</span>
                                <span style="font-weight: 600;">High Risk</span>
                                <span style="float: right; font-weight: 700;">{high_risk:,}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Tab 6: Activity Heatmap
            with tabs[5]:
                st.markdown("### 🗓️ Temporal Activity Patterns")
                st.markdown("*Average risk score by day of week and hour*")
                
                fig_heatmap = create_hourly_heatmap(df_filtered, amount_col)
                if fig_heatmap:
                    st.plotly_chart(fig_heatmap, use_container_width=True)
                else:
                    st.info("Unable to generate heatmap. Ensure your data has proper date/time information.")
            
            # ═══════════════════════════════════════════════════════════════════
            # EXECUTIVE SUMMARY
            # ═══════════════════════════════════════════════════════════════════
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            with st.expander("📋 Executive Summary", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                        ### Key Findings
                    """)
                    st.markdown(f"""
                        - **Total Transactions Analyzed:** {total_transactions:,}
                        - **Total Transaction Volume:** {format_currency(total_volume)}
                        - **High-Risk Transactions:** {high_risk_count:,} ({high_risk_count/total_transactions*100:.1f}%)
                        - **Value at Risk:** {format_currency(high_risk_volume)}
                        - **Average Risk Score:** {avg_risk*100:.1f}%
                        - **Critical Alerts:** {critical_count}
                    """)
                
                with col2:
                    st.markdown("""
                        ### Recommendations
                    """)
                    if high_risk_count > 0:
                        st.markdown("""
                            - 🔴 Review all critical and high-risk transactions immediately
                            - 🔍 Investigate unusual vendor patterns identified
                            - 📊 Implement additional controls for off-hours transactions
                            - 🔐 Consider enhanced approval workflows for high-value items
                        """)
                    else:
                        st.markdown("""
                            - ✅ No immediate action required
                            - 📊 Continue regular monitoring
                            - 🔄 Schedule periodic deep-dive reviews
                        """)
        
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.markdown("""
                <div style="text-align: center; padding: 2rem; color: var(--text-muted);">
                    <p>Please ensure your file contains the following columns:</p>
                    <p><strong>Date</strong> (or similar), <strong>Amount</strong> (or similar), <strong>Vendor</strong> (optional)</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander("🔧 Debug Information"):
                st.code(str(e))
    
    else:
        # No file uploaded - show empty state
        render_empty_state()
    
    # Render footer
    render_footer()

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                           RUN APPLICATION                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

if __name__ == "__main__":
    main()