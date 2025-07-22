#!/usr/bin/env python3

from client.socket_path import get_niri_socket_path
from client.socket_client import connect_to_niri_socket
from client.socket_client import send_command
from ipc.actions import list_workspaces_query
from ipc.actions import list_windows_query
from util.workspace_utils import find_workspace_by_id
from util.workspace_utils import find_workspace_by_name
from util.window_utils import find_windows_by_workspace_id
import json

def main():
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

    wsp = find_workspace_by_name(workspaces, "scratchpad")
    # print(f"Worksapce for name scratchpad: {wsp}")

    response = send_command(socket_path, list_windows_query())

    if isinstance(response.get("Ok"), dict) and "Windows" in response["Ok"]:
        windows = response["Ok"]["Windows"]
    else:
        windows = response.get("Ok", [])

    print("Raw IPC Response-Windows:")
    print(json.dumps(response, indent=2))
    
    win = find_windows_by_workspace_id(windows, wsp.get("id",""))
    print(f"Windows for workspace: {wsp.get("id","")}")
    print(f"{win}")
                                       
if __name__ == "__main__":
    main()
