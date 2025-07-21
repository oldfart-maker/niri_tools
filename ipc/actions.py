#!/usr/bin/env python3

def list_windows_query():
    return '"Windows"'  # The special IPC identifier Niri understands

def move_window_to_workspace_action(window_id, reference, focus=True):
    return {
        "Action": {
            "MoveWindowToWorkspace": {
                "window_id": window_id,
                "reference": reference,
                "focus": focus
            }
        }
    }

def focus_window_action(window_id):
    return {
        "Action": {
            "FocusWindow": {
                "id": window_id
            }
        }
    }

def move_window_to_monitor_action(window_id, output):
    return {
        "Action": {
            "MoveWindowToMonitor": {
                "id": window_id,
                "output": output
            }
        }
    }

def format_workspace_reference(workspace):
    if workspace.isdigit():
        return {"Index": int(workspace)}
    return {"Name": workspace}
