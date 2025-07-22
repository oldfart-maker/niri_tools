#!/usr/bin/env python3

def find_workspace_by_id(workspaces, wsp_id):
    for wsp in workspaces:
        if wsp_id == wsp.get("id", ""):
            return wsp
    return None

def find_workspace_by_name(workspaces, wsp_name):
    for wsp in workspaces:
        if wsp_name == wsp.get("name", ""):
            return wsp
    return None
