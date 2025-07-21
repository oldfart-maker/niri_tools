#!/usr/bin/env python3

import os
import glob

def get_niri_socket_path():
    """Locate the Niri IPCUnix socket."""
    xdg_runtime = os.environ.get("XDG_RUNTIME_DIR", "/tmp")
    pattern = os.path.join(xdg_runtime, "niri.wayland-1.*.sock")
    matches = glob.glob(pattern)
    return matches[0] if matches else None
