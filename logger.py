import json
import os
from datetime import datetime

LOG_FILE = "request_log.json"


def save_log(data):

    data["processed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)

    with open(LOG_FILE, "r") as f:
        logs = json.load(f)

    logs.append(data)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)