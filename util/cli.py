#!/usr/bin/env python3

import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Move a Niri window to a specific workspace.")
    parser.add_argument("--match", required=True, help="Match window title or app_id")
    parser.add_argument("--target", required=True, help="m=monitor, w=workspace")
    parser.add_argument("--target_id", required=True, help="Target name or index")
    parser.add_argument("--focus", action="store_true", help="Focus moved window")
    return parser.parse_args()
