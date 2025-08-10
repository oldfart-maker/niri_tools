import tkinter as tk
from tkinter import messagebox, colorchooser
import os
import shlex

# Config file path
CONFIG_PATH = os.path.expanduser('~/.config/niri/config.kdl')

def load_config():
    """Read the entire config file."""
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")
    with open(CONFIG_PATH, 'r') as f:
        return f.read()

def save_config(content):
    """Write back the updated config."""
    with open(CONFIG_PATH, 'w') as f:
        f.write(content)
    print("Config saved! Changes should apply immediately in Niri.")

def find_focus_ring_block(content):
    """Find the start and end lines of the focus-ring block."""
    lines = content.splitlines()
    start = None
    end = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == 'focus-ring {':
            start = i
        elif start is not None and stripped == '}':
            end = i
            break
    if start is None or end is None:
        raise ValueError("focus-ring block not found in config.")
    return start, end, lines

def parse_focus_ring(lines, start, end):
    """Parse each configurable line in the block into items."""
    items = []
    for i in range(start + 1, end):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            continue  # Skip empty lines
        enabled = not stripped.startswith('//')
        if not enabled:
            clean = stripped.lstrip('/ ').strip()
        else:
            clean = stripped
        # Parse clean into tokens
        try:
            tokens = shlex.split(clean)
        except ValueError:
            continue  # Invalid line, skip
        if not tokens:
            continue
        key = tokens[0]
        if key == 'off':
            item = {'type': 'off', 'enabled': enabled, 'value': None, 'key': 'off'}
        elif len(tokens) == 2 and key.endswith('-color'):
            value = tokens[1].strip('"')
            if value.startswith('#'):
                item = {'type': 'color', 'enabled': enabled, 'value': value, 'key': key}
            else:
                item = {'type': 'simple', 'enabled': enabled, 'value': tokens[1], 'key': key}
        elif 'gradient' in key and len(tokens) > 1:
            params = {}
            for t in tokens[1:]:
                if '=' in t:
                    pkey, pval = t.split('=', 1)
                    params[pkey] = pval.strip('"')
            if 'from' in params and 'to' in params:
                item = {'type': 'gradient', 'enabled': enabled, 'value': params, 'key': key}
            else:
                continue
        else:
            if len(tokens) == 2:
                item = {'type': 'simple', 'enabled': enabled, 'value': tokens[1], 'key': key}
            else:
                continue
        items.append(item)
    return items

def reconstruct_block(items):
    """Rebuild the focus-ring block from items."""
    new_block = ['    focus-ring {']
    for item in items:
        if item['type'] == 'off':
            assembled = 'off'
        elif item['type'] == 'simple':
            assembled = f"{item['key']} {item['value']}"
        elif item['type'] == 'color':
            assembled = f"{item['key']} \"{item['value']}\""
        elif item['type'] == 'gradient':
            params = item['value']
            param_strs = []
            for pkey, pval in params.items():
                if pval.startswith('#'):
                    param_strs.append(f'{pkey}="{pval}"')
                elif pval.isdigit():
                    param_strs.append(f'{pkey}={pval}')
                else:
                    param_strs.append(f'{pkey}="{pval}"')
            assembled = f"{item['key']} {' '.join(param_strs)}"
        if item['enabled']:
            new_block.append(f'                    {assembled}')
        else:
            new_block.append(f'                    // {assembled}')
    new_block.append('            }')
    return '\n'.join(new_block)

def update_preview(preview_label, color_var):
    """Update the background color of the preview label, handling invalid colors."""
    color = color_var.get()
    try:
        preview_label.config(bg=color)
    except tk.TclError:
        pass  # Invalid color, keep previous or default

def create_gui(items):
    """Build the Tkinter GUI for editing."""
    root = tk.Tk()
    root.title("Niri Focus Ring Editor")
    root.geometry("600x600")  # Larger to fit gradients
    root.attributes('-topmost', True)  # Stay on top

    row = 0
    for idx, item in enumerate(items):
        frame = tk.Frame(root)
        frame.grid(row=row, column=0, columnspan=2, padx=10, pady=5, sticky='w')
        item['check_var'] = tk.BooleanVar(value=item['enabled'])
        check = tk.Checkbutton(frame, text="", variable=item['check_var'])
        check.pack(side=tk.LEFT)

        if item['type'] == 'off':
            tk.Label(frame, text="off").pack(side=tk.LEFT)
        elif item['type'] == 'simple':
            tk.Label(frame, text=f"{item['key']}: ").pack(side=tk.LEFT)
            item['entry_var'] = tk.StringVar(value=item['value'])
            tk.Entry(frame, textvariable=item['entry_var'], width=10).pack(side=tk.LEFT)
        elif item['type'] == 'color':
            tk.Label(frame, text=f"{item['key']}: ").pack(side=tk.LEFT)
            item['color_var'] = tk.StringVar(value=item['value'])
            entry = tk.Entry(frame, textvariable=item['color_var'], width=15)
            entry.pack(side=tk.LEFT)
            def pick_color(color_var):
                color = colorchooser.askcolor(initialcolor=color_var.get())[1]
                if color:
                    color_var.set(color)
            tk.Button(frame, text="Pick", command=lambda cv=item['color_var']: pick_color(cv)).pack(side=tk.LEFT)
            # Color preview
            preview_label = tk.Label(frame, width=4, height=1, bg=item['color_var'].get(), relief="solid", borderwidth=1)
            preview_label.pack(side=tk.LEFT, padx=5)
            item['color_var'].trace("w", lambda *args, pl=preview_label, cv=item['color_var']: update_preview(pl, cv))
        elif item['type'] == 'gradient':
            tk.Label(frame, text=f"{item['key']}: ").pack(side=tk.LEFT)
            # From
            tk.Label(frame, text="from ").pack(side=tk.LEFT)
            item['from_var'] = tk.StringVar(value=item['value'].get('from', '#000000'))
            from_entry = tk.Entry(frame, textvariable=item['from_var'], width=15)
            from_entry.pack(side=tk.LEFT)
            tk.Button(frame, text="Pick", command=lambda cv=item['from_var']: pick_color(cv)).pack(side=tk.LEFT)
            from_preview = tk.Label(frame, width=4, height=1, bg=item['from_var'].get(), relief="solid", borderwidth=1)
            from_preview.pack(side=tk.LEFT, padx=5)
            item['from_var'].trace("w", lambda *args, pl=from_preview, cv=item['from_var']: update_preview(pl, cv))
            # To
            tk.Label(frame, text=" to ").pack(side=tk.LEFT)
            item['to_var'] = tk.StringVar(value=item['value'].get('to', '#000000'))
            to_entry = tk.Entry(frame, textvariable=item['to_var'], width=15)
            to_entry.pack(side=tk.LEFT)
            tk.Button(frame, text="Pick", command=lambda cv=item['to_var']: pick_color(cv)).pack(side=tk.LEFT)
            to_preview = tk.Label(frame, width=4, height=1, bg=item['to_var'].get(), relief="solid", borderwidth=1)
            to_preview.pack(side=tk.LEFT, padx=5)
            item['to_var'].trace("w", lambda *args, pl=to_preview, cv=item['to_var']: update_preview(pl, cv))
            # Angle
            tk.Label(frame, text=" angle ").pack(side=tk.LEFT)
            item['angle_var'] = tk.StringVar(value=item['value'].get('angle', '45'))
            tk.Entry(frame, textvariable=item['angle_var'], width=5).pack(side=tk.LEFT)
            # Relative-to
            tk.Label(frame, text=" relative-to ").pack(side=tk.LEFT)
            item['rel_var'] = tk.StringVar(value=item['value'].get('relative-to', 'workspace-view'))
            tk.Entry(frame, textvariable=item['rel_var'], width=20).pack(side=tk.LEFT)
        row += 1

    status_label = tk.Label(root, text="", fg="green")
    status_label.grid(row=row, column=0, columnspan=2, pady=5)

    def save_changes():
        for item in items:
            item['enabled'] = item['check_var'].get()
            if item['type'] == 'simple':
                item['value'] = item['entry_var'].get()
            elif item['type'] == 'color':
                item['value'] = item['color_var'].get()
            elif item['type'] == 'gradient':
                item['value']['from'] = item['from_var'].get()
                item['value']['to'] = item['to_var'].get()
                item['value']['angle'] = item['angle_var'].get()
                item['value']['relative-to'] = item['rel_var'].get()
        
        content = load_config()  # Reload to avoid external changes conflicts
        start, end, lines = find_focus_ring_block(content)
        new_block = reconstruct_block(items)
        
        # Replace the old block
        updated_lines = lines[:start] + new_block.splitlines() + lines[end + 1:]
        updated_content = '\n'.join(updated_lines)
        
        save_config(updated_content)
        status_label.config(text="Changes saved! Check Niri.")
        root.after(3000, lambda: status_label.config(text=""))  # Clear message after 3 seconds

    tk.Button(root, text="Save", command=save_changes).grid(row=row + 1, column=0, columnspan=2, pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    try:
        content = load_config()
        start, end, lines = find_focus_ring_block(content)
        items = parse_focus_ring(lines, start, end)
        create_gui(items)
    except Exception as e:
        print(f"Error: {e}")
        # Could add GUI error if desired
