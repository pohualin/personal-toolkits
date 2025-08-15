import pandas as pd
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

def load_excel_file():
    """Load and display Excel file from customer sync directory."""
    sync_dir = os.getenv('CUSTOMER_SYNC_DIR')
    if not sync_dir:
        raise ValueError("CUSTOMER_SYNC_DIR environment variable is required")
    target_dir = os.path.expanduser(sync_dir)
    
    if not os.path.isdir(target_dir):
        print(f"Directory {target_dir} does not exist.")
        sys.exit(1)
    
    # Find all Excel files in the directory
    excel_files = []
    for file in os.listdir(target_dir):
        if file.endswith(('.xlsx', '.xls')):
            excel_files.append(os.path.join(target_dir, file))
    
    if not excel_files:
        print(f"No Excel files found in {target_dir}")
        sys.exit(1)
    
    # Load the first Excel file found
    excel_file = excel_files[0]
    print(f"Loading Excel file: {excel_file}")
    
    try:
        df = pd.read_excel(excel_file, usecols="A", sheet_name=0)
        # Concatenate 1000 rows at a time with a space and print until all rows are printed
        col_values = df.iloc[:, 0].astype(str).tolist()

        for i in range(0, len(col_values), 1000):
            concat_1000 = " ".join(col_values[i:i+1000])    

            url = "https://fusion.trustwave.com/customer-user-access-service/json/admin/commonSearchSyncCustomers"
            headers = {
                "X-TW-SESSION-CLIENTID": "portal-d9309503-b734-49ab-b1aa-cad8d0b51b35",
                "Content-Type": "application/json",
            }
            payload = {
                "@twrpc": "1.0",
                "@data": [f"{concat_1000}"]
            }

            response = requests.post(url, headers=headers, json=payload)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error loading Excel file: {e}")

if __name__ == "__main__":
    load_excel_file()