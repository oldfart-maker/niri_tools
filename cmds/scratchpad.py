#!/usr/bin/env python3

from client.socket_client import (
    connect_to_niri_socket,
    send_command,
)

from client.socket_path import get_niri_socket_path

from ipc.actions import (
    list_windows_query,
    list_workspaces_query,
    move_window_to_workspace_action,
    move_window_to_monitor_action,
    focus_window_action,
    format_workspace_reference,
)

from util.window_utils import (
    find_matching_window,
    find_windows_by_workspace_id,
)

from util.workspace_utils import (
    find_workspace_by_name,    
)

import json

def get_windows_from_scratchpad(scratchpad_name):
    socket_path = get_niri_socket_path()
    if not socket_path:
        return

    sock = connect_to_niri_socket(socket_path)
    if not sock:
        return

    response = send_command(socket_path, list_workspaces_query())

    if isinstance(response.get("Ok"), dict) and "Workspaces" in response["Ok"]:
        workspaces = response["Ok"]["Workspaces"]
    else:
        workspaces = response.get("Ok", [])

    # print("Raw IPC Response-Workspaces:")
    # print(json.dumps(response, indent=2))

    # test module
    # wsp = find_workspace_by_id(workspaces, 4)
    # print(f"Workspace for id 4: {wsp}")

    wsp = find_workspace_by_name(workspaces, scratchpad_name)
    # print(f"Worksapce for name scratchpad: {wsp}")

    response = send_command(socket_path, list_windows_query())

    if isinstance(response.get("Ok"), dict) and "Windows" in response["Ok"]:
        windows = response["Ok"]["Windows"]
    else:
        windows = response.get("Ok", [])

    # print("Raw IPC Response-Windows:")
    # print(json.dumps(response, indent=2))
    
    win = find_windows_by_workspace_id(windows, wsp.get("id",""))
    # print(f"Windows for workspace: {wsp.get("id","")}")
    # print(f"{win}")

    return win

    
