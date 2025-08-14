import sqlite3
import os
import tkinter as tk # Imported to provide type hints and access to Tkinter constants/methods if needed.  # noqa: F401

# --- Version 2.0.1 ---

# --- Configuration ---
# Get the absolute path of the directory where this script is located
script_dir = os.path.dirname(os.path.realpath(__file__))
# Join the script directory with the database filename
DB_PATH = os.path.join(script_dir, 'HR_Hiring_DB.db')

# --- Helper function for database connection ---
def get_db_connection():
    """Establishes a database connection and enables foreign key support."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# --- Helper function for centering windows ---
def center_window(win, parent=None):
    """Centers a tkinter window on the primary screen or over its parent."""
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    
    if parent:
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
    else:
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

    win.geometry(f'{width}x{height}+{x}+{y}')
    win.deiconify()
