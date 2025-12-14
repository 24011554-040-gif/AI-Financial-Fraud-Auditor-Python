import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import time
from datetime import datetime, timedelta
import io
import base64
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json

# --- IMPORT CUSTOM ENGINE ---
try:
    import fraud_forensics as ff
    FRAUD_ENGINE_AVAILABLE = True
except ImportError:
    FRAUD_ENGINE_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════════════════════
# 📦 CONFIGURATION & CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

class RiskLevel(Enum):
    CRITICAL = ("Critical", "#FF3B3B", "🔴")
    HIGH = ("High", "#FF6B6B", "🟠")
    MEDIUM = ("Medium", "#FFB946", "🟡")
    LOW = ("Low", "#00D4AA", "🟢")
    SAFE = ("Safe", "#4CAF50", "✅")

@dataclass
class AppConfig:
    APP_NAME: str = "FraudGuard AI"
    APP_VERSION: str = "2.0.0"
    APP_TAGLINE: str = "Enterprise Forensic Intelligence Platform"
    DEFAULT_CONTAMINATION: float = 0.05
    HIGH_RISK_THRESHOLD: float = 0.7
    MEDIUM_RISK_THRESHOLD: float = 0.4
    MAX_DISPLAY_ROWS: int = 1000
    ANIMATION_SPEED: float = 0.03

CONFIG = AppConfig()

# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 PREMIUM THEME ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def get_theme_css(dark_mode: bool = False) -> str:
    """Generate dynamic CSS based on theme selection"""
    
    if dark_mode:
        colors = {
            "bg_primary": "#0A0E1A",
            "bg_secondary": "#111827",
            "bg_card": "rgba(17, 24, 39, 0.8)",
            "text_primary": "#F8FAFC",
            "text_secondary": "#94A3B8",
            "text_muted": "#64748B",
            "border_color": "rgba(255, 255, 255, 0.1)",
            "accent_primary": "#3B82F6",
            "accent_secondary": "#8B5CF6",
            "accent_success": "#10B981",
            "accent_danger": "#EF4444",
            "accent_warning": "#F59E0B",
            "glass_bg": "rgba(15, 23, 42, 0.75)",
            "glass_border": "rgba(255, 255, 255, 0.08)",
            "gradient_start": "#0A0E1A",
            "gradient_mid": "#111827",
            "gradient_end": "#1E1B4B",
            "shadow_color": "rgba(0, 0, 0, 0.5)",
            "glow_color": "rgba(59, 130, 246, 0.5)",
        }
    else:
        colors = {
            "bg_primary": "#FAFBFF",
            "bg_secondary": "#FFFFFF",
            "bg_card": "rgba(255, 255, 255, 0.7)",
            "text_primary": "#0F172A",
            "text_secondary": "#475569",
            "text_muted": "#94A3B8",
            "border_color": "rgba(0, 0, 0, 0.06)",
            "accent_primary": "#0066FF",
            "accent_secondary": "#8B5CF6",
            "accent_success": "#00D4AA",
            "accent_danger": "#FF6B6B",
            "accent_warning": "#FFB946",
            "glass_bg": "rgba(255, 255, 255, 0.65)",
            "glass_border": "rgba(255, 255, 255, 0.9)",
            "gradient_start": "#F0F4FF",
            "gradient_mid": "#FFFFFF",
            "gradient_end": "#F0FFF9",
            "shadow_color": "rgba(31, 38, 135, 0.07)",
            "glow_color": "rgba(0, 102, 255, 0.4)",
        }
    
    return f"""
<style>
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* 🔤 TYPOGRAPHY IMPORTS                                                    */
    /* ═══════════════════════════════════════════════════════════════════════ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* 🎨 CSS VARIABLES                                                         */
    /* ═══════════════════════════════════════════════════════════════════════ */
    :root {{
        --bg-primary: {colors['bg_primary']};
        --bg-secondary: {colors['bg_secondary']};
        --bg-card: {colors['bg_card']};
        --text-primary: {colors['text_primary']};
        --text-secondary: {colors['text_secondary']};
        --text-muted: {colors['text_muted']};
        --border-color: {colors['border_color']};
        --accent-primary: {colors['accent_primary']};
        --accent-secondary: {colors['accent_secondary']};
        --accent-success: {colors['accent_success']};
        --accent-danger: {colors['accent_danger']};
        --accent-warning: {colors['accent_warning']};
        --glass-bg: {colors['glass_bg']};
        --glass-border: {colors['glass_border']};
        --gradient-start: {colors['gradient_start']};
        --gradient-mid: {colors['gradient_mid']};
        --gradient-end: {colors['gradient_end']};
        --shadow-color: {colors['shadow_color']};
        --glow-color: {colors['glow_color']};
        --card-radius: 20px;
        --button-radius: 12px;
        --transition-speed: 0.3s;
    }}

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* 🌐 GLOBAL STYLES                                                         */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .stApp {{
        background: 
            radial-gradient(ellipse at 0% 0%, var(--gradient-start) 0%, transparent 50%),
            radial-gradient(ellipse at 100% 0%, var(--gradient-end) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 100%, var(--gradient-mid) 0%, transparent 50%),
            var(--bg-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary);
    }}

    /* Hide Streamlit Defaults */
    #MainMenu, footer, header, .stDeployButton {{
        visibility: hidden !important;
        display: none !important;
    }}

    .block-container {{
        padding: 2rem 3rem 4rem 3rem !important;
        max-width: 1400px !important;
    }}

    /* Typography */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--text-primary);
    }}

    p, span, div {{
        color: var(--text-secondary);
    }}

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* 🏠 NAVIGATION BAR                                                        */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .navbar {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid var(--border-color);
        padding: 0.75rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}

    .navbar-brand {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}

    .navbar-logo {{
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        box-shadow: 0 4px 15px var(--glow-color);
    }}

    .navbar-title {{
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 1.25rem;
        background: linear-gradient(135deg, var(--text-primary), var(--accent-primary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .navbar-badge {{
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        color: white;
        font-size: 0.65rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* 🦸 HERO SECTION                                                          */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .hero-section {{
        text-align: center;
        padding: 5rem 2rem 3rem 2rem;
        position: relative;
        overflow: hidden;
    }}

    .hero-section::before {{
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 600px;
        height: 600px;
        background: radial-gradient(circle, var(--glow-color) 0%, transparent 70%);
        opacity: 0.3;
        pointer-events: none;
        animation: pulse-glow 4s ease-in-out infinite;
    }}

    @keyframes pulse-glow {{
        0%, 100% {{ transform: translate(-50%, -50%) scale(1); opacity: 0.3; }}
        50% {{ transform: translate(-50%, -50%) scale(1.1); opacity: 0.5; }}
    }}

    .hero-icon {{
        font-size: 4rem;
        margin-bottom: 1rem;
        animation: float 3s ease-in-out infinite;
    }}

    @keyframes float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-10px); }}
    }}

    .hero-title {{
        font-size: clamp(2.5rem, 6vw, 4.5rem);
        font-weight: 900;
        line-height: 1.1;
        margin-bottom: 0.75rem;
        background: linear-gradient(135deg, var(--text-primary) 0%, var(--accent-primary) 50%, var(--accent-secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-shift 8s ease infinite;
        background-size: 200% 200%;
    }}

    @keyframes gradient-shift {{
        0%, 100% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
    }}

    .hero-subtitle {{
        font-size: 1.25rem;
        color: var(--text-secondary);
        max-width: 650px;
        margin: 0 auto 2rem auto;
        font-weight: 400;
        line-height: 1.6;
    }}

    .hero-features {{
        display: flex;
        justify-content: center;
        gap: 2rem;
        flex-wrap: wrap;
        margin-top: 2rem;
    }}

    .hero-feature {{
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.9rem;
        color: var(--text-muted);
        font-weight: 500;
    }}

    .hero-feature-icon {{
        width: 24px;
        height: 24px;
        background: var(--accent-success);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
    }}

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* 🪟 GLASS CARDS                                                           */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .glass-card {{
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: var(--card-radius);
        box-shadow: 
            0 8px 32px var(--shadow-color),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        transition: all var(--transition-speed) cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}

    .glass-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    }}

    .glass-card:hover {{
        transform: translateY(-4px);
        box-shadow: 
            0 16px 48px var(--shadow-color),
            0 0 0 1px var(--accent-primary),
            inset 0 1px 0 rgba(255, 255, 255, 0.15);
    }}

    .glass-card-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border-color);
    }}

    .glass-card-title {{
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 1rem;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* 📊 METRIC CARDS                                                          */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .metric-card {{
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: var(--card-radius);
        padding: 1.75rem;
        text-align: center;
        transition: all var(--transition-speed) cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}

    .metric-card::after {{
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--metric-accent, var(--accent-primary));
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }}

    .metric-card:hover::after {{
        transform: scaleX(1);
    }}

    .metric-card:hover {{
        transform: translateY(-6px);
        box-shadow: 0 20px 40px var(--shadow-color);
    }}

    .metric-icon {{
        font-size: 2rem;
        margin-bottom: 0.75rem;
        display: block;
    }}

    .metric-value {{
        font-family: 'Poppins', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        line-height: 1.2;
        color: var(--metric-color, var(--text-primary));
        margin-bottom: 0.25rem;
    }}

    .metric-label {{
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-muted);
        font-weight: 600;
    }}

    .metric-trend {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.5rem;
        padding: 4px 10px;
        border-radius: 20px;
    }}

    .metric-trend.up {{
        background: rgba(16, 185, 129, 0.15);
        color: var(--accent-success);
    }}

    .metric-trend.down {{
        background: rgba(239, 68, 68, 0.15);
        color: var(--accent-danger);
    }}

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* 📁 FILE UPLOADER                                                         */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .upload-zone {{
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 2px dashed var(--border-color);
        border-radius: var(--card-radius);
        padding: 3rem 2rem;
        text-align: center;
        transition: all var(--transition-speed) ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }}

    .upload-zone:hover {{
        border-color: var(--accent-primary);
        background: rgba(59, 130, 246, 0.05);
        transform: scale(1.01);
    }}

    .upload-zone-active {{
        border-color: var(--accent-primary);
        background: rgba(59, 130, 246, 0.1);
        box-shadow: 0 0 30px var(--glow-color);
    }}

    .upload-icon {{
        font-size: 3.5rem;
        margin-bottom: 1rem;
        animation: bounce 2s ease infinite;
    }}

    @keyframes bounce {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-8px); }}
    }}

    .upload-title {{
        font-family: 'Poppins', sans-serif;
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }}

    .upload-subtitle {{
        font-size: 0.9rem;
        color: var(--text-muted);
    }}

    .upload-formats {{
        display: flex;
        justify-content: center;
        gap: 0.75rem;
        margin-top: 1rem;
    }}

    .format-badge {{
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-muted);
        font-family: 'JetBrains Mono', monospace;
    }}

    /* Streamlit File Uploader Override */
    .stFileUploader {{
        background: transparent !important;
    }}

    .stFileUploader > div {{
        background: transparent !important;
        border: none !important;
    }}

    .stFileUploader label {{
        display: none !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* 🔘 BUTTONS                                                               */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .stButton > button {{
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        color: white;
        border: none;
        padding: 0.85rem 2rem;
        border-radius: var(--button-radius);
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.02em;
        box-shadow: 0 4px 15px var(--glow-color);
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        position: relative;
        overflow: hidden;
    }}

    .stButton > button::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }}

    .stButton > button:hover::before {{
        left: 100%;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 25px var(--glow-color);
    }}

    .stButton > button:active {{
        transform: translateY(0) scale(0.98);
    }}

    /* Secondary Button */
    .stDownloadButton 