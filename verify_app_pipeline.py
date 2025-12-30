import pandas as pd
import numpy as np
import fraud_forensics as ff
import sys

def verify_pipeline():
    print("🚀 Starting Pipeline Verification...")
    
    # 1. Create Mock Data (Same as app logic)
    print("1. Generating Mock Data...")
    data = {
        'Date': pd.date_range(start='2025-01-01', periods=10, freq='H'),
        'Vendor': ['VendorA']*10,
        'Amount': [100.0, 200.0, 300.0, 400.0, 500.0, 600.0, 700.0, 800.0, 900.0, 5000.0],
        'Description': ['Test']*10
    }
    df = pd.DataFrame(data)
    
    # 2. Pipeline Steps
    try:
        print("2. Running Feature Engineering...")
        df_features = ff.prepare_features(df, time_col='Date', amount_col='Amount', id_cols=['Vendor'])
        
        print("3. Running Detectors...")
        df_scored = ff.run_detectors(df_features, contamination=0.05)
        
        print("4. Running Ensemble...")
        df_final = ff.ensemble_scores(df_scored, score_cols=['iforest_score', 'lof_score'])
        
        print("5. Running Rules Engine...")
        alerts = ff.rules_engine(df_final, amount_col='Amount', vendor_col='Vendor')
        print(f"   -> Found {len(alerts)} alerts")
        
        print("6. Running Benford's Law...")
        benford = ff.benfords_law_analysis(df, amount_col='Amount')
        print(f"   -> Sample size: {benford.get('sample_size')}")
        
        print("✅ Pipeline Verification SUCCESS")
        
    except Exception as e:
        print(f"❌ Pipeline Verification FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_pipeline()
