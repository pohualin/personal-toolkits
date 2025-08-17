#!/usr/bin/env python3

import datetime
from src.util.gmail_util import send_gmail

print(f"[{datetime.datetime.now()}] personal-toolkits script started")
subject = "personal-toolkits started"
body = f"personal-toolkits started at {datetime.datetime.now()}!!"
to = "pohualin@gmail.com"

send_gmail(subject=subject, body=body, to=to)