import unittest
import pandas as pd
import numpy as np
import fraud_forensics as ff
from datetime import datetime, timedelta

class TestFraudForensics(unittest.TestCase):

    def setUp(self):
        # Create a sample DataFrame for testing
        self.data = {
            'Date': pd.date_range('2025-01-01', periods=10, freq='h'),
            'Vendor': ['VendorA', 'VendorB', 'VendorA', 'VendorC', 'VendorB',
                       'VendorA', 'VendorD', 'VendorE', 'VendorA', 'VendorF'],
            'Amount': ['100.00', '200.00', '100.00', '50.00', '200.00', 
                       '5,000.00', '123.45', '10.00', '100.00', '9999.00'],
            'tx_id': range(10)
        }
        self.df = pd.DataFrame(self.data)
        
        # Add a duplicate for rule testing
        self.df.loc[2, 'Amount'] = '100.00' # Make sure it matches row 0 for VendorA
        
        # Add a round number
        self.df.loc[5, 'Amount'] = '5000.00'

    def test_prepare_features(self):
        print("\nTesting prepare_features...")
        df_processed = ff.prepare_features(self.df.copy(), time_col='Date', amount_col='Amount')
        
        # Check if Amount is numeric
        self.assertTrue(pd.api.types.is_numeric_dtype(df_processed['Amount']))
        
        # Check for new columns
        expected_cols = ['hour', 'weekday', 'amount_log', 'vendor_freq']
        for col in expected_cols:
            self.assertIn(col, df_processed.columns)
            
        # Check amount cleaning (5,000.00 -> 5000.0)
        self.assertEqual(df_processed.loc[5, 'Amount'], 5000.0)

    def test_detectors_integration(self):
        print("\nTesting detectors (IF and LOF)...")
        df_processed = ff.prepare_features(self.df.copy(), time_col='Date', amount_col='Amount')
        
        # Run detectors
        df_scored = ff.run_detectors(df_processed)
        
        self.assertIn('iforest_score', df_scored.columns)
        self.assertIn('lof_score', df_scored.columns)
        
        # Check scores are normalized [0, 1]
        self.assertTrue(df_scored['iforest_score'].between(0, 1).all())
        self.assertTrue(df_scored['lof_score'].between(0, 1).all())

    def test_rules_engine(self):
        print("\nTesting rules_engine...")
        df_processed = ff.prepare_features(self.df.copy(), time_col='Date', amount_col='Amount')
        
        # We manually created a duplicate: Row 0 and Row 2 (VendorA, 100.00)
        # And a high round number: Row 5 (VendorA, 5000.00)
        
        alerts = ff.rules_engine(df_processed, amount_col='Amount', high_amount_thresh=1000, round_threshold=100)
        
        alert_types = [a['type'] for a in alerts]
        
        # Check for duplicate alert
        self.assertIn('duplicate', alert_types)
        
        # Check for round_amount alert
        self.assertIn('round_amount', alert_types)
        
        # Check for high_value alert
        self.assertIn('high_value', alert_types)

    def test_ensemble_scores(self):
        print("\nTesting ensemble_scores...")
        df_processed = ff.prepare_features(self.df.copy(), time_col='Date', amount_col='Amount')
        df_scored = ff.run_detectors(df_processed)
        
        df_final = ff.ensemble_scores(df_scored, score_cols=['iforest_score', 'lof_score'])
        
        self.assertIn('risk_score', df_final.columns)
        self.assertIn('risk_explainer', df_final.columns)

    def test_graph_collusion(self):
        print("\nTesting graph_collusion_detector...")
        # Create data that should trigger collusion logic
        # Multiple transactions sharing same Card but different devices/vendors? 
        # The logic in source is: 
        # "components with many distinct cards or repeated device reuse"
        # Logic: if len(tx_nodes) >= 5 and (len(card_nodes) > len(device_nodes) * 2 or len(device_nodes) == 1)
        
        data = {
            'tx_id': range(10),
            'Vendor': ['V1']*10,
            'Card': [f'C{i}' for i in range(10)], # 10 different cards
            'Device': ['D1']*10 # 1 single device
        }
        df_graph = pd.DataFrame(data)
        
        suspicious = ff.graph_collusion_detector(df_graph, node_cols=['Card', 'Device'], min_component_size=5)
        
        self.assertTrue(len(suspicious) > 0)
        self.assertEqual(suspicious[0]['devices'], 1)
        self.assertEqual(suspicious[0]['cards'], 10)

if __name__ == '__main__':
    unittest.main()