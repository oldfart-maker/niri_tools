#!/usr/bin/env python3
import json
from tabulate import tabulate
import subprocess

output = subprocess.check_output(["niri", "msg", "-j", "windows"]).decode()
windows = json.loads(output)

table = []
for win in windows:
    table.append([
        win.get("id"),
        win.get("title", "")[:30],
        win.get("app_id", ""),
        win.get("workspace_id", ""),
        win.get("is_focused", ""),
        win.get("is_floating", ""),
        win.get("is_urgent", "")
    ])

headers = ["ID", "Title", "App ID", "WS", "Focused", "Floating", "Urgent"]
print(tabulate(table, headers=headers, tablefmt="github"))
