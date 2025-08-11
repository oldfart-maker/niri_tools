#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shlex
from functools import partial

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QColorDialog, QGroupBox, QCheckBox, QMessageBox, QScrollArea,
    QFrame
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

# ----------------------------------------------------------------------------- 
# Config paths & IO
# -----------------------------------------------------------------------------

CONFIG_PATH = os.path.expanduser('~/.config/niri/config.kdl')

def load_config_text():
    """Read the entire config file."""
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def save_config_text(content):
    """Write back the updated config."""
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

# ----------------------------------------------------------------------------- 
# Parsing + reconstruction
# -----------------------------------------------------------------------------

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
        clean = stripped.lstrip('/ ').strip() if not enabled else stripped

        try:
            tokens = shlex.split(clean)
        except ValueError:
            # Skip malformed lines rather than crashing
            continue

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
                if isinstance(pval, str) and pval.startswith('#'):
                    param_strs.append(f'{pkey}="{pval}"')
                elif isinstance(pval, str) and pval.isdigit():
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

# ----------------------------------------------------------------------------- 
# Qt widgets
# -----------------------------------------------------------------------------

def _color_preview(color_hex: str) -> QFrame:
    frame = QFrame()
    frame.setFixedSize(32, 18)
    frame.setFrameShape(QFrame.Box)
    frame.setStyleSheet(f"background-color: {color_hex or '#000000'};")
    return frame

class FocusRingEditor(QWidget):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Niri Focus Ring Editor (Qt)")
        self.items = items  # list of dicts; we’ll attach widgets to each dict

        # Scrollable area
        outer = QVBoxLayout(self)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)

        # Build per-item UIs
        for item in self.items:
            g = QGroupBox(item['key'])
            gl = QHBoxLayout(g)

            # checkbox for enabled on all except 'width' special-case
            add_enable_box = not (item['type'] == 'simple' and item['key'] == 'width')

            if add_enable_box:
                item['check'] = QCheckBox(self)
                item['check'].setChecked(bool(item['enabled']))
                gl.addWidget(item['check'])

            if item['type'] == 'off':
                gl.addWidget(QLabel("off", self))

            elif item['type'] == 'simple':
                gl.addWidget(QLabel(item['key'] + ":", self))
                item['entry'] = QLineEdit(str(item['value']), self)
                item['entry'].setFixedWidth(80)
                gl.addWidget(item['entry'])

            elif item['type'] == 'color':
                gl.addWidget(QLabel(item['key'] + ":", self))
                item['color_edit'] = QLineEdit(item.get('value', ''), self)
                item['color_edit'].setFixedWidth(110)
                gl.addWidget(item['color_edit'])

                # color picker
                btn = QPushButton("Pick", self)
                gl.addWidget(btn)
                # preview
                item['preview'] = _color_preview(item.get('value', '#000000'))
                gl.addWidget(item['preview'])

                # bind item; ignore clicked(bool)
                btn.clicked.connect(partial(self._pick_color_for, item))

                # keep preview in sync if typed
                item['color_edit'].textChanged.connect(
                    lambda txt, it=item: it['preview'].setStyleSheet(f"background-color: {txt or '#000000'};")
                )

            elif item['type'] == 'gradient':
                gl.addWidget(QLabel(item['key'] + ":", self))

                # from
                gl.addWidget(QLabel("from", self))
                item['from_edit'] = QLineEdit(item['value'].get('from', ''), self)
                item['from_edit'].setFixedWidth(110)
                gl.addWidget(item['from_edit'])
                from_btn = QPushButton("Pick", self)
                gl.addWidget(from_btn)
                item['from_preview'] = _color_preview(item['value'].get('from', '#000000'))
                gl.addWidget(item['from_preview'])
                from_btn.clicked.connect(partial(self._pick_from_color, item))
                item['from_edit'].textChanged.connect(
                    lambda txt, it=item: it['from_preview'].setStyleSheet(f"background-color: {txt or '#000000'};")
                )

                # to
                gl.addWidget(QLabel("to", self))
                item['to_edit'] = QLineEdit(item['value'].get('to', ''), self)
                item['to_edit'].setFixedWidth(110)
                gl.addWidget(item['to_edit'])
                to_btn = QPushButton("Pick", self)
                gl.addWidget(to_btn)
                item['to_preview'] = _color_preview(item['value'].get('to', '#000000'))
                gl.addWidget(item['to_preview'])
                to_btn.clicked.connect(partial(self._pick_to_color, item))
                item['to_edit'].textChanged.connect(
                    lambda txt, it=item: it['to_preview'].setStyleSheet(f"background-color: {txt or '#000000'};")
                )

                # angle
                gl.addWidget(QLabel("angle", self))
                item['angle_edit'] = QLineEdit(str(item['value'].get('angle', '')), self)
                item['angle_edit'].setFixedWidth(60)
                gl.addWidget(item['angle_edit'])

                # relative-to
                gl.addWidget(QLabel("relative-to", self))
                item['rel_edit'] = QLineEdit(item['value'].get('relative-to', ''), self)
                item['rel_edit'].setFixedWidth(160)
                gl.addWidget(item['rel_edit'])

            gl.addStretch(1)
            g.setLayout(gl)
            layout.addWidget(g)

        # Save button + status
        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save Configuration", self)
        btn_row.addWidget(save_btn)
        self.status_label = QLabel("", self)
        self.status_label.setStyleSheet("color: green;")
        btn_row.addWidget(self.status_label, alignment=Qt.AlignLeft)
        layout.addLayout(btn_row)

        layout.addStretch(1)
        scroll.setWidget(container)
        outer.addWidget(scroll)

        save_btn.clicked.connect(self.on_save)

        # Size hint
        self.resize(860, 600)

    # ------------------------------------------------------------------ 
    # Color pickers (ignore clicked(bool) via partial)
    # ------------------------------------------------------------------ 

    def _pick_color_for(self, it, _checked=False):
        col0 = it['color_edit'].text() or "#000000"
        color = QColorDialog.getColor(QColor(col0), self, "Pick color")
        if color.isValid():
            it['color_edit'].setText(color.name())
            it['preview'].setStyleSheet(f"background-color: {color.name()};")

    def _pick_from_color(self, it, _checked=False):
        c0 = it['from_edit'].text() or "#000000"
        color = QColorDialog.getColor(QColor(c0), self, "Pick color (from)")
        if color.isValid():
            it['from_edit'].setText(color.name())
            it['from_preview'].setStyleSheet(f"background-color: {color.name()};")

    def _pick_to_color(self, it, _checked=False):
        c0 = it['to_edit'].text() or "#000000"
        color = QColorDialog.getColor(QColor(c0), self, "Pick color (to)")
        if color.isValid():
            it['to_edit'].setText(color.name())
            it['to_preview'].setStyleSheet(f"background-color: {color.name()};")

    # ------------------------------------------------------------------ 
    # Save
    # ------------------------------------------------------------------ 

    def on_save(self):
        """Collect UI state -> items -> reconstruct -> replace block -> write."""
        # Collect values back from widgets
        for it in self.items:
            if it['type'] == 'off':
                if 'check' in it:
                    it['enabled'] = it['check'].isChecked()

            elif it['type'] == 'simple':
                if it['key'] == 'width':
                    if 'entry' in it:
                        it['value'] = it['entry'].text().strip()
                else:
                    if 'check' in it:
                        it['enabled'] = it['check'].isChecked()
                    if 'entry' in it:
                        it['value'] = it['entry'].text().strip()

            elif it['type'] == 'color':
                if 'check' in it:
                    it['enabled'] = it['check'].isChecked()
                if 'color_edit' in it:
                    it['value'] = it['color_edit'].text().strip()

            elif it['type'] == 'gradient':
                if 'check' in it:
                    it['enabled'] = it['check'].isChecked()
                v = it['value']
                if 'from_edit' in it:
                    v['from'] = it['from_edit'].text().strip()
                if 'to_edit' in it:
                    v['to'] = it['to_edit'].text().strip()
                if 'angle_edit' in it:
                    v['angle'] = it['angle_edit'].text().strip()
                if 'rel_edit' in it:
                    v['relative-to'] = it['rel_edit'].text().strip()

        # Reconstruct + write
        try:
            content = load_config_text()  # reload to avoid external drift
            start, end, lines = find_focus_ring_block(content)
            new_block = reconstruct_block(self.items)
            updated_lines = lines[:start] + new_block.splitlines() + lines[end + 1:]
            updated = '\n'.join(updated_lines)
            save_config_text(updated)
            self.status_label.setText("Changes saved! Check Niri.")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

# ----------------------------------------------------------------------------- 
# main
# -----------------------------------------------------------------------------

def main():
    try:
        content = load_config_text()
        start, end, lines = find_focus_ring_block(content)
        items = parse_focus_ring(lines, start, end)
    except Exception as e:
        app = QApplication([])
        QMessageBox.critical(None, "Error", str(e))
        return

    app = QApplication([])
    w = FocusRingEditor(items)
    w.show()
    app.exec_()

if __name__ == "__main__":
    main()
