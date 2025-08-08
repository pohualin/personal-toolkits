#!/usr/bin/env python3

import logging
import sys
import os
from datetime import datetime, timedelta
from ..util.logging_config import setup_logging
from ..util.output_capture import TeeOutput
from .fetch_esc_kpi import fetch_esc_kpi, analyze_filter_18891
from .fetch_weekly_report import main as weekly_report_main

def main():
    """Run ESC KPI report followed by weekly report"""
    # Create weekly_report directory if it doesn't exist
    report_dir = "weekly_report"
    os.makedirs(report_dir, exist_ok=True)
    
    # Create filename with YYYYmmdd format in weekly_report directory
    report_filename = os.path.join(report_dir, f"{(datetime.now() + timedelta(days=(7 - datetime.now().weekday()))).strftime('%Y%m%d')}_weekly_report.txt")
    
    # Setup output capture
    tee = TeeOutput(report_filename)
    original_stdout = sys.stdout
    sys.stdout = tee
    
    try:
        # Run ESC KPI report
        logging.info("Starting ESC KPI report")
        print(f"Weekly Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        fetch_esc_kpi()
        analyze_filter_18891()
        
        # Run weekly report
        logging.info("Starting weekly report")
        weekly_report_main()
        
        logging.info("All reports completed successfully")
        
    except Exception as e:
        logging.error(f"Error running reports: {e}")
    finally:
        # Restore original stdout and close file
        sys.stdout = original_stdout
        tee.close()

if __name__ == "__main__":
    main()