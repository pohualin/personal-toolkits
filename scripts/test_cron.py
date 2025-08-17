#!/usr/bin/env python3

import datetime
from util.gmail_util import send_gmail

subject = "Test cron job"
body = f"Hello World! - {datetime.datetime.now()}"
to = "pohualin@gmail.com"

send_gmail(subject=subject, body=body, to=to)