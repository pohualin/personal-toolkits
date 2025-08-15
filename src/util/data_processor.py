"""Data processing utilities for JSON and Excel operations."""

import json
import pandas as pd
from typing import List, Dict, Any


def load_json(file_path: str) -> Dict[str, Any]:
    """Load JSON data from file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def extract_customers(data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extract customer data from OpenSearch response."""
    customers = []
    
    if 'hits' in data and 'hits' in data['hits']:
        hits = data['hits']['hits']
        
        for hit in hits:
            customer_id = hit.get('_id', '')
            source = hit.get('_source', {})
            customer_name = source.get('customerName', '')
            
            # Extract product names
            customer_products = source.get('customerProducts', [])
            product_names = [
                str(product['productName']) 
                for product in customer_products 
                if isinstance(product, dict) and product.get('productName')
            ]
            
            customers.append({
                'Customer ID': customer_id,
                'Customer Name': customer_name,
                'Products': ', '.join(product_names)
            })
    
    return customers


def export_to_excel(data: List[Dict], output_path: str, columns: List[str] = None) -> pd.DataFrame:
    """Export data to Excel file."""
    df = pd.DataFrame(data, columns=columns)
    df.to_excel(output_path, index=False)
    return df