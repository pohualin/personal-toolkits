"""Convert JSON customer data to Excel format."""

import os
from util.data_processor import JSONProcessor, ExcelExporter
from util.file_utils import ensure_file_exists, generate_timestamped_filename


def parse_json_to_excel(input_file: str = None, output_dir: str = None) -> None:
    """Parse JSON customer data and export to Excel."""
    # Default paths
    input_file = input_file or os.path.expanduser("~/Workspace/customer_sync/true_active.json")
    output_dir = output_dir or "~/Workspace/customer_sync"
    
    # Validate input file
    if not ensure_file_exists(input_file):
        print(f"File not found: {input_file}")
        return
    
    try:
        # Load and process data
        data = JSONProcessor.load_json(input_file)
        customers = JSONProcessor.extract_customers(data)
        
        print(f"Extracted {len(customers)} customers")
        
        # Generate output file path
        output_file = generate_timestamped_filename(
            "customers", "xlsx", output_dir
        )
        
        # Export to Excel
        df = ExcelExporter.export_to_excel(
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