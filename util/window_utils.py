#!/usr/bin/env python3

def find_matching_window(windows, match_str):
    match_str = match_str.lower()

    for win in windows:
        title = win.get("title", "").lower()
        app_id = win.get("app_id", "").lower()

        if match_str in title or match_str in app_id:
            return win
    return None
