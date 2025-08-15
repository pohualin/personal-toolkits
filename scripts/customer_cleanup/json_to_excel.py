"""Convert JSON customer data to Excel format."""

import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))
from util.data_processor import load_json, extract_customers, export_to_excel
from util.file_utils import ensure_file_exists, generate_timestamped_filename

load_dotenv()


def parse_json_to_excel(input_file: str = None, output_dir: str = None) -> None:
    """Parse JSON customer data and export to Excel."""
    # Get required environment variable
    sync_dir = os.getenv('CUSTOMER_SYNC_DIR')
    if not sync_dir:
        raise ValueError("CUSTOMER_SYNC_DIR environment variable is required")
    sync_dir = os.path.expanduser(sync_dir)
    input_file = input_file or os.path.join(sync_dir, "true_active.json")
    output_dir = output_dir or sync_dir
    
    # Validate input file
    if not ensure_file_exists(input_file):
        print(f"File not found: {input_file}")
        return
    
    try:
        # Load and process data
        data = load_json(input_file)
        customers = extract_customers(data)
        
        print(f"Extracted {len(customers)} customers")
        
        # Generate output file path
        output_file = generate_timestamped_filename(
            "customers", "xlsx", output_dir
        )
        
        # Export to Excel
        df = export_to_excel(
            customers, 
            output_file, 
            ['Customer ID', 'Customer Name', 'Products']
        )
        
        print(f"Excel file created: {output_file}")
        print("\nPreview of data:")
        print(df.head().to_string(index=False))
        
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    parse_json_to_excel()