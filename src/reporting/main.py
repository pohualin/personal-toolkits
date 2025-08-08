#!/usr/bin/env python3

import logging
from datetime import datetime
from ..util.logging_config import setup_logging
from .fetch_esc_kpi import fetch_esc_kpi, analyze_filter_18891
from .fetch_weekly_report import main as weekly_report_main

def main():
    """Run ESC KPI report followed by weekly report"""
    try:
        # Run ESC KPI report
        logging.info("Starting ESC KPI report")
        print(f"Weekly Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        fetch_esc_kpi()
        analyze_filter_18891()
        
        # Run weekly report
        weekly_report_main()
        
        logging.info("All reports completed successfully")
        
    except Exception as e:
        logging.error(f"Error running reports: {e}")

if __name__ == "__main__":
    main()