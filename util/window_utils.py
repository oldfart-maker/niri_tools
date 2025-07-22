#!/usr/bin/env python3

def find_matching_window(windows, match_str):
    match_str = match_str.lower()

    for win in windows:
        title = win.get("title", "").lower()
        app_id = win.get("app_id", "").lower()
        window_id = str(win.get("id", ""))  # Convert id to string

        if match_str in title or match_str in app_id or match_str in window_id:
            return win
    
    return None

def find_windows_by_workspace_id(windows, wsp_id):
    matching_windows = []
    for win in windows:
        if wsp_id == win.get("workspace_id",""):
            matching_windows.append(win)
    return matching_windows
