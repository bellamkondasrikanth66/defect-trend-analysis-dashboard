import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_mock_data(num_records=500):
    np.random.seed(42)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    # Generate random creation dates
    creation_dates = [start_date + timedelta(days=int(np.random.randint(0, 180))) for _ in range(num_records)]
    
    modules = ['Authentication', 'Billing & Payments', 'Dashboard UI', 'API Gateway', 'Notification Engine']
    severities = ['Low', 'Medium', 'High', 'Critical']
    status_choices = ['Closed', 'Open', 'In Progress', 'Resolved']
    
    data = {
        'Defect_ID': [f'BUG-{i+1000}' for i in range(num_records)],
        'Creation_Date': creation_dates,
        'Module': np.random.choice(modules, num_records, p=[0.15, 0.25, 0.20, 0.25, 0.15]),
        'Severity': np.random.choice(severities, num_records, p=[0.30, 0.40, 0.20, 0.10]),
        'Status': np.random.choice(status_choices, num_records, p=[0.60, 0.15, 0.15, 0.10])
    }
    
    df = pd.DataFrame(data)
    
    # Logic for Resolution Date based on Status
    res_dates = []
    for _, row in df.iterrows():
        if row['Status'] in ['Closed', 'Resolved']:
            # Resolution happens 1 to 15 days after creation
            days_to_resolve = np.random.randint(1, 15)
            res_date = row['Creation_Date'] + timedelta(days=days_to_resolve)
            res_dates.append(res_date)
        else:
            res_dates.append(pd.NaT)
            
    df['Resolution_Date'] = res_dates
    df['Creation_Month'] = df['Creation_Date'].dt.to_period('M').astype(str)
    
    df.to_csv('defects_mock_data.csv', index=False)
    print("✅ 'defects_mock_data.csv' successfully generated with 500 records!")

if __name__ == "__main__":
    generate_mock_data()