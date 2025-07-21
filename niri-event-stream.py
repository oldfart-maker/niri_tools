#!/usr/bin/env python3
import subprocess
import json
import sys

def format_kv(d, indent=0):
    pad = "  " * indent
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, dict):
                print(f"{pad}{k}:")
                format_kv(v, indent + 1)
            else:
                print(f"{pad}{k}: {v}")
    else:
        print(f"{pad}{d}")

def main():
    proc = subprocess.Popen(
        ["niri", "msg", "-j", "event-stream"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    try:
        for line in proc.stdout:
            try:
                event = json.loads(line)
                print("Event:")
                format_kv(event)
                print("-" * 40)
            except Exception as e:
                print(f"Error parsing JSON: {e}", file=sys.stderr)
    except KeyboardInterrupt:
        proc.terminate()

if __name__ == "__main__":
    main()
