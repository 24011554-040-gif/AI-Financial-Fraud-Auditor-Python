"""
Advanced local forensic module for transaction CSVs.
Drop-in helpers: feature engineering, robust stats, IsolationForest/LOF detectors,
simple autoencoder (optional), graph-based collusion detection, rule engine,
and an ensemble scorer that returns explainable alerts.

Usage:
    from fraud_forensics import prepare_features, run_detectors, ensemble_scores, rules_engine
    df = pd.read_csv("transactions.csv")
    df = prepare_features(df, time_col='Date', amount_col='Amount')
    results = run_detectors(df)
    df = ensemble_scores(df, score_cols=['iforest_score','lof_score'])
    alerts = rules_engine(df)
"""

from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import RobustScaler, MinMaxScaler
import networkx as nx

# Optional deep model
try:
    from tensorflow.keras import layers, models
    _HAS_KERAS = True
except Exception:
    _HAS_KERAS = False

# ---------------------------
# Utility / Feature Helpers
# ---------------------------
def robust_median_mad(series: pd.Series):
    med = series.median()
    mad = (series - med).abs().median()
    return med, mad if mad > 0 else 1.0

def robust_zscore(series: pd.Series):
    med, mad = robust_median_mad(series)
    # 0.6745 scaling makes MAD comparable to std under normality
    return 0.6745 * (series - med) / mad

def parse_datetime(df: pd.DataFrame, time_col: str = 'Date'):
    if time_col in df.columns:
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    return df

def prepare_features(df: pd.DataFrame,
                     time_col: str = 'Date',
                     amount_col: str = 'Amount',
                     id_cols: Optional[List[str]] = None) -> pd.DataFrame:
    """
    - Normalizes amount and creates robust zscore, log-amount.
    - Adds time features (hour, weekday).
    - Vendor frequency and vendor-median/MAD normalized amount.
    - EWMA global amount.
    - If id_cols (e.g., ['Card','Account']) provided, creates simple velocity features:
        count_last_1d, sum_last_1d (approx using groupby + transform)
    """
    df = df.copy()
    
    # 1. Parse Date
    if time_col and time_col in df.columns:
        df = parse_datetime(df, time_col)
    
    # 2. Clean amount common formats
    if amount_col and amount_col in df.columns:
        # Check if already numeric, otherwise clean
        if not pd.api.types.is_numeric_dtype(df[amount_col]):
            df[amount_col] = df[amount_col].astype(str).str.replace(r'[$,]', '', regex=True)
            df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce')

    # 3. Basic time features
    if time_col and time_col in df.columns:
        # We need a valid datetime to extract hour/weekday
        # Only process rows where date conversion succeeded
        valid_dates = pd.notna(df[time_col])
        df.loc[valid_dates, 'hour'] = df.loc[valid_dates, time_col].dt.hour
        df.loc[valid_dates, 'weekday'] = df.loc[valid_dates, time_col].dt.weekday
        
        # Fill NaNs if any (optional, or just leave as NaN)
        df['hour'] = df['hour'].fillna(0)
        df['weekday'] = df['weekday'].fillna(0)
        
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    else:
        # If no time col, we must synthesize or skip time features to avoid crashes
        df['hour'] = 12
        df['weekday'] = 0
        df['hour_sin'] = 0.0
        df['hour_cos'] = 0.0

    # 4. Amount transformations
    if amount_col and amount_col in df.columns:
        df['amount_log'] = np.log1p(df[amount_col].fillna(0).clip(lower=0))
        
        # Check for Vendor column existence (dynamic)
        vendor_col = None
        if id_cols and len(id_cols) > 0:
             # Assume first ID col is "Vendor-like" for grouping
             vendor_col = id_cols[0]
        
        if vendor_col and vendor_col in df.columns:
            df['amount_med'] = df.groupby(vendor_col)[amount_col].transform('median')
            
            # vendor MAD
            vendor_mad = df.groupby(vendor_col)[amount_col].transform(lambda x: (x - x.median()).abs().median())
            vendor_mad = vendor_mad.replace(0, 1.0)
            df['vendor_mad_z'] = 0.6745 * (df[amount_col] - df['amount_med']) / vendor_mad
            
            # Vendor Freq
            freq = df[vendor_col].value_counts(normalize=True)
            df['vendor_freq'] = df[vendor_col].map(freq).fillna(0)

        else:
            # Fallback if no vendor/grouping
            df['amount_med'] = df[amount_col].median()
            df['vendor_mad_z'] = robust_zscore(df[amount_col])
            df['vendor_freq'] = 0.0
        
        # Global robust zscore
        df['global_mad_z'] = robust_zscore(df[amount_col])
        
        # EWMA of amount (global)
        df['amount_ewma_0.2'] = df[amount_col].ewm(alpha=0.2, adjust=False).mean()

    # 5. Simple per-id velocity (if id provided)
    if id_cols and time_col in df.columns:
        for idc in id_cols:
            if idc in df.columns:
                # Need sorting for rolling/groupby ops
                try:
                    grp = df.sort_values(time_col).groupby(idc)
                    df[f'{idc}_count'] = grp[amount_col].transform('count')
                    df[f'{idc}_sum'] = grp[amount_col].transform('sum')
                except:
                    pass

    # Keep a canonical transaction id for graph usage
    if 'tx_id' not in df.columns:
        df = df.reset_index().rename(columns={'index': 'tx_id'})

    return df

# ---------------------------
# Unsupervised Detectors
# ---------------------------
def _normalize_series(s: pd.Series) -> pd.Series:
    # Min-max stable
    s = s.copy()
    if s.max() == s.min():
        return pd.Series(0.0, index=s.index)
    return (s - s.min()) / (s.max() - s.min())

def isolation_forest_detector(df: pd.DataFrame, feature_cols: List[str],
                              contamination: float = 0.01, random_state: int = 42) -> pd.Series:
    """
    Returns normalized anomaly score in [0,1] where 1 is most anomalous.
    """
    X = df[feature_cols].fillna(0).values
    if len(X) == 0:
        return pd.Series(dtype=float)
        
    scaler = RobustScaler()
    Xs = scaler.fit_transform(X)
    clf = IsolationForest(n_estimators=200, contamination=contamination, random_state=random_state)
    clf.fit(Xs)
    raw = -clf.decision_function(Xs)  # higher = more anomalous
    return _normalize_series(pd.Series(raw, index=df.index))

def lof_detector(df: pd.DataFrame, feature_cols: List[str], n_neighbors: int = 20) -> pd.Series:
    """
    LOF returns negative_outlier_factor_: lower = more outlier.
    We invert and normalize to get high=anomaly.
    """
    X = df[feature_cols].fillna(0).values
    
    # Adjust neighbors for small datasets to avoid warnings/errors
    n_samples = len(df)
    if n_samples <= 1:
        return pd.Series(0.0, index=df.index)

    actual_neighbors = max(1, min(n_neighbors, n_samples - 1))
    
    scaler = RobustScaler()
    Xs = scaler.fit_transform(X)
    lof = LocalOutlierFactor(n_neighbors=actual_neighbors, novelty=False, contamination='auto')
    # fit_predict returns -1 for outliers; we use negative_outlier_factor_ (need refit style)
    lof.fit(Xs)
    raw = -lof.negative_outlier_factor_
    return _normalize_series(pd.Series(raw, index=df.index))

def autoencoder_detector(df: pd.DataFrame, feature_cols: List[str], epochs: int = 30, batch_size: int = 128) -> Optional[pd.Series]:
    """
    Simple dense autoencoder using Keras. Optional: requires tensorflow.
    Returns normalized reconstruction error if available.
    """
    if not _HAS_KERAS:
        return None
    X = df[feature_cols].fillna(0).values
    if len(X) == 0:
        return None

    scaler = RobustScaler()
    Xs = scaler.fit_transform(X)
    input_dim = Xs.shape[1]
    # small bottleneck
    model = models.Sequential([
        layers.Input(shape=(input_dim,)),
        layers.Dense(max(8, input_dim//2), activation='relu'),
        layers.Dense(max(4, input_dim//4), activation='relu'),
        layers.Dense(max(8, input_dim//2), activation='relu'),
        layers.Dense(input_dim, activation='linear')
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(Xs, Xs, epochs=epochs, batch_size=batch_size, verbose=0)
    rec = model.predict(Xs, verbose=0)
    mse = np.mean((Xs - rec) ** 2, axis=1)
    return _normalize_series(pd.Series(mse, index=df.index))

# ---------------------------
# Graph / Collusion Detector
# ---------------------------
def graph_collusion_detector(df: pd.DataFrame,
                             node_cols: List[str] = ['Vendor', 'Card', 'Device', 'IP'],
                             tx_id_col: str = 'tx_id',
                             min_component_size: int = 5) -> List[Dict]:
    """
    Build a bipartite-like graph: tx nodes connected to entity nodes (prefixed).
    Returns suspicious components metadata: components with many distinct cards or repeated device reuse.
    """
    G = nx.Graph()
    for _, row in df.iterrows():
        tx = f"tx_{row[tx_id_col]}"
        G.add_node(tx, bipartite=0)
        for c in node_cols:
            if c in df.columns and pd.notna(row.get(c)):
                node = f"{c.lower()}_{str(row[c])}"
                G.add_node(node, bipartite=1)
                G.add_edge(tx, node)
    suspicious = []
    for comp in nx.connected_components(G):
        sub = G.subgraph(comp)
        nodes = list(sub.nodes)
        tx_nodes = [n for n in nodes if n.startswith('tx_')]
        entity_nodes = [n for n in nodes if not n.startswith('tx_')]
        # crude heuristics:
        card_nodes = [n for n in entity_nodes if n.startswith('card_')]
        device_nodes = [n for n in entity_nodes if n.startswith('device_')]
        if len(tx_nodes) >= min_component_size and (len(card_nodes) > len(device_nodes) * 2 or len(device_nodes) == 1):
            suspicious.append({
                'component_size': len(tx_nodes),
                'tx_examples': tx_nodes[:5],
                'cards': len(card_nodes),
                'devices': len(device_nodes),
                'entities': entity_nodes[:10]
            })
    return suspicious

# ---------------------------
# Benford's Law
# ---------------------------
def benfords_law_analysis(df: pd.DataFrame, amount_col: str = 'Amount') -> Dict:
    """
    Calculates the distribution of the first digit of the amount column
    and compares it to the expected Benford's Law distribution.
    """
    if amount_col not in df.columns:
        return {}

    # Extract first digit (1-9)
    # Convert to string, strip leading zeros/minus, take first char
    s = df[amount_col].astype(str).str.lstrip('-0').str[0]
    # Keep only digits 1-9
    s = s[s.str.match(r'^[1-9]$')]
    
    if len(s) == 0:
        return {}
        
    counts = s.value_counts(normalize=True).sort_index()
    
    # Benford's expected frequencies
    benford = {str(d): np.log10(1 + 1/d) for d in range(1, 10)}
    
    results = []
    for d in range(1, 10):
        d_str = str(d)
        actual = counts.get(d_str, 0.0)
        expected = benford[d_str]
        results.append({
            'digit': d,
            'actual': actual,
            'expected': expected,
            'delta': actual - expected
        })
        
    return {'distribution': pd.DataFrame(results), 'sample_size': len(s)}

# ---------------------------
# Rule Engine
# ---------------------------
def rules_engine(df: pd.DataFrame,
                 amount_col: str = 'Amount',
                 vendor_col: Optional[str] = 'Vendor',
                 high_amount_thresh: float = 5000.0,
                 round_threshold: float = 500.0) -> List[Dict]:
    """
    Rules:
    - duplicate tx by Vendor+Amount (exact)
    - round numbers above round_threshold
    - high value above high_amount_thresh
    """
    alerts = []
    
    # 1. Duplicates
    # Only run if we have a Vendor column (or description) to pair with Amount
    if vendor_col and vendor_col in df.columns and amount_col in df.columns:
        dup_mask = df.duplicated(subset=[vendor_col, amount_col], keep=False)
        dup = df[dup_mask]
        for idx, row in dup.iterrows():
            # Only flag the second occurrence onwards or all? 
            # Usually flagging all involved helps usage.
            alerts.append({
                'tx_id': row.get('tx_id'),
                'type': 'Duplicate Transaction',
                'severity': 'High',
                'note': f"Potential Duplicate: {row.get(vendor_col)} - ${row.get(amount_col):,.2f}"
            })

    # 2. Round numbers & High Value
    if amount_col in df.columns:
        # Round numbers
        # Filter for non-nulls
        valid_amounts = df[df[amount_col].notna()]
        
        # Check if float is basically an integer
        round_mask = (valid_amounts[amount_col] % 1 == 0) & (valid_amounts[amount_col] >= round_threshold)
        for idx, row in valid_amounts[round_mask].iterrows():
            alerts.append({
                'tx_id': row.get('tx_id'),
                'type': 'Round Dollar Amount',
                'severity': 'Medium',
                'note': f"Unusual Round Amount: ${row.get(amount_col):,.2f}"
            })

        # High value
        high_mask = valid_amounts[amount_col] >= high_amount_thresh
        for idx, row in valid_amounts[high_mask].iterrows():
            alerts.append({
                'tx_id': row.get('tx_id'),
                'type': 'High Value Transaction',
                'severity': 'High',
                'note': f"High Value Alert: ${row.get(amount_col):,.2f} exceeds threshold"
            })

    return alerts

# ---------------------------
# Ensemble + Explain
# ---------------------------
def ensemble_scores(df: pd.DataFrame, score_cols: List[str], weights: Optional[List[float]] = None, out_col: str = 'risk_score') -> pd.DataFrame:
    """
    Normalizes the provided detector score columns and produces a weighted ensemble.
    Also creates a detailed explanation string with top contributing score(s).
    """
    df = df.copy()
    
    # Validate columns exist
    valid_cols = [c for c in score_cols if c in df.columns]
    if not valid_cols:
        df[out_col] = 0.0
        df['risk_explainer'] = "No scores"
        return df

    scaler = MinMaxScaler()
    S = df[valid_cols].fillna(0).values
    if S.ndim == 1:
        S = S.reshape(-1, 1)
    
    # If S is empty
    if S.shape[0] == 0:
        df[out_col] = 0.0
        df['risk_explainer'] = ""
        return df
        
    S_norm = scaler.fit_transform(S)
    if weights is None:
        weights = [1.0] * S_norm.shape[1]
    
    # Adjust weights to match valid_cols length
    weights = weights[:len(valid_cols)]
    weights = np.array(weights) / max(1e-9, sum(weights))
    
    ensemble = S_norm.dot(weights)
    df[out_col] = ensemble
    
    # Explanation: top scoring method per transaction
    best_idx = np.argmax(S_norm * weights, axis=1)
    
    # Generate human-readable explanations
    explanations = []
    for j, i in enumerate(best_idx):
        score_val = float(S_norm[j, i])
        method = valid_cols[i]
        
        # Threshold for considering it an "active" anomaly
        if score_val < 0.3:
            expl = "Low Risk"
        else:
            if method == 'iforest_score':
                expl = "Statistical Outlier (Isolation Forest)"
            elif method == 'lof_score':
                expl = "Local Density Anomaly (LOF)"
            elif method == 'ae_score':
                expl = "Pattern Mismatch (Autoencoder)"
            else:
                expl = f"Anomaly ({method})"
            
        explanations.append(expl)
        
    df['risk_explainer'] = explanations
    return df

# ---------------------------
# Runner convenience
# ---------------------------
def run_detectors(df: pd.DataFrame,
                  feature_cols: Optional[List[str]] = None,
                  contamination: float = 0.01) -> pd.DataFrame:
    """
    Executes a set of detectors and appends score columns:
      - iforest_score
      - lof_score
      - ae_score (if Keras available)
    Returns df with scores.
    """
    df = df.copy()
    # If no feature_cols provided, pick useful numeric columns
    if feature_cols is None:
        possible = ['Amount', 'amount_log', 'vendor_mad_z', 'global_mad_z', 'vendor_freq', 'amount_ewma_0.2', 'hour_sin', 'hour_cos']
        feature_cols = [c for c in possible if c in df.columns]
    
    # If still no features, cannot run
    if len(feature_cols) == 0:
        # Just return 0 scores
        df['iforest_score'] = 0.0
        df['lof_score'] = 0.0
        return df

    df['iforest_score'] = isolation_forest_detector(df, feature_cols, contamination=contamination)
    try:
        df['lof_score'] = lof_detector(df, feature_cols)
    except Exception:
        df['lof_score'] = 0.0
        
    ae_score = autoencoder_detector(df, feature_cols) if _HAS_KERAS else None
    if ae_score is not None:
        df['ae_score'] = ae_score
        
    return df