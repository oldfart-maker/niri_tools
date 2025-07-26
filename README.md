# niri_toolkit

A growing set of multi-language tools (mostly Python) created to extend [niri](https://niri.mitmaro.ca)’s capabilities by filling workflow gaps not yet addressed by stock niri commands.  

This toolkit is somewhat similar in spirit to [nirius](https://git.sr.ht/~tsdh/nirius), but focused entirely on practical tools I personally need and use.

---

## 🚀 RUNNING

To use:
1. Clone the repository.
2. Ensure the scripts are executable (`chmod +x script_name.py`)
3. Run any script directly with appropriate arguments.

---

## 🔧 TOOLS

### `niri_move_window.py`

Moves a window by matching either its app ID or window title, then targets it to a specific workspace or monitor. You can also bring the moved window into focus.

**Usage:**
```bash
niri_move_window.py \
  --match "googlemessages" \
  --target m|w \
  --target_id "HDMI-A-1"|"workspace-name" \
  --focus
```

**Example Workflow:**
- You use a texting app in a workspace called `messaging`.
- You want to pull it to the center monitor to reply, then return it after.

**Commands:**
```bash
# Pull it to the center monitor:
niri_move_window.py --match "googlemessages" --target "m" --target_id "HDMI-A-1" --focus

# Send it back to the workspace:
niri_move_window.py --match "googlemessages" --target "w" --target_id "messaging"
```

---
### `niri_scratchpad

Moves the currently focused window to a workspace that acts as a scratchpad similar to the sway scratchpad. Use the --acton "put" to put the currently focused window into the workspace you have created to be your scratchpad, for example "scratchpad". Use --action "get" to retrieve the window(s) from your scratchpad workspace. If more than one window exists in the scratchpad workspace a list of windows will be displayed for selection using rofi.

**Usage:**
```bash
niri_scratchpad \
  --acton put|get \
  --scratchpad_name "scratchpad" \
```

**Commands:**
```bash
# Put focused window in a workspace named "my_scratchpad"
niri_scratchpad --action "put" --scratchpad_name "my_scratchpad"

# Retrieve the window(s) from the workspace name "my_scratchpad"
niri_scratchpad --action "get" --scratchpad_name "my_scratchpad"
```

---

### `niri_tail_event_stream.py`

Connects to the niri IPC and outputs event messages to the console — similar to `niri msg event-stream`.

Use this to validate your IPC connection or to observe live event data for debugging or extension purposes.
