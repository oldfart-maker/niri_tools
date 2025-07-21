#!/usr/bin/env python3

from client.socket_client import send_command
from client.socket_path import get_niri_socket_path
from ipc.actions import (
    list_windows_query,
    move_window_to_workspace_action,
    move_window_to_monitor_action,
    focus_window_action,
    format_workspace_reference,
)
from util.window_utils import find_matching_window
import json

def move_window_by_match(args):
    sock_path = get_niri_socket_path()
    if not sock_path:
        print("❌ Could not find Niri IPC socket.")
        return
    
    print(f"📡 Using socket path: {sock_path}")
    print("📤 Sending IPC Request: Windows")
    response = send_command(sock_path, list_windows_query())

    print("📥 Raw IPC Response:")
    print(json.dumps(response, indent=2))

    if isinstance(response.get("Ok"), dict) and "Windows" in response["Ok"]:
        windows = response["Ok"]["Windows"]
    else:
        windows = response.get("Ok", [])

    print(f"📦 Found {len(windows)} window(s)")

    for win in windows:
        print(f"🪟 Window => ID: {win.get('id')}, Title: {win.get('title')}, App ID: {win.get('app_id')}")

    matched = find_matching_window(windows, args.match)
    if not matched:
        print(f"❌ No matching window found for: {args.match}")
        return

    print("✅ Found matching window")
    print(f"  🖼 Title: {matched.get('title')}")
    print(f"  🧩 App ID: {matched.get('app_id')}")

    window_id = matched["id"]

    if args.target == "w":
        ref = format_workspace_reference(args.target_id)
        action = move_window_to_workspace_action(window_id, ref, args.focus)
        print("📤 Sending MoveWindowToWorkspace...")
        result = send_command(sock_path, action)
        print("📥 Received:", result)
        
    if args.target == "m":
        print(f"  🧩 target_id: {args.target_id}")
        action = move_window_to_monitor_action(window_id, args.target_id)
        print("📤 Sending MoveWindowToMonitor...")
        result = send_command(sock_path, action)
        print("📥 Received:", result)

    if args.focus:
        action = focus_window_action(window_id)
        print("📤 Sending FocusWindow...")
        result = send_command(sock_path, action)
        print("📥 Received:", result)

