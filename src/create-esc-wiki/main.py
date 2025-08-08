#!/usr/bin/env python3

import argparse
import logging
import sys
from dotenv import load_dotenv
from .sync import CreateEscWiki

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def main():
    parser = argparse.ArgumentParser(description="Sync Jira issues from filter to Confluence pages")
    parser.add_argument('-f', '--filter-id', type=str, required=True,
                       help='Jira filter ID to sync issues from')
    
    args = parser.parse_args()
    
    try:
        sync_service = CreateEscWiki()
        results = sync_service.sync_filter_to_confluence(args.filter_id)
        
        print(f"\nSync Results:")
        print(f"  Total Issues: {results['total_issues']}")
        print(f"  Pages Created: {results['pages_created']}")
        print(f"  Pages Skipped: {results['pages_skipped']}")
        print(f"  Errors: {len(results['errors'])}")
        
        if results['errors']:
            print("\nErrors:")
            for error in results['errors']:
                print(f"  - {error}")
        
    except Exception as e:
        logging.error(f"Sync failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()