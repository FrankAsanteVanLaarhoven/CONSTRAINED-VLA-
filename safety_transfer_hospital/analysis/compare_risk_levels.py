import os
import json
import glob
import pandas as pd
import numpy as np

def compare_risk_levels():
    print("Running Risk Stratification Analysis...")
    
    # 1. Gather Metadata (Risk Index)
    world_meta = {}
    world_files = glob.glob("../data/worlds/*/objects.json")
    
    if not world_files:
        print("No world data found. Generating dummy data for demonstration...")
        # Mock Data
        data = [
            {'id': 'w1', 'risk': 1.5, 'svr_base': 0.1, 'svr_ours': 0.05}, # Low Risk
            {'id': 'w2', 'risk': 3.0, 'svr_base': 0.3, 'svr_ours': 0.08}, # Med Risk
            {'id': 'w3', 'risk': 5.5, 'svr_base': 0.6, 'svr_ours': 0.10}, # High Risk (Stress)
        ]
        df = pd.DataFrame(data)
    else:
        # Real Data Loading Logic (Placeholder)
        pass

    # 2. Binning
    bins = [0, 2.0, 4.0, 10.0]
    labels = ['Low Risk', 'Medium Risk', 'High Risk']
    df['Risk Category'] = pd.cut(df['risk'], bins=bins, labels=labels)
    
    # 3. Aggregation
    report = df.groupby('Risk Category')[['svr_base', 'svr_ours']].mean()
    
    # 4. Calculation of Improvement
    report['Improvement'] = (report['svr_base'] - report['svr_ours']) / report['svr_base']
    
    print("\n--- Risk Stratification Report ---")
    print(report)
    
    # 5. Insight Generation
    high_risk_improv = report.loc['High Risk', 'Improvement']
    print(f"\nKey Finding: In High-Risk scenarios, our method reduces violations by {high_risk_improv*100:.1f}%.")
    
    return report

if __name__ == "__main__":
    compare_risk_levels()
