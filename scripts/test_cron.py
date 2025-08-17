#!/usr/bin/env python3

import datetime
from src.util.gmail_util import send_gmail

print(f"Script started at {datetime.datetime.now()}")
subject = "Test cron job"
body = f"Hello World! - {datetime.datetime.now()}"
to = "pohualin@gmail.com"

send_gmail(subject=subject, body=body, to=to)