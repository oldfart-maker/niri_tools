import json
import os
import tkinter as tk
from tkinter import colorchooser
import re
import threading

# Step 1: Load the config.kdl file
def load_config(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content

# Step 2: Modify the 'focus-ring' section
def modify_focus_ring(config_content, width, active_color, inactive_color, 
                      relative_to_active, relative_to_inactive, 
                      active_gradient_from, active_gradient_to, active_gradient_angle, 
                      inactive_gradient_from, inactive_gradient_to, inactive_gradient_angle, 
                      active_color_enabled, inactive_color_enabled, 
                      active_gradient_enabled, inactive_gradient_enabled):
    
    # Step 1: Regular expression to match the entire focus-ring section
    focus_ring_pattern = r"(focus-ring\s*{)(.*?)(})"
    
    match = re.search(focus_ring_pattern, config_content, re.DOTALL)

    if match:
        # Extract the section inside the focus-ring
        focus_ring_section = match.group(2)
        
        # Split the focus-ring section into lines
        focus_ring_lines = focus_ring_section.splitlines()
        modified_focus_ring_lines = []
        
        # Step 2: Process each line in the focus-ring section
        for line in focus_ring_lines:
            
            #print(f"focus ring line: {line}")            

            # Capture the leading spaces for indentation
            leading_spaces = len(line) - len(line.lstrip())
            
            # Modify the line by applying the logic to retain leading spaces
            if 'width' in line:
                modified_line = f"{' ' * leading_spaces}width {width}"
                modified_focus_ring_lines.append(modified_line)
                
            # Active color modification
            elif 'active-color' in line and not any('active-color' in l for l in modified_focus_ring_lines):
                modified_line = f"{' ' * leading_spaces}active-color \"{active_color}\""
                if not active_color_enabled:
                    modified_line = f"{' ' * leading_spaces}// {modified_line}"  # Prepend `//` if disabled
                modified_focus_ring_lines.append(modified_line)
                
            # Inactive color modification
            elif 'inactive-color' in line and not any('inactive-color' in l for l in modified_focus_ring_lines):
                modified_line = f"{' ' * leading_spaces}inactive-color \"{inactive_color}\""
                if not inactive_color_enabled:
                    modified_line = f"{' ' * leading_spaces}// {modified_line}"  # Prepend `//` if disabled
                modified_focus_ring_lines.append(modified_line)
                
            # Active gradient modification
            elif 'active-gradient' in line and not \
                 any('active-gradient' in l for l in modified_focus_ring_lines):
                
                modified_line = f"{' ' * leading_spaces}active-gradient " \
                f"from=\"{active_gradient_from}\" " \
                f"to=\"{active_gradient_to}\" " \
                f"angle={active_gradient_angle} " \
                f"relative-to=\"{relative_to_active}\""
                
                # Strip leading/trailing whitespace and ensure only a single space between components
                modified_line = ' '.join(modified_line.lstrip().split())
                
                # Reapply the leading spaces
                modified_line = ' ' * leading_spaces + modified_line

                if not active_gradient_enabled:
                    modified_line = f"{' ' * leading_spaces}// {modified_line}"
                    
                modified_focus_ring_lines.append(modified_line)
            
            # Inactive gradient modification
            elif 'inactive-gradient' in line and not \
                 any('inactive-gradient' in l for l in modified_focus_ring_lines):

                modified_line = f"{' ' * leading_spaces}inactive-gradient " \
                f"from=\"{inactive_gradient_from}\" " \
                f"to=\"{inactive_gradient_to}\" " \
                f"angle={inactive_gradient_angle} " \
                f"relative-to=\"{relative_to_inactive}\""
                
                # Strip leading/trailing whitespace and ensure only a single space between components
                modified_line = ' '.join(modified_line.lstrip().split())

                # Reapply the leading spaces
                modified_line = ' ' * leading_spaces + modified_line
                
                if not inactive_gradient_enabled:
                    modified_line = f"{' ' * leading_spaces}// {modified_line}"
                    
                modified_focus_ring_lines.append(modified_line)
            
            # If the line doesn't contain any of the focus-ring elements, just add it as is
            else:
                modified_focus_ring_lines.append(line)
        
        # Step 3: Rebuild the focus-ring section with the modified lines
        modified_focus_ring_section = '\n'.join(modified_focus_ring_lines)
        
        # Replace the original focus-ring section in the config content with the modified version
        new_config = config_content.replace(focus_ring_section, modified_focus_ring_section)
        
        # print(f"Final modified focus-ring:\n{modified_focus_ring_section}")  # Debugging line
        
        return new_config  # Return the modified config
    else:
        print("No match for focus ring section.")  # Debugging line
        return config_content  # If no match, return original content
    
# Save function to write the modified config to the file    
def save_config(new_focus_ring, theme_name, description):
    user_themes_dir = os.path.expanduser("~/.config/niri/user_themes/")
    os.makedirs(user_themes_dir, exist_ok=True)
    
    # Save only the modified focus-ring properties in the JSON file
    theme_data = {
        "focus-ring": new_focus_ring,
        "description": description
    }
    
    theme_file = os.path.join(user_themes_dir, f"{theme_name}.json")
    with open(theme_file, 'w') as json_file:
        json.dump(theme_data, json_file, indent=4)

# Step 4: Write the modifications back to config.kdl
def save_to_config_kdl(new_config):
    config_file = os.path.expanduser("~/.config/niri/config.kdl")
    with open(config_file, 'w') as file:
        file.write(new_config)

# Function to open the color chooser dialog in a separate thread
def choose_color_in_thread(color_var, label):
    color = colorchooser.askcolor()[1]  # Open the color chooser dialog
    if color:
        color_var.set(color) 
        label.config(bg=color)

# Function to create the GUI
def create_gui(config_content):
    # Define the root window
    root = tk.Tk()
    root.title("Focus Ring Configuration")
    
    # Set window size and styling options
    root.geometry("600x600")
    root.option_add("*Font", "JetBrains 10")
    root.configure(bg="#f4f4f4")

    # Define default values
    default_width = 0
    default_active_color = "#000000"
    default_inactive_color = "#000000"
    default_active_relative_to = "workspace-view"
    default_inactive_relative_to = "workspace-view"
    default_description = "My custom theme"
    default_active_gradient_from = "#000000"
    default_active_gradient_to = "#000000"
    default_active_gradient_angle = 45
    default_inactive_gradient_from = "#000000"
    default_inactive_gradient_to = "#000000"
    default_inactive_gradient_angle = 45

    # Function to update color display
    def update_color_display(color_var, label):
        color = color_var.get()
        label.config(bg=color)  # Update the background color of the label

    
    # Step 5: Submit and save configuration
    def submit_configuration():
        width = width_var.get()
        active_color = active_color_var.get()
        inactive_color = inactive_color_var.get()
        #description = description_var.get()

        # Get the states of the gradient checkboxes
        active_gradient_enabled = active_gradient_checkbox_var.get()
        inactive_gradient_enabled = inactive_gradient_checkbox_var.get()
        active_color_enabled = active_color_checkbox_var.get()
        inactive_color_enabled = inactive_color_checkbox_var.get()
        
        # Get the values for the gradient colors and angles
        active_gradient_from = active_gradient_from_var.get()
        active_gradient_to = active_gradient_to_var.get()
        active_gradient_angle = active_gradient_angle_var.get()
        active_relative_to = relative_to_active_var.get()
        inactive_gradient_from = inactive_gradient_from_var.get()
        inactive_gradient_to = inactive_gradient_to_var.get()
        inactive_gradient_angle = inactive_gradient_angle_var.get()
        inactive_relative_to = relative_to_inactive_var.get()

        # Modify the config and save it
        new_config = modify_focus_ring(
            config_content, 
            width, 
            active_color, 
            inactive_color,
            active_relative_to,
            inactive_relative_to,
            active_gradient_from, 
            active_gradient_to, 
            active_gradient_angle, 
            inactive_gradient_from, 
            inactive_gradient_to, 
            inactive_gradient_angle,
            active_color_enabled,
            inactive_color_enabled,            
            active_gradient_enabled, 
            inactive_gradient_enabled
        )
        
        #theme_name = theme_name_var.get()

        #save_config(new_config, theme_name, description)
        save_to_config_kdl(new_config)

        root.quit()  # Close the GUI after saving

    # Widgets for the Theme Name and Description with alignment to the left
    #theme_name_label = tk.Label(root, text="Theme Name:")
    #theme_name_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)  # Align to the left
    #theme_name_var = tk.StringVar(value="test_theme")
    #theme_name_entry = tk.Entry(root, textvariable=theme_name_var)
    #theme_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")  # Align to the left
    #description_label = tk.Label(root, text="Description:")
    #description_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)  # Align to the left
    #description_var = tk.StringVar(value=default_description)
    #description_entry = tk.Entry(root, textvariable=description_var)
    #description_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")  # Align to the left#

    # Focus Ring Section with improved padding and styling
    focus_ring_frame = tk.LabelFrame(root, text="Focus Ring", padx=15, pady=15)
    focus_ring_frame.grid(row=2, columnspan=2, padx=10, pady=10, sticky="w")
    width_label = tk.Label(focus_ring_frame, text="Width:")
    width_label.grid(row=0, column=0, sticky="e", padx=10, pady=5)
    width_var = tk.IntVar(value=default_width)
    width_spinbox = tk.Spinbox(focus_ring_frame, from_=1, to=10, textvariable=width_var, width=5)  # Set width to 5 characters
    width_spinbox.grid(row=0, column=1, padx=10, pady=5)

    # Row 2: Active Color
    active_color_label = tk.Label(focus_ring_frame, text="Active Color:")
    active_color_label.grid(row=1, column=0, sticky="e", padx=10, pady=5)
    active_color_var = tk.StringVar(value=default_active_color)
    active_color_button = tk.Button(focus_ring_frame, text="Pick Color", command=lambda: threading.Thread(target=choose_color_in_thread, args=(active_color_var, active_color_display)).start())
    active_color_button.grid(row=1, column=1, padx=10, pady=5)
    active_color_display = tk.Label(focus_ring_frame, bg=active_color_var.get(), width=10)
    active_color_display.grid(row=1, column=2, padx=5, pady=5)
    active_color_checkbox_var = tk.BooleanVar(value=True)  # Default enabled state
    active_color_checkbox = tk.Checkbutton(focus_ring_frame, text="Enable", variable=active_color_checkbox_var)
    active_color_checkbox.grid(row=1, column=3, sticky="w", padx=10, pady=5)

    # Row 3: Inactive Color
    inactive_color_label = tk.Label(focus_ring_frame, text="Inactive Color:")
    inactive_color_label.grid(row=2, column=0, sticky="e", padx=10, pady=5)
    inactive_color_var = tk.StringVar(value=default_inactive_color)
    inactive_color_button = tk.Button(focus_ring_frame, text="Pick Color", command=lambda: threading.Thread(target=choose_color_in_thread, args=(inactive_color_var, inactive_color_display)).start())
    inactive_color_button.grid(row=2, column=1, padx=10, pady=5)
    inactive_color_display = tk.Label(focus_ring_frame, bg=inactive_color_var.get(), width=10)
    inactive_color_display.grid(row=2, column=2, padx=5, pady=5)
    inactive_color_checkbox_var = tk.BooleanVar(value=True)  # Default enabled state
    inactive_color_checkbox = tk.Checkbutton(focus_ring_frame, text="Enable", variable=inactive_color_checkbox_var)
    inactive_color_checkbox.grid(row=2, column=3, sticky="w", padx=10, pady=5)

    # Row 4: Active Gradient (Relative To field added before Enable)
    active_gradient_from_label = tk.Label(focus_ring_frame, text="Active Gradient: From Color:")
    active_gradient_from_label.grid(row=3, column=0, sticky="e", padx=10, pady=5)
    active_gradient_from_var = tk.StringVar(value=default_active_gradient_from)
    active_gradient_from_button = tk.Button(focus_ring_frame, text="Pick Color", command=lambda: threading.Thread(target=choose_color_in_thread, args=(active_gradient_from_var, active_gradient_from_display)).start())
    active_gradient_from_button.grid(row=3, column=1, padx=10, pady=5)
    active_gradient_from_display = tk.Label(focus_ring_frame, bg=active_gradient_from_var.get(), width=10)
    active_gradient_from_display.grid(row=3, column=2, padx=5, pady=5)
    active_gradient_to_label = tk.Label(focus_ring_frame, text="To Color:")
    active_gradient_to_label.grid(row=3, column=3, sticky="e", padx=10, pady=5)
    active_gradient_to_var = tk.StringVar(value=default_active_gradient_to)
    active_gradient_to_button = tk.Button(focus_ring_frame, text="Pick Color", command=lambda: threading.Thread(target=choose_color_in_thread, args=(active_gradient_to_var, active_gradient_to_display)).start())
    active_gradient_to_button.grid(row=3, column=4, padx=10, pady=5)
    active_gradient_to_display = tk.Label(focus_ring_frame, bg=active_gradient_to_var.get(), width=10)
    active_gradient_to_display.grid(row=3, column=5, padx=5, pady=5)
    active_gradient_angle_label = tk.Label(focus_ring_frame, text="Angle:")
    active_gradient_angle_label.grid(row=3, column=6, sticky="e", padx=10, pady=5)
    active_gradient_angle_var = tk.IntVar(value=default_active_gradient_angle)
    active_gradient_angle_entry = tk.Entry(focus_ring_frame, textvariable=active_gradient_angle_var, width=3)  # Set width to 3 characters
    active_gradient_angle_entry.grid(row=3, column=7, padx=10, pady=5)
    active_gradient_relative_to_label = tk.Label(focus_ring_frame, text="Active Gradient Relative To:")
    active_gradient_relative_to_label.grid(row=3, column=8, sticky="e", padx=10, pady=5)
    relative_to_active_var = tk.StringVar(value=default_active_relative_to)
    relative_to_active_entry = tk.Entry(focus_ring_frame, textvariable=relative_to_active_var)
    relative_to_active_entry.grid(row=3, column=9, padx=9, pady=5)    
    active_gradient_checkbox_var = tk.BooleanVar(value=True)  # Default enabled state
    active_gradient_checkbox = tk.Checkbutton(focus_ring_frame, text="Enable", variable=active_gradient_checkbox_var)
    active_gradient_checkbox.grid(row=3, column=10, sticky="w", padx=10, pady=5)

    # Row 5: Inactive Gradient (Similar to Active Gradient)
    inactive_gradient_from_label = tk.Label(focus_ring_frame, text="Inactive Gradient: From Color:")
    inactive_gradient_from_label.grid(row=4, column=0, sticky="e", padx=10, pady=5)
    inactive_gradient_from_var = tk.StringVar(value=default_inactive_gradient_from)
    inactive_gradient_from_button = tk.Button(focus_ring_frame, text="Pick Color", command=lambda: threading.Thread(target=choose_color_in_thread, args=(inactive_gradient_from_var, inactive_gradient_from_display)).start())
    inactive_gradient_from_button.grid(row=4, column=1, padx=10, pady=5)
    inactive_gradient_from_display = tk.Label(focus_ring_frame, text="Selected Color", bg=inactive_gradient_from_var.get(), width=10)
    inactive_gradient_from_display.grid(row=4, column=2, padx=5, pady=5)
    inactive_gradient_to_label = tk.Label(focus_ring_frame, text="To Color:")
    inactive_gradient_to_label.grid(row=4, column=3, sticky="e", padx=10, pady=5)
    inactive_gradient_to_var = tk.StringVar(value=default_inactive_gradient_to)
    inactive_gradient_to_button = tk.Button(focus_ring_frame, text="Pick Color", command=lambda: threading.Thread(target=choose_color_in_thread, args=(inactive_gradient_to_var, inactive_gradient_to_display)).start())
    inactive_gradient_to_button.grid(row=4, column=4, padx=10, pady=5)
    inactive_gradient_to_display = tk.Label(focus_ring_frame, text="Selected Color", bg=inactive_gradient_to_var.get(), width=10)
    inactive_gradient_to_display.grid(row=4, column=5, padx=5, pady=5)
    inactive_gradient_angle_label = tk.Label(focus_ring_frame, text="Angle:")
    inactive_gradient_angle_label.grid(row=4, column=6, sticky="e", padx=10, pady=5)
    inactive_gradient_angle_var = tk.IntVar(value=default_inactive_gradient_angle)
    inactive_gradient_angle_entry = tk.Entry(focus_ring_frame, textvariable=inactive_gradient_angle_var, width=3)  # Set width to 3 characters
    inactive_gradient_angle_entry.grid(row=4, column=7, padx=10, pady=5)
    inactive_gradient_relative_to_label = tk.Label(focus_ring_frame, text="Inactive Gradient Relative To:")
    inactive_gradient_relative_to_label.grid(row=4, column=8, sticky="e", padx=10, pady=5)
    relative_to_inactive_var = tk.StringVar(value=default_inactive_relative_to)
    relative_to_inactive_entry = tk.Entry(focus_ring_frame, textvariable=relative_to_inactive_var)
    relative_to_inactive_entry.grid(row=4, column=9, padx=10, pady=5)
    inactive_gradient_checkbox_var = tk.BooleanVar(value=True)  # Default enabled state
    inactive_gradient_checkbox = tk.Checkbutton(focus_ring_frame, text="Enable", variable=inactive_gradient_checkbox_var)
    inactive_gradient_checkbox.grid(row=4, column=10, sticky="w", padx=10, pady=5)

    submit_button = tk.Button(root, text="Save Theme", command=submit_configuration)
    submit_button.grid(row=5, columnspan=2, pady=15)

    # Run the GUI
    root.mainloop()

# Main function to run the app
def main():
    config_file = os.path.expanduser("~/.config/niri/config.kdl")
    config_content = load_config(config_file)
    create_gui(config_content)

if __name__ == "__main__":
    main()
