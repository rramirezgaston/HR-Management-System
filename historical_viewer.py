import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from common import get_db_connection, center_window
from search_update import EditWindow

# ==================================================================
# HISTORICAL VIEWER MODULE
# ==================================================================
# This class defines the "Class Roster Viewer" window. Its purpose is to provide
# a detailed view of the candidates assigned to a specific hiring class date.
# It has two modes: a "Future View" (acting as a to-do list) and a "Past View"
# (acting as a historical record).
class HistoricalViewerApp(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.withdraw()
        self.title("Class Roster Viewer and Editor")
        self.geometry("1100x700")
        self.transient(parent)
        self.grab_set()
        self.classes_map = {}
        self.create_widgets()
        self.load_hiring_classes()
        center_window(self, parent)

    def create_widgets(self):
        """Builds the entire user interface for the module."""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        selection_frame = ttk.Frame(main_frame)
        selection_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(selection_frame, text="Select a Hiring Class Date:").pack(side=tk.LEFT, padx=(0, 10))
        self.class_combobox = ttk.Combobox(selection_frame, state="readonly", width=30)
        self.class_combobox.pack(side=tk.LEFT, padx=5)
        ttk.Button(selection_frame, text="View Class Roster", command=self.view_class_roster).pack(side=tk.LEFT, padx=10)
        ttk.Button(selection_frame, text="Edit Selected Candidate", command=self.open_edit_window).pack(side=tk.LEFT, padx=10)
        
        # A PanedWindow is a widget that allows the user to resize the two sections.
        paned_window = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        self.started_frame = ttk.LabelFrame(paned_window, text="Started Candidates / Cleared to Start", padding="10")
        paned_window.add(self.started_frame, weight=1)
        self.started_tree = self.create_results_tree(self.started_frame)
        
        self.not_started_frame = ttk.LabelFrame(paned_window, text="Did Not Start / Action Required", padding="10")
        paned_window.add(self.not_started_frame, weight=1)
        self.not_started_tree = self.create_results_tree(self.not_started_frame)
        
        self.started_tree.bind("<Double-1>", self.open_edit_window)
        self.not_started_tree.bind("<Double-1>", self.open_edit_window)

    def create_results_tree(self, parent_frame):
        """Reusable helper function to create a styled Treeview for displaying results."""
        tree_frame = ttk.Frame(parent_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        columns = ('last_name', 'first_name', 'department', 'shift', 'status', 'notes')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=8)
        for col in columns:
            tree.heading(col, text=col.replace('_', ' ').title())
        tree.column('last_name', width=150, anchor=tk.W)
        tree.column('first_name', width=150, anchor=tk.W)
        tree.column('department', width=150, anchor=tk.W)
        tree.column('shift', width=100, anchor=tk.W)
        tree.column('status', width=200, anchor=tk.W)
        tree.column('notes', width=300, anchor=tk.W)
        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=v_scroll.set)
        h_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(xscroll=h_scroll.set)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        return tree
        
    def load_hiring_classes(self):
        """Fetches all hiring class dates to populate the dropdown menu."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT strftime('%Y-%m-%d', class_date), class_id FROM Hiring_Classes ORDER BY class_date DESC;")
            self.classes_map = {date_str: class_id for date_str, class_id in cursor.fetchall()}
            conn.close()
            self.class_combobox['values'] = list(self.classes_map.keys())
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load hiring classes: {e}", parent=self)

    def clear_trees(self):
        """Clears all existing data from both result tables."""
        for item in self.started_tree.get_children():
            self.started_tree.delete(item)
        for item in self.not_started_tree.get_children():
            self.not_started_tree.delete(item)

    def view_class_roster(self):
        """Main logic function. Fetches and sorts candidates for a selected date."""
        selected_date = self.class_combobox.get()
        if not selected_date:
            messagebox.showwarning("Selection Error", "Please select a hiring class date.", parent=self)
            return
        class_id = self.classes_map.get(selected_date)
        self.clear_trees()
        
        # Determines if the selected date is in the future or past to adjust the UI.
        is_future_view = selected_date >= datetime.datetime.now().strftime('%Y-%m-%d')
        
        try:
            conn = get_db_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = "SELECT c.candidate_id, c.first_name, c.last_name, c.candidate_status, c.rejection_reason, c.notes, c.bg_ds_clear, c.pre_board_complete, c.myinfo_ready, c.pn_number, c.euid, j.department, j.shift FROM Candidates c LEFT JOIN Jobs j ON c.fk_job_id = j.job_id WHERE c.fk_class_id = ? ORDER BY c.last_name, c.first_name;"
            cursor.execute(query, (class_id,))
            all_candidates = cursor.fetchall()
            conn.close()
            
            if not all_candidates:
                messagebox.showinfo("No Data", "No candidates found for the selected class date.", parent=self)
                return

            # Dynamically change the labels and column headers based on the view mode.
            if is_future_view:
                self.started_frame.config(text="Cleared to Start")
                self.not_started_frame.config(text="Action Required")
                self.not_started_tree.heading('status', text='Missing Items')
            else:
                self.started_frame.config(text="Started Candidates")
                self.not_started_frame.config(text="Did Not Start / Rejected Candidates")
                self.not_started_tree.heading('status', text='Final Status / Rejection Reason')

            # Sort candidates into the appropriate table based on their status and the view mode.
            for candidate in all_candidates:
                base_values = (candidate['last_name'], candidate['first_name'], candidate['department'] or 'N/A', candidate['shift'] or 'N/A')
                notes = candidate['notes'] or ''
                candidate_id = candidate['candidate_id']
                if is_future_view:
                    is_cleared = (candidate['bg_ds_clear'] and candidate['pre_board_complete'] and candidate['myinfo_ready'] and candidate['pn_number'] and candidate['euid'])
                    if is_cleared:
                        self.started_tree.insert('', tk.END, iid=candidate_id, values=(*base_values, "Cleared", notes))
                    else:
                        missing_items = []
                        if not candidate['bg_ds_clear']: missing_items.append("BG/DS Clear")  # noqa: E701
                        if not candidate['pre_board_complete']: missing_items.append("Pre-Board")  # noqa: E701
                        if not candidate['myinfo_ready']: missing_items.append("MyInfo Ready")  # noqa: E701
                        if not candidate['pn_number'] or not candidate['euid']: missing_items.append("PN/EUID")  # noqa: E701
                        self.not_started_tree.insert('', tk.END, iid=candidate_id, values=(*base_values, ", ".join(missing_items), notes))
                else:
                    if candidate['candidate_status'] == 'Hired':
                        self.started_tree.insert('', tk.END, iid=candidate_id, values=(*base_values, "Hired", notes))
                    else:
                        self.not_started_tree.insert('', tk.END, iid=candidate_id, values=(*base_values, candidate['rejection_reason'] or candidate['candidate_status'], notes))
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch roster: {e}", parent=self)

    def open_edit_window(self, event=None):
        """Opens the EditWindow for the candidate selected in either of the two tables."""
        selected_id = None
        focused_tree = self.focus_get()
        if focused_tree == self.started_tree and self.started_tree.selection():
            selected_id = self.started_tree.selection()[0]
        elif focused_tree == self.not_started_tree and self.not_started_tree.selection():
            selected_id = self.not_started_tree.selection()[0]
        
        if selected_id:
            EditWindow(self, selected_id)
        elif event is None:
            messagebox.showwarning("Selection Error", "Please select a candidate from one of the lists to edit.", parent=self)
