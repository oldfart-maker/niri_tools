#!/usr/bin/env python3

from cmds.scratchpad import get_windows_from_scratchpad
import argparse
import json

def main():
    parser = argparse.ArgumentParser(description="Manage Niri scratchpad workspace.")
    parser.add_argument("--scratchpad_name", required=True, help="Name of scratchpad workspace (e.g. myscratchpad)")
    args = parser.parse_args()

    windows = get_windows_from_scratchpad(args.scratchpad_name)

    print(json.dumps(windows))

if __name__ == "__main__":
    main()
