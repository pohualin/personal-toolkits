#!/usr/bin/env python3

import datetime
from src.util.gmail_util import send

print(f"[{datetime.datetime.now()}] personal-toolkits script started")
subject = "personal-toolkits started"
body = f"personal-toolkits started at {datetime.datetime.now()}!!"
to = "pohualin@gmail.com"

send(subject=subject, body=body, to=to)