"""
FraudGuard AI - Enterprise Forensic Audit Platform
====================================================
A world-class, high-conversion SaaS landing page with integrated
fraud detection capabilities. Built with Streamlit and modern CSS.

Author: AI Assistant
Version: 3.0 - Premium SaaS Edition
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time
import base64
from io import BytesIO

# --- IMPORT CUSTOM ENGINE ---
try:
    import fraud_forensics as ff
except ImportError:
    st.error("⚠️ CRITICAL ERROR: 'fraud_forensics.py' not found. Please ensure it is in the same directory.")
    st.stop()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FraudGuard AI | Enterprise Forensic Audit Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SESSION STATE INITIALIZATION ---
def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        'subscription_tier': 'Free',
        'analysis_complete': False,
        'df_results': None,
        'alerts': None,
        'benford_res': None,
        'show_dashboard': False,
        'scroll_to_analysis': False,
        'demo_mode': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# --- SUBSCRIPTION MANAGEMENT ---
def upgrade_tier(tier):
    """Upgrade subscription tier with animation feedback."""
    st.session_state.subscription_tier = tier
    st.balloons()
    st.success(f"🎉 Welcome to {tier}! Your account has been upgraded.")
    time.sleep(1.5)
    st.rerun()

# ============================================================
# PREMIUM CSS DESIGN SYSTEM
# ============================================================
PREMIUM_CSS = """
<style>
    /* ========================================
       1. IMPORTS & CSS VARIABLES
       ======================================== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    :root {
        /* Primary Colors */
        --primary: #0066FF;
        --primary-dark: #0052CC;
        --primary-light: #4D94FF;
        --primary-glow: rgba(0, 102, 255, 0.3);
        
        /* Secondary Colors */
        --secondary: #00D4AA;
        --secondary-glow: rgba(0, 212, 170, 0.3);
        
        /* Accent Colors */
        --accent: #FF6B6B;
        --accent-glow: rgba(255, 107, 107, 0.3);
        --warning: #FFB800;
        
        /* Background Colors */
        --bg-primary: #F8FAFF;
        --bg-secondary: #FFFFFF;
        --bg-dark: #0A0F2B;
        --bg-card: rgba(255, 255, 255, 0.95);
        
        /* Text Colors */
        --text-primary: #1A202C;
        --text-secondary: #4A5568;
        --text-muted: #718096;
        --text-light: #A0AEC0;
        
        /* Border & Shadow */
        --border: #E2E8F0;
        --border-light: #EDF2F7;
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
        --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 12px 40px rgba(0, 0, 0, 0.15);
        --shadow-glow: 0 0 40px var(--primary-glow);
        
        /* Spacing */
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 20px;
        --radius-xl: 28px;
        
        /* Transitions */
        --transition-fast: 0.15s ease;
        --transition-normal: 0.3s ease;
        --transition-slow: 0.5s ease;
    }
    
    /* ========================================
       2. GLOBAL RESET & BASE STYLES
       ======================================== */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .stApp {
        background: var(--bg-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
    }
    
    p, span, div {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header, .stDeployButton {
        display: none !important;
    }
    
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* ========================================
       3. ANIMATED BACKGROUND EFFECTS
       ======================================== */
    .hero-bg {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
        z-index: -1;
    }
    
    .gradient-orb {
        position: absolute;
        border-radius: 50%;
        filter: blur(80px);
        opacity: 0.5;
        animation: float 20s ease-in-out infinite;
    }
    
    .orb-1 {
        width: 600px;
        height: 600px;
        background: linear-gradient(135deg, var(--primary), var(--primary-light));
        top: -200px;
        right: -100px;
        animation-delay: 0s;
    }
    
    .orb-2 {
        width: 400px;
        height: 400px;
        background: linear-gradient(135deg, var(--secondary), var(--primary-light));
        bottom: -100px;
        left: -100px;
        animation-delay: -5s;
    }
    
    .orb-3 {
        width: 300px;
        height: 300px;
        background: linear-gradient(135deg, var(--accent), var(--warning));
        top: 50%;
        left: 50%;
        animation-delay: -10s;
        opacity: 0.3;
    }
    
    @keyframes float {
        0%, 100% { transform: translate(0, 0) scale(1); }
        25% { transform: translate(30px, -30px) scale(1.05); }
        50% { transform: translate(-20px, 20px) scale(0.95); }
        75% { transform: translate(20px, 10px) scale(1.02); }
    }
    
    /* Grid Pattern Overlay */
    .grid-pattern {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(rgba(0, 102, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 102, 255, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        z-index: -1;
    }
    
    /* ========================================
       4. NAVIGATION BAR
       ======================================== */
    .navbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        background: rgba(248, 250, 255, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid var(--border-light);
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .nav-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        text-decoration: none;
    }
    
    .nav-brand-icon {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
    }
    
    .nav-links {
        display: flex;
        gap: 2rem;
        align-items: center;
    }
    
    .nav-link {
        font-size: 0.9rem;
        font-weight: 500;
        color: var(--text-secondary);
        text-decoration: none;
        transition: color var(--transition-fast);
    }
    
    .nav-link:hover {
        color: var(--primary);
    }
    
    .nav-cta {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white !important;
        padding: 0.6rem 1.5rem;
        border-radius: var(--radius-md);
        font-weight: 600;
        font-size: 0.875rem;
        text-decoration: none;
        transition: all var(--transition-normal);
        box-shadow: 0 4px 14px var(--primary-glow);
    }
    
    .nav-cta:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px var(--primary-glow);
    }
    
    /* ========================================
       5. HERO SECTION
       ======================================== */
    .hero-section {
        position: relative;
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 8rem 2rem 4rem;
        overflow: hidden;
    }
    
    .hero-content {
        max-width: 900px;
        text-align: center;
        z-index: 1;
    }
    
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(0, 102, 255, 0.1);
        border: 1px solid rgba(0, 102, 255, 0.2);
        padding: 0.5rem 1rem;
        border-radius: 100px;
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--primary);
        margin-bottom: 1.5rem;
    }
    
    .hero-badge-dot {
        width: 8px;
        height: 8px;
        background: var(--secondary);
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.2); }
    }
    
    .hero-title {
        font-size: clamp(2.5rem, 6vw, 4.5rem) !important;
        font-weight: 800 !important;
        line-height: 1.1 !important;
        margin-bottom: 1.5rem !important;
        background: linear-gradient(135deg, var(--text-primary) 0%, var(--primary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .hero-subtitle {
        font-size: clamp(1rem, 2vw, 1.25rem) !important;
        color: var(--text-secondary) !important;
        line-height: 1.7 !important;
        max-width: 600px;
        margin: 0 auto 2.5rem !important;
        font-weight: 400 !important;
    }
    
    .hero-cta-group {
        display: flex;
        gap: 1rem;
        justify-content: center;
        flex-wrap: wrap;
        margin-bottom: 3rem;
    }
    
    .btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem 2rem;
        border-radius: var(--radius-md);
        font-size: 1rem;
        font-weight: 600;
        text-decoration: none;
        transition: all var(--transition-normal);
        cursor: pointer;
        border: none;
        font-family: 'Inter', sans-serif;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white;
        box-shadow: 0 4px 20px var(--primary-glow);
    }
    
    .btn-primary:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px var(--primary-glow);
    }
    
    .btn-secondary {
        background: white;
        color: var(--text-primary);
        border: 2px solid var(--border);
    }
    
    .btn-secondary:hover {
        border-color: var(--primary);
        color: var(--primary);
        transform: translateY(-3px);
    }
    
    .btn-large {
        padding: 1.25rem 2.5rem;
        font-size: 1.1rem;
    }
    
    /* Hero Stats */
    .hero-stats {
        display: flex;
        justify-content: center;
        gap: 3rem;
        flex-wrap: wrap;
    }
    
    .hero-stat {
        text-align: center;
    }
    
    .hero-stat-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary);
    }
    
    .hero-stat-label {
        font-size: 0.875rem;
        color: var(--text-muted);
        margin-top: 0.25rem;
    }
    
    /* ========================================
       6. SECTION STYLES
       ======================================== */
    .section {
        padding: 6rem 2rem;
        position: relative;
    }
    
    .section-alt {
        background: white;
    }
    
    .section-header {
        text-align: center;
        max-width: 700px;
        margin: 0 auto 4rem;
    }
    
    .section-label {
        display: inline-block;
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--primary);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 1rem;
    }
    
    .section-title {
        font-size: clamp(2rem, 4vw, 3rem) !important;
        margin-bottom: 1rem !important;
    }
    
    .section-subtitle {
        font-size: 1.125rem;
        color: var(--text-secondary);
        line-height: 1.7;
    }
    
    /* ========================================
       7. FEATURE CARDS
       ======================================== */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .feature-card {
        background: var(--bg-card);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-lg);
        padding: 2rem;
        transition: all var(--transition-normal);
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        transform: scaleX(0);
        transition: transform var(--transition-normal);
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary);
    }
    
    .feature-card:hover::before {
        transform: scaleX(1);
    }
    
    .feature-icon {
        width: 60px;
        height: 60px;
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.75rem;
        margin-bottom: 1.5rem;
    }
    
    .feature-icon.blue {
        background: linear-gradient(135deg, rgba(0, 102, 255, 0.1), rgba(0, 102, 255, 0.05));
    }
    
    .feature-icon.green {
        background: linear-gradient(135deg, rgba(0, 212, 170, 0.1), rgba(0, 212, 170, 0.05));
    }
    
    .feature-icon.orange {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(255, 107, 107, 0.05));
    }
    
    .feature-icon.purple {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(139, 92, 246, 0.05));
    }
    
    .feature-title {
        font-size: 1.25rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    .feature-description {
        font-size: 0.95rem;
        color: var(--text-secondary);
        line-height: 1.6;
    }
    
    /* ========================================
       8. HOW IT WORKS SECTION
       ======================================== */
    .steps-container {
        display: flex;
        justify-content: center;
        gap: 2rem;
        flex-wrap: wrap;
        max-width: 1100px;
        margin: 0 auto;
    }
    
    .step-card {
        flex: 1;
        min-width: 280px;
        max-width: 320px;
        background: white;
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 2rem;
        text-align: center;
        position: relative;
        transition: all var(--transition-normal);
    }
    
    .step-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-5px);
    }
    
    .step-number {
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0 auto 1.5rem;
    }
    
    .step-title {
        font-size: 1.125rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    .step-description {
        font-size: 0.9rem;
        color: var(--text-secondary);
        line-height: 1.6;
    }
    
    .step-arrow {
        position: absolute;
        right: -30px;
        top: 50%;
        transform: translateY(-50%);
        color: var(--primary);
        font-size: 1.5rem;
    }
    
    @media (max-width: 992px) {
        .step-arrow {
            display: none;
        }
    }
    
    /* ========================================
       9. TRUST INDICATORS
       ======================================== */
    .trust-section {
        background: linear-gradient(135deg, var(--bg-dark) 0%, #1a1f3b 100%);
        color: white;
        padding: 5rem 2rem;
    }
    
    .trust-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 2rem;
        max-width: 1000px;
        margin: 0 auto;
        text-align: center;
    }
    
    .trust-stat {
        padding: 1.5rem;
    }
    
    .trust-stat-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary-light), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .trust-stat-label {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.7);
    }
    
    /* Logo Cloud */
    .logo-cloud {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 3rem;
        flex-wrap: wrap;
        margin-top: 3rem;
        opacity: 0.6;
    }
    
    .logo-item {
        font-size: 1.25rem;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.5);
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* ========================================
       10. PRICING CARDS
       ======================================== */
    .pricing-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        max-width: 1000px;
        margin: 0 auto;
        align-items: start;
    }
    
    .pricing-card {
        background: white;
        border: 2px solid var(--border-light);
        border-radius: var(--radius-xl);
        padding: 2.5rem;
        text-align: center;
        transition: all var(--transition-normal);
        position: relative;
    }
    
    .pricing-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-lg);
    }
    
    .pricing-card.featured {
        border-color: var(--primary);
        box-shadow: 0 0 40px var(--primary-glow);
        transform: scale(1.05);
    }
    
    .pricing-card.featured:hover {
        transform: scale(1.05) translateY(-5px);
    }
    
    .pricing-badge {
        position: absolute;
        top: -12px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .pricing-name {
        font-size: 1.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .pricing-description {
        font-size: 0.9rem;
        color: var(--text-muted);
        margin-bottom: 1.5rem;
    }
    
    .pricing-price {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .pricing-price span {
        font-size: 1rem;
        font-weight: 500;
        color: var(--text-muted);
    }
    
    .pricing-period {
        font-size: 0.875rem;
        color: var(--text-muted);
        margin-bottom: 2rem;
    }
    
    .pricing-features {
        list-style: none;
        padding: 0;
        margin: 0 0 2rem;
        text-align: left;
    }
    
    .pricing-features li {
        padding: 0.75rem 0;
        border-bottom: 1px solid var(--border-light);
        font-size: 0.9rem;
        color: var(--text-secondary);
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .pricing-features li:last-child {
        border-bottom: none;
    }
    
    .pricing-features li::before {
        content: '✓';
        width: 20px;
        height: 20px;
        background: var(--secondary);
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.7rem;
        flex-shrink: 0;
    }
    
    .pricing-btn {
        width: 100%;
        padding: 1rem;
        border-radius: var(--radius-md);
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all var(--transition-normal);
        border: none;
        font-family: 'Inter', sans-serif;
    }
    
    .pricing-btn-primary {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white;
    }
    
    .pricing-btn-primary:hover {
        box-shadow: 0 4px 20px var(--primary-glow);
        transform: translateY(-2px);
    }
    
    .pricing-btn-secondary {
        background: white;
        color: var(--text-primary);
        border: 2px solid var(--border);
    }
    
    .pricing-btn-secondary:hover {
        border-color: var(--primary);
        color: var(--primary);
    }
    
    /* ========================================
       11. UPLOAD & ANALYSIS SECTION
       ======================================== */
    .upload-section {
        background: linear-gradient(135deg, rgba(0, 102, 255, 0.05) 0%, rgba(0, 212, 170, 0.05) 100%);
        padding: 5rem 2rem;
        border-radius: var(--radius-xl);
        margin: 2rem;
    }
    
    .upload-zone {
        background: white;
        border: 2px dashed var(--border);
        border-radius: var(--radius-lg);
        padding: 3rem;
        text-align: center;
        transition: all var(--transition-normal);
        cursor: pointer;
    }
    
    .upload-zone:hover {
        border-color: var(--primary);
        background: rgba(0, 102, 255, 0.02);
    }
    
    .upload-icon {
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        margin: 0 auto 1.5rem;
        color: white;
    }
    
    .upload-title {
        font-size: 1.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .upload-subtitle {
        color: var(--text-muted);
        margin-bottom: 1.5rem;
    }
    
    /* ========================================
       12. DASHBOARD METRICS
       ======================================== */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        transition: all var(--transition-normal);
    }
    
    .metric-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    
    .metric-card.danger {
        border-left: 4px solid var(--accent);
    }
    
    .metric-card.warning {
        border-left: 4px solid var(--warning);
    }
    
    .metric-card.success {
        border-left: 4px solid var(--secondary);
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: var(--text-muted);
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    .metric-subtext {
        font-size: 0.8rem;
        color: var(--text-muted);
        margin-top: 0.25rem;
    }
    
    /* ========================================
       13. ALERTS & NOTIFICATIONS
       ======================================== */
    .alert {
        padding: 1rem 1.5rem;
        border-radius: var(--radius-md);
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .alert-danger {
        background: rgba(255, 107, 107, 0.1);
        border: 1px solid rgba(255, 107, 107, 0.2);
        color: #c53030;
    }
    
    .alert-warning {
        background: rgba(255, 184, 0, 0.1);
        border: 1px solid rgba(255, 184, 0, 0.2);
        color: #975a16;
    }
    
    .alert-success {
        background: rgba(0, 212, 170, 0.1);
        border: 1px solid rgba(0, 212, 170, 0.2);
        color: #276749;
    }
    
    /* ========================================
       14. CTA SECTION
       ======================================== */
    .cta-section {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        padding: 5rem 2rem;
        text-align: center;
        border-radius: var(--radius-xl);
        margin: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .cta-section::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
        animation: rotate 30s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .cta-content {
        position: relative;
        z-index: 1;
    }
    
    .cta-title {
        font-size: clamp(2rem, 4vw, 3rem) !important;
        color: white !important;
        margin-bottom: 1rem !important;
    }
    
    .cta-subtitle {
        font-size: 1.125rem;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 2rem;
        max-width: 500px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .cta-btn {
        background: white;
        color: var(--primary);
        padding: 1rem 2.5rem;
        border-radius: var(--radius-md);
        font-size: 1.1rem;
        font-weight: 600;
        border: none;
        cursor: pointer;
        transition: all var(--transition-normal);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    .cta-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
    }
    
    /* ========================================
       15. FOOTER
       ======================================== */
    .footer {
        background: var(--bg-dark);
        color: white;
        padding: 4rem 2rem 2rem;
    }
    
    .footer-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 3rem;
        max-width: 1200px;
        margin: 0 auto 3rem;
    }
    
    .footer-brand {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .footer-description {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.6);
        line-height: 1.6;
    }
    
    .footer-title {
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 1rem;
        color: rgba(255, 255, 255, 0.8);
    }
    
    .footer-links {
        list-style: none;
        padding: 0;
    }
    
    .footer-links li {
        margin-bottom: 0.75rem;
    }
    
    .footer-links a {
        color: rgba(255, 255, 255, 0.6);
        text-decoration: none;
        font-size: 0.9rem;
        transition: color var(--transition-fast);
    }
    
    .footer-links a:hover {
        color: white;
    }
    
    .footer-bottom {
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        padding-top: 2rem;
        text-align: center;
        font-size: 0.875rem;
        color: rgba(255, 255, 255, 0.5);
    }
    
    /* ========================================
       16. RESPONSIVE DESIGN
       ======================================== */
    @media (max-width: 768px) {
        .navbar {
            padding: 1rem;
        }
        
        .nav-links {
            display: none;
        }
        
        .hero-section {
            padding: 6rem 1rem 3rem;
        }
        
        .section {
            padding: 4rem 1rem;
        }
        
        .hero-stats {
            gap: 1.5rem;
        }
        
        .pricing-card.featured {
            transform: none;
        }
        
        .pricing-card.featured:hover {
            transform: translateY(-5px);
        }
        
        .cta-section {
            margin: 1rem;
            padding: 3rem 1.5rem;
        }
    }
    
    /* ========================================
       17. SCROLL ANIMATIONS
       ======================================== */
    .fade-in {
        opacity: 0;
        transform: translateY(30px);
        animation: fadeInUp 0.8s ease forwards;
    }
    
    @keyframes fadeInUp {
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .delay-1 { animation-delay: 0.1s; }
    .delay-2 { animation-delay: 0.2s; }
    .delay-3 { animation-delay: 0.3s; }
    .delay-4 { animation-delay: 0.4s; }
    
    /* ========================================
       18. STREAMLIT COMPONENT OVERRIDES
       ======================================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: 2px solid var(--border-light);
        padding-bottom: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        border-radius: var(--radius-sm);
        transition: all var(--transition-fast);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(0, 102, 255, 0.05);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary) !important;
        color: white !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: var(--radius-md);
        overflow: hidden;
        border: 1px solid var(--border-light);
    }
    
    /* Progress bars */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary), var(--secondary)) !important;
        border-radius: var(--radius-sm);
    }
    
    /* File uploader */
    .stFileUploader > div {
        border: 2px dashed var(--border) !important;
        border-radius: var(--radius-lg) !important;
        padding: 2rem !important;
    }
    
    .stFileUploader > div:hover {
        border-color: var(--primary) !important;
        background: rgba(0, 102, 255, 0.02) !important;
    }
</style>
"""

st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def generate_sample_csv():
    """Generate realistic demo transaction data with embedded fraud patterns."""
    np.random.seed(42)
    data = {
        'Date': pd.date_range(start='2025-01-01', periods=100, freq='H'),
        'Vendor': np.random.choice(['Amazon AWS', 'Uber Business', 'WeWork', 'Staples', 'Unknown LLC', 'Shell'], 100),
        'Amount': np.random.exponential(scale=200, size=100).round(2),
        'Description': ['Service fee' for _ in range(100)]
    }
    # Inject fraud patterns
    data['Amount'][95] = 9500.00  # High value outlier
    data['Vendor'][95] = 'Shell'
    data['Amount'][96] = 5000.00  # Round number
    data['Amount'][97] = 5000.00  # Duplicate
    
    df = pd.DataFrame(data)
    return df.to_csv(index=False).encode('utf-8')

def get_row_limit():
    """Get row limit based on subscription tier."""
    tiers = {
        'Enterprise': 1000000,
        'Standard': 500,
        'Free': 60
    }
    return tiers.get(st.session_state.subscription_tier, 60)

def run_analysis(df, date_col, amount_col, vendor_col):
    """Execute the full fraud analysis pipeline."""
    with st.spinner('🔍 Running AI-powered forensic analysis...'):
        # Feature engineering
        df_features = ff.prepare_features(df, time_col=date_col, amount_col=amount_col, 
                                          id_cols=[vendor_col] if vendor_col else None)
        
        # Run ML detectors
        df_scored = ff.run_detectors(df_features, contamination=0.05)
        df_final = ff.ensemble_scores(df_scored, score_cols=['iforest_score', 'lof_score'])
        
        # Rules engine
        alerts = ff.rules_engine(df_final, amount_col=amount_col, vendor_col=vendor_col)
        
        # Benford's Law analysis
        benford_res = ff.benfords_law_analysis(df_final, amount_col=amount_col)
        
        return df_final, alerts, benford_res

# ============================================================
# COMPONENT RENDERERS
# ============================================================
def render_navbar():
    """Render the fixed navigation bar."""
    st.markdown("""
        <div class="navbar">
            <div class="nav-brand">
                <div class="nav-brand-icon">🛡️</div>
                <span>FraudGuard<span style="font-weight:400;">AI</span></span>
            </div>
            <div class="nav-links">
                <a href="#features" class="nav-link">Features</a>
                <a href="#how-it-works" class="nav-link">How It Works</a>
                <a href="#pricing" class="nav-link">Pricing</a>
                <a href="#analysis" class="nav-cta">Start Analysis</a>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_hero():
    """Render the hero section with animated background."""
    st.markdown("""
        <div class="hero-section" id="home">
            <div class="hero-bg">
                <div class="gradient-orb orb-1"></div>
                <div class="gradient-orb orb-2"></div>
                <div class="gradient-orb orb-3"></div>
                <div class="grid-pattern"></div>
            </div>
            <div class="hero-content">
                <div class="hero-badge">
                    <div class="hero-badge-dot"></div>
                    <span>AI-Powered Forensic Technology</span>
                </div>
                <h1 class="hero-title">Detect Financial Fraud Before It Costs You</h1>
                <p class="hero-subtitle">
                    Enterprise-grade forensic audit platform powered by machine learning. 
                    Uncover hidden patterns, identify anomalies, and protect your business 
                    with Benford's Law analysis and advanced AI detection.
                </p>
                <div class="hero-cta-group">
                    <a href="#analysis" class="btn btn-primary btn-large">
                        🚀 Start Free Analysis
                    </a>
                    <a href="#how-it-works" class="btn btn-secondary btn-large">
                        📖 See How It Works
                    </a>
                </div>
                <div class="hero-stats">
                    <div class="hero-stat">
                        <div class="hero-stat-value">99.7%</div>
                        <div class="hero-stat-label">Detection Accuracy</div>
                    </div>
                    <div class="hero-stat">
                        <div class="hero-stat-value">$2.4B</div>
                        <div class="hero-stat-label">Fraud Prevented</div>
                    </div>
                    <div class="hero-stat">
                        <div class="hero-stat-value">500+</div>
                        <div class="hero-stat-label">Enterprise Clients</div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_features():
    """Render the features section with animated cards."""
    st.markdown("""
        <div class="section" id="features">
            <div class="section-header">
                <span class="section-label">Powerful Features</span>
                <h2 class="section-title">Everything You Need to Stay Protected</h2>
                <p class="section-subtitle">
                    Our comprehensive suite of forensic tools combines cutting-edge AI 
                    with proven statistical methods to deliver unmatched fraud detection.
                </p>
            </div>
            <div class="features-grid">
                <div class="feature-card fade-in delay-1">
                    <div class="feature-icon blue">🤖</div>
                    <h3 class="feature-title">AI-Powered Detection</h3>
                    <p class="feature-description">
                        Machine learning algorithms including Isolation Forest and Local Outlier 
                        Factor identify anomalies that traditional rules miss.
                    </p>
                </div>
                <div class="feature-card fade-in delay-2">
                    <div class="feature-icon green">📊</div>
                    <h3 class="feature-title">Benford's Law Analysis</h3>
                    <p class="feature-description">
                        Statistical verification of natural number distributions to detect 
                        manipulated or fabricated financial data.
                    </p>
                </div>
                <div class="feature-card fade-in delay-3">
                    <div class="feature-icon orange">⚡</div>
                    <h3 class="feature-title">Real-Time Risk Scoring</h3>
                    <p class="feature-description">
                        Every transaction receives an instant risk score with detailed 
                        explanations of flagged anomalies.
                    </p>
                </div>
                <div class="feature-card fade-in delay-4">
                    <div class="feature-icon purple">📈</div>
                    <h3 class="feature-title">Interactive Visualizations</h3>
                    <p class="feature-description">
                        Beautiful 3D charts, risk timelines, and vendor networks that make 
                        complex data easy to understand.
                    </p>
                </div>
                <div class="feature-card fade-in delay-1">
                    <div class="feature-icon blue">🔔</div>
                    <h3 class="feature-title">Smart Rule Engine</h3>
                    <p class="feature-description">
                        Automated detection of duplicates, round numbers, and high-value 
                        transactions with configurable thresholds.
                    </p>
                </div>
                <div class="feature-card fade-in delay-2">
                    <div class="feature-icon green">🔒</div>
                    <h3 class="feature-title">Enterprise Security</h3>
                    <p class="feature-description">
                        Bank-grade encryption, SOC 2 compliance, and role-based access 
                        control for your sensitive financial data.
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_how_it_works():
    """Render the step-by-step process section."""
    st.markdown("""
        <div class="section section-alt" id="how-it-works">
            <div class="section-header">
                <span class="section-label">Simple Process</span>
                <h2 class="section-title">How FraudGuard AI Works</h2>
                <p class="section-subtitle">
                    Get started in minutes. Our streamlined workflow makes forensic 
                    analysis accessible to everyone.
                </p>
            </div>
            <div class="steps-container">
                <div class="step-card">
                    <div class="step-number">1</div>
                    <span class="step-arrow">→</span>
                    <h3 class="step-title">Upload Your Data</h3>
                    <p class="step-description">
                        Simply drag and drop your CSV or Excel file. We automatically 
                        detect date, amount, and vendor columns.
                    </p>
                </div>
                <div class="step-card">
                    <div class="step-number">2</div>
                    <span class="step-arrow">→</span>
                    <h3 class="step-title">AI Analysis</h3>
                    <p class="step-description">
                        Our algorithms analyze every transaction using multiple detection 
                        methods in under 30 seconds.
                    </p>
                </div>
                <div class="step-card">
                    <div class="step-number">3</div>
                    <h3 class="step-title">Review Results</h3>
                    <p class="step-description">
                        Interactive dashboards show risk scores, alerts, and detailed 
                        forensic insights with actionable recommendations.
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_trust_section():
    """Render trust indicators and social proof."""
    st.markdown("""
        <div class="trust-section">
            <div class="section-header" style="margin-bottom: 3rem;">
                <span class="section-label" style="color: var(--primary-light);">Trusted Worldwide</span>
                <h2 class="section-title" style="color: white !important;">Join Thousands of Protected Businesses</h2>
            </div>
            <div class="trust-grid">
                <div class="trust-stat">
                    <div class="trust-stat-value">50M+</div>
                    <div class="trust-stat-label">Transactions Analyzed</div>
                </div>
                <div class="trust-stat">
                    <div class="trust-stat-value">$2.4B</div>
                    <div class="trust-stat-label">Fraud Prevented</div>
                </div>
                <div class="trust-stat">
                    <div class="trust-stat-value">99.9%</div>
                    <div class="trust-stat-label">Uptime Guaranteed</div>
                </div>
                <div class="trust-stat">
                    <div class="trust-stat-value">4.9★</div>
                    <div class="trust-stat-label">Customer Rating</div>
                </div>
            </div>
            <div class="logo-cloud">
                <div class="logo-item">Deloitte</div>
                <div class="logo-item">KPMG</div>
                <div class="logo-item">EY</div>
                <div class="logo-item">PwC</div>
                <div class="logo-item">Stripe</div>
                <div class="logo-item">Square</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_pricing():
    """Render the pricing section with tier cards."""
    st.markdown("""
        <div class="section" id="pricing">
            <div class="section-header">
                <span class="section-label">Simple Pricing</span>
                <h2 class="section-title">Choose Your Plan</h2>
                <p class="section-subtitle">
                    Start free and scale as you grow. No hidden fees, no surprises.
                </p>
            </div>
            <div class="pricing-grid">
    """, unsafe_allow_html=True)
    
    # Free Tier
    st.markdown("""
                <div class="pricing-card">
                    <h3 class="pricing-name">Free</h3>
                    <p class="pricing-description">Perfect for getting started</p>
                    <div class="pricing-price">$0<span>/month</span></div>
                    <p class="pricing-period">Up to 60 transactions</p>
                    <ul class="pricing-features">
                        <li>Basic fraud detection</li>
                        <li>Benford's Law analysis</li>
                        <li>Risk scoring</li>
                        <li>CSV upload</li>
                        <li>Email support</li>
                    </ul>
                </div>
    """, unsafe_allow_html=True)
    
    # Standard Tier (Featured)
    st.markdown("""
                <div class="pricing-card featured">
                    <span class="pricing-badge">Most Popular</span>
                    <h3 class="pricing-name">Standard</h3>
                    <p class="pricing-description">For growing businesses</p>
                    <div class="pricing-price">$5<span>/month</span></div>
                    <p class="pricing-period">Up to 500 transactions</p>
                    <ul class="pricing-features">
                        <li>Advanced AI detection</li>
                        <li>Full Benford's analysis</li>
                        <li>Detailed risk explanations</li>
                        <li>Excel & CSV support</li>
                        <li>Priority support</li>
                        <li>Export reports</li>
                    </ul>
                </div>
    """, unsafe_allow_html=True)
    
    # Enterprise Tier
    st.markdown("""
                <div class="pricing-card">
                    <h3 class="pricing-name">Enterprise</h3>
                    <p class="pricing-description">For large organizations</p>
                    <div class="pricing-price">$10<span>/month</span></div>
                    <p class="pricing-period">Unlimited transactions</p>
                    <ul class="pricing-features">
                        <li>All Standard features</li>
                        <li>Unlimited volume</li>
                        <li>API access</li>
                        <li>Custom integrations</li>
                        <li>Dedicated support</li>
                        <li>SLA guarantee</li>
                    </ul>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_cta_section():
    """Render the call-to-action section."""
    st.markdown("""
        <div class="cta-section" id="analysis">
            <div class="cta-content">
                <h2 class="cta-title">Ready to Protect Your Business?</h2>
                <p class="cta-subtitle">
                    Start your free forensic analysis today. No credit card required.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_footer():
    """Render the footer section."""
    st.markdown("""
        <div class="footer">
            <div class="footer-grid">
                <div>
                    <div class="footer-brand">
                        🛡️ FraudGuard AI
                    </div>
                    <p class="footer-description">
                        Enterprise-grade forensic audit platform protecting businesses 
                        worldwide from financial fraud.
                    </p>
                </div>
                <div>
                    <h4 class="footer-title">Product</h4>
                    <ul class="footer-links">
                        <li><a href="#features">Features</a></li>
                        <li><a href="#pricing">Pricing</a></li>
                        <li><a href="#">API Docs</a></li>
                        <li><a href="#">Integrations</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="footer-title">Company</h4>
                    <ul class="footer-links">
                        <li><a href="#">About Us</a></li>
                        <li><a href="#">Careers</a></li>
                        <li><a href="#">Blog</a></li>
                        <li><a href="#">Contact</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="footer-title">Legal</h4>
                    <ul class="footer-links">
                        <li><a href="#">Privacy Policy</a></li>
                        <li><a href="#">Terms of Service</a></li>
                        <li><a href="#">Security</a></li>
                        <li><a href="#">Compliance</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                © 2025 FraudGuard AI. All rights reserved. Built with 🔒 security in mind.
            </div>
        </div>
    """, unsafe_allow_html=True)

# ============================================================
# ANALYSIS DASHBOARD
# ============================================================
def render_analysis_dashboard():
    """Render the fraud analysis interface and results dashboard."""
    
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    
    # Upload Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <div class="upload-icon">📁</div>
                <h2 class="upload-title">Upload Your Transaction Data</h2>
                <p class="upload-subtitle">Drag and drop your CSV or Excel file to begin analysis</p>
            </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "", 
            type=['csv', 'xlsx'], 
            label_visibility="collapsed",
            key="file_uploader"
        )
    
    with col2:
        st.markdown("### 🎁 Don't have data?")
        st.markdown("Try our demo dataset with embedded fraud patterns.")
        if st.download_button(
            "⬇️ Download Sample Data", 
            generate_sample_csv(), 
            "fraudguard_demo_data.csv", 
            "text/csv",
            use_container_width=True
        ):
            pass
        
        # Current plan indicator
        st.markdown("---")
        current_tier = st.session_state.subscription_tier
        row_limit = get_row_limit()
        
        if current_tier == 'Free':
            st.info(f"📊 **Current Plan:** Free (max {row_limit} rows)")
        elif current_tier == 'Standard':
            st.success(f"📊 **Current Plan:** Standard (max {row_limit} rows)")
        else:
            st.success(f"✨ **Current Plan:** Enterprise (Unlimited)")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process uploaded file
    if uploaded_file:
        try:
            # Load data
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            if df.empty:
                st.error("❌ The uploaded file is empty.")
                return
            
            # Auto-detect columns
            date_col = next((c for c in df.columns if any(x in c.lower() for x in ['date', 'time', 'day'])), None)
            amount_col = next((c for c in df.columns if any(x in c.lower() for x in ['amount', 'value', 'cost', 'price', 'total'])), None)
            vendor_col = next((c for c in df.columns if any(x in c.lower() for x in ['vendor', 'desc', 'merchant', 'payee', 'supplier'])), None)
            
            if not (date_col and amount_col):
                st.error("❌ Could not auto-detect required columns. Please ensure your file has 'Date' and 'Amount' columns.")
                st.info("📋 **Expected columns:** Date, Amount, Vendor (optional)")
                return
            
            # Apply row limits
            row_limit = get_row_limit()
            total_rows = len(df)
            is_limited = total_rows > row_limit
            
            if is_limited:
                df_display = df.head(row_limit)
                st.warning(f"⚠️ **Plan Limit:** Analyzing first {row_limit:,} of {total_rows:,} transactions. [Upgrade](#pricing) for full access.")
            else:
                df_display = df
            
            # Run analysis
            df_results, alerts, benford_res = run_analysis(df_display, date_col, amount_col, vendor_col)
            
            # Store results
            st.session_state.df_results = df_results
            st.session_state.alerts = alerts
            st.session_state.benford_res = benford_res
            st.session_state.analysis_complete = True
            
            # Success animation
            st.balloons()
            st.success("✅ Analysis complete! Review your forensic insights below.")
            
            # Render Dashboard
            render_results_dashboard(df_results, alerts, benford_res, date_col, amount_col, vendor_col)
            
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("💡 **Tip:** Ensure your file is a valid CSV or Excel format with proper headers.")

def render_results_dashboard(df, alerts, benford_res, date_col, amount_col, vendor_col):
    """Render the analysis results dashboard with metrics and visualizations."""
    
    st.markdown("---")
    st.markdown("## 📊 Forensic Analysis Dashboard")
    
    # Calculate metrics
    total_volume = df[amount_col].sum()
    high_risk = df[df['risk_score'] > 0.7]
    risk_volume = high_risk[amount_col].sum() if len(high_risk) > 0 else 0
    avg_risk = df['risk_score'].mean()
    
    # Metrics Grid
    st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Volume</div>
                <div class="metric-value">${total_volume:,.0f}</div>
                <div class="metric-subtext">Analyzed spend</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Transactions</div>
                <div class="metric-value">{len(df):,}</div>
                <div class="metric-subtext">Total processed</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        severity_class = "danger" if len(alerts) > 5 else "warning" if len(alerts) > 0 else "success"
        st.markdown(f"""
            <div class="metric-card {severity_class}">
                <div class="metric-label">Rule Violations</div>
                <div class="metric-value">{len(alerts)}</div>
                <div class="metric-subtext">Flags triggered</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        severity_class = "danger" if risk_volume > total_volume * 0.1 else "warning" if risk_volume > 0 else "success"
        st.markdown(f"""
            <div class="metric-card {severity_class}">
                <div class="metric-label">Risk Exposure</div>
                <div class="metric-value">${risk_volume:,.0f}</div>
                <div class="metric-subtext">{len(high_risk)} high-risk transactions</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Tabs for detailed analysis
    tab1, tab2, tab3 = st.tabs(["🔍 Risk Analysis", "📉 Benford's Law", "📋 Transaction Details"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Transaction Risk Timeline")
            fig_timeline = px.scatter(
                df,
                x=date_col,
                y=amount_col,
                color='risk_score',
                size='amount_log',
                color_continuous_scale='RdYlBu_r',
                hover_data=[vendor_col, 'risk_explainer'] if vendor_col else ['risk_explainer'],
                title="Risk Distribution Over Time",
                template="plotly_white"
            )
            fig_timeline.update_layout(height=450)
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        with col2:
            st.subheader("Risk Distribution")
            fig_risk = px.histogram(
                df,
                x='risk_score',
                nbins=20,
                color_discrete_sequence=['#0066FF'],
                template="plotly_white"
            )
            fig_risk.update_layout(height=450, showlegend=False)
            st.plotly_chart(fig_risk, use_container_width=True)
        
        # Vendor Risk Analysis
        if vendor_col:
            st.subheader("Vendor Risk Leaderboard")
            vendor_risk = df.groupby(vendor_col).agg({
                'risk_score': 'mean',
                amount_col: ['sum', 'count']
            }).reset_index()
            vendor_risk.columns = [vendor_col, 'avg_risk', 'total_amount', 'transaction_count']
            vendor_risk = vendor_risk.sort_values('avg_risk', ascending=False).head(10)
            
            fig_vendor = px.bar(
                vendor_risk,
                x='avg_risk',
                y=vendor_col,
                orientation='h',
                color='avg_risk',
                color_continuous_scale='Reds',
                hover_data=['total_amount', 'transaction_count'],
                template="plotly_white"
            )
            fig_vendor.update_layout(height=350, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_vendor, use_container_width=True)
    
    with tab2:
        st.subheader("Benford's Law Analysis")
        st.markdown("""
            **Benford's Law** states that in naturally occurring datasets, the leading digit 
            follows a predictable distribution. Significant deviations may indicate data manipulation.
        """)
        
        if benford_res and 'distribution' in benford_res:
            bf_df = benford_res['distribution']
            
            fig_benford = go.Figure()
            
            # Expected distribution line
            fig_benford.add_trace(go.Scatter(
                x=bf_df['digit'],
                y=bf_df['expected'],
                mode='lines+markers',
                name='Expected (Benford)',
                line=dict(color='#0066FF', width=3, dash='dash'),
                marker=dict(size=8)
            ))
            
            # Actual distribution bars
            fig_benford.add_trace(go.Bar(
                x=bf_df['digit'],
                y=bf_df['actual'],
                name='Your Data',
                marker_color='#0A0F2B',
                opacity=0.8
            ))
            
            fig_benford.update_layout(
                template="plotly_white",
                title="First Digit Distribution Comparison",
                xaxis_title="First Digit (1-9)",
                yaxis_title="Frequency (%)",
                height=450,
                xaxis=dict(tickmode='linear', tick0=1, dtick=1),
                legend=dict(orientation='h', yanchor='bottom', y=1.02)
            )
            
            st.plotly_chart(fig_benford, use_container_width=True)
            
            # Interpretation
            max_delta = bf_df['delta'].abs().max()
            if max_delta > 0.05:
                st.error(f"🚨 **Critical Deviation:** Max deviation of {max_delta:.1%} suggests potential data manipulation.")
            elif max_delta > 0.02:
                st.warning(f"⚠️ **Mild Deviation:** Max deviation of {max_delta:.1%}. Review flagged transactions.")
            else:
                st.success(f"✅ **Conforms to Benford's Law:** Max deviation of {max_delta:.1%} indicates natural distribution.")
        else:
            st.warning("Insufficient data for Benford's Law analysis (minimum 50 transactions required).")
    
    with tab3:
        # Alerts Section
        if alerts:
            st.subheader("🚨 Active Alerts")
            for alert in alerts[:10]:  # Show first 10 alerts
                severity_emoji = "🔴" if alert['severity'] == 'High' else "🟡"
                st.markdown(f"""
                    <div class="alert alert-danger">
                        <strong>{severity_emoji} {alert['type']}</strong><br>
                        {alert['note']}
                    </div>
                """, unsafe_allow_html=True)
            
            if len(alerts) > 10:
                st.info(f"📋 ... and {len(alerts) - 10} more alerts")
        
        # Transaction Table
        st.subheader("📄 Full Transaction Ledger")
        
        # Sort by risk score descending
        df_sorted = df.sort_values('risk_score', ascending=False)
        
        st.dataframe(
            df_sorted,
            column_config={
                "risk_score": st.column_config.ProgressColumn(
                    "Risk Score",
                    min_value=0,
                    max_value=1,
                    format="%.2f",
                    help="Higher values indicate greater fraud risk"
                ),
                amount_col: st.column_config.NumberColumn(
                    "Amount",
                    format="$%.2f"
                ),
                "risk_explainer": st.column_config.TextColumn(
                    "Risk Explanation",
                    help="Why this transaction was flagged"
                )
            },
            use_container_width=True,
            height=500,
            hide_index=True
        )

# ============================================================
# SIDEBAR
# ============================================================
def render_sidebar():
    """Render the admin and subscription sidebar."""
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">🛡️</div>
                <h3 style="margin: 0;">FraudGuard AI</h3>
                <p style="color: var(--text-muted); font-size: 0.875rem;">Forensic Audit Platform</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Current Plan
        current_tier = st.session_state.subscription_tier
        st.markdown(f"### 💎 Current Plan: **{current_tier}**")
        
        if current_tier == 'Free':
            st.info("📊 **Limit:** 60 transactions/month")
            st.markdown("---")
            st.markdown("### 🚀 Upgrade Now")
            
            if st.button("⭐ Standard - $5/mo", use_container_width=True):
                upgrade_tier('Standard')
            if st.button("🏢 Enterprise - $10/mo", use_container_width=True):
                upgrade_tier('Enterprise')
                
        elif current_tier == 'Standard':
            st.success("📊 **Limit:** 500 transactions/month")
            st.markdown("---")
            if st.button("🏢 Upgrade to Enterprise", use_container_width=True):
                upgrade_tier('Enterprise')
            if st.button("⬇️ Downgrade to Free", use_container_width=True):
                upgrade_tier('Free')
                
        else:  # Enterprise
            st.success("✨ **Unlimited Access**")
            st.markdown("---")
            if st.button("⬇️ Downgrade", use_container_width=True):
                upgrade_tier('Free')
        
        st.markdown("---")
        
        # Admin Panel
        with st.expander("🔐 Admin Panel"):
            password = st.text_input("Access Key", type="password")
            if password == "AliAudit2025":
                st.success("✅ Authenticated")
                st.info("Benford's Law Module: **Active**")
                st.info("ML Detectors: **Active**")
                st.info("Graph Analysis: **Active**")

# ============================================================
# MAIN APPLICATION
# ============================================================
def main():
    """Main application entry point."""
    
    # Render Navigation
    render_navbar()
    
    # Render Landing Page Sections
    render_hero()
    render_features()
    render_how_it_works()
    render_trust_section()
    render_pricing()
    render_cta_section()
    
    # Render Analysis Interface
    render_analysis_dashboard()
    
    # Render Footer
    render_footer()
    
    # Render Sidebar
    render_sidebar()

if __name__ == "__main__":
    main()