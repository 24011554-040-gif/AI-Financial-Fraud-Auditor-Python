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
    df = parse_datetime(df, time_col)

    # Clean amount common formats
    if amount_col in df.columns:
        df[amount_col] = df[amount_col].astype(str).str.replace(r'[$,]', '', regex=True)
        df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce')

    # Basic time features
    if time_col in df.columns:
        df['hour'] = df[time_col].dt.hour
        df['weekday'] = df[time_col].dt.weekday
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)

    # Amount transformations
    df['amount_log'] = np.log1p(df[amount_col].clip(lower=0))
    df['amount_med'] = df.groupby('Vendor')[amount_col].transform('median') if 'Vendor' in df.columns else df[amount_col].median()
    # vendor MAD
    if 'Vendor' in df.columns:
        vendor_mad = df.groupby('Vendor')[amount_col].transform(lambda x: (x - x.median()).abs().median())
        vendor_mad = vendor_mad.replace(0, 1.0)
        df['vendor_mad_z'] = 0.6745 * (df[amount_col] - df['amount_med']) / vendor_mad
    else:
        df['vendor_mad_z'] = robust_zscore(df[amount_col])

    # Global robust zscore
    df['global_mad_z'] = robust_zscore(df[amount_col])

    # Frequency encoding for Vendor (safe, no label leakage)
    if 'Vendor' in df.columns:
        freq = df['Vendor'].value_counts(normalize=True)
        df['vendor_freq'] = df['Vendor'].map(freq).fillna(0)

    # EWMA of amount (global)
    df['amount_ewma_0.2'] = df[amount_col].ewm(alpha=0.2, adjust=False).mean()

    # Simple per-id velocity (if id provided)
    if id_cols:
        for idc in id_cols:
            if idc in df.columns:
                grp = df.sort_values(time_col).groupby(idc)
                # approximate counts and sums in last 24h using expanding and a window flag (cheap)
                df[f'{idc}_count'] = grp[amount_col].transform('count')
                df[f'{idc}_sum'] = grp[amount_col].transform('sum')

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
    scaler = RobustScaler()
    Xs = scaler.fit_transform(X)
    lof = LocalOutlierFactor(n_neighbors=n_neighbors, novelty=False, contamination='auto')
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
# Rule Engine
# ---------------------------
def rules_engine(df: pd.DataFrame,
                 amount_col: str = 'Amount',
                 high_amount_thresh: float = 5000.0,
                 round_threshold: float = 500.0) -> List[Dict]:
    """
    Existing simple rules and additional ones:
    - duplicate tx by Vendor+Amount (exact)
    - round numbers above round_threshold
    - high value above high_amount_thresh
    - impossible travel if lat/lon + previous tx exists (not implemented unless lat/lon present)
    Returns list of alert dicts.
    """
    alerts = []
    # Duplicates
    if {'Vendor', amount_col}.issubset(df.columns):
        dup = df[df.duplicated(subset=['Vendor', amount_col], keep=False)]
        for idx, row in dup.iterrows():
            alerts.append({'tx_id': row.get('tx_id'), 'type': 'duplicate', 'severity': 'high',
                           'note': f"Duplicate {amount_col} to {row.get('Vendor')} - ${row.get(amount_col)}"})

    # Round numbers
    if amount_col in df.columns:
        round_mask = (df[amount_col] % 1 == 0) & (df[amount_col] >= round_threshold)
        for idx, row in df[round_mask].iterrows():
            alerts.append({'tx_id': row.get('tx_id'), 'type': 'round_amount', 'severity': 'medium',
                           'note': f"Round amount ${row.get(amount_col)}"})

        # High value
        high_mask = df[amount_col] >= high_amount_thresh
        for idx, row in df[high_mask].iterrows():
            alerts.append({'tx_id': row.get('tx_id'), 'type': 'high_value', 'severity': 'high',
                           'note': f"High value ${row.get(amount_col)} >= threshold {high_amount_thresh}"})

    # Impossible travel (requires lat/lon & timestamp & per-entity grouping)
    if {'lat', 'lon', 'Date', 'Card'}.issubset(df.columns):
        df_sorted = df.sort_values('Date')
        grp = df_sorted.groupby('Card')
        for card, g in grp:
            g = g.reset_index(drop=True)
            for i in range(1, len(g)):
                t0 = g.loc[i-1, 'Date']
                t1 = g.loc[i, 'Date']
                if pd.isna(t0) or pd.isna(t1): 
                    continue
                hours = (t1 - t0).total_seconds() / 3600
                if hours <= 0: 
                    continue
                # haversine
                lat1, lon1 = g.loc[i-1, 'lat'], g.loc[i-1, 'lon']
                lat2, lon2 = g.loc[i, 'lat'], g.loc[i, 'lon']
                if pd.isna(lat1) or pd.isna(lat2): 
                    continue
                # simple distance in km
                R = 6371.0
                phi1, phi2 = np.radians([lat1, lat2])
                dphi = np.radians(lat2 - lat1)
                dlambda = np.radians(lon2 - lon1)
                a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
                dist = 2 * R * np.arcsin(np.sqrt(a))
                speed = dist / (hours + 1e-9)
                if speed > 1000:  # impossible travel threshold km/h
                    alerts.append({'tx_id': g.loc[i, 'tx_id'], 'type': 'impossible_travel', 'severity': 'high',
                                   'note': f"Impossible travel: {dist:.1f}km in {hours:.2f}h (~{speed:.1f} km/h)"})
    return alerts

# ---------------------------
# Ensemble + Explain
# ---------------------------
def ensemble_scores(df: pd.DataFrame, score_cols: List[str], weights: Optional[List[float]] = None, out_col: str = 'risk_score') -> pd.DataFrame:
    """
    Normalizes the provided detector score columns and produces a weighted ensemble.
    Also creates a simple explanation string with top contributing score(s).
    """
    df = df.copy()
    scaler = MinMaxScaler()
    S = df[score_cols].fillna(0).values
    if S.ndim == 1:
        S = S.reshape(-1, 1)
    S_norm = scaler.fit_transform(S)
    if weights is None:
        weights = [1.0] * S_norm.shape[1]
    weights = np.array(weights) / max(1e-9, sum(weights))
    ensemble = S_norm.dot(weights)
    df[out_col] = ensemble
    # Explanation: top scoring method per transaction
    best_idx = np.argmax(S_norm * weights, axis=1)
    df['risk_explainer'] = [f"{score_cols[i]}={float(S_norm[j, i]):.3f}" for j, i in enumerate(best_idx)]
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
    if len(feature_cols) == 0:
        raise ValueError("No feature columns available for detectors. Run prepare_features first or pass feature_cols.")
    df['iforest_score'] = isolation_forest_detector(df, feature_cols, contamination=contamination)
    try:
        df['lof_score'] = lof_detector(df, feature_cols)
    except Exception:
        df['lof_score'] = 0.0
    ae_score = autoencoder_detector(df, feature_cols) if _HAS_KERAS else None
    if ae_score is not None:
        df['ae_score'] = ae_score
    return df

# ---------------------------
# Quick CLI demo when run directly
# ---------------------------
if __name__ == "__main__":
    # Minimal demo (synthetic)
    df_demo = pd.DataFrame({
        'Date': pd.date_range('2025-01-01', periods=200, freq='H'),
        'Vendor': np.random.choice(['Amazon','Walmart','Uber','Shell','VendorX'], size=200),
        'Amount': np.concatenate([np.random.randint(10,2000, 195), [5000, 5000, 10000, 3000, 2500]])
    })
    df_demo = prepare_features(df_demo, time_col='Date', amount_col='Amount')
    df_demo = run_detectors(df_demo)
    df_demo = ensemble_scores(df_demo, score_cols=[c for c in df_demo.columns if c.endswith('_score')])
    alerts = rules_engine(df_demo)
    print("Top risk txs:\n", df_demo.sort_values('risk_score', ascending=False).head(10)[['tx_id','Amount','risk_score','risk_explainer']])
    print("Rule alerts sample:", alerts[:5])