import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from common import get_db_connection, center_window

# ==================================================================
# SEARCH AND UPDATE MODULE
# ==================================================================
# This module provides the main interface for finding and managing existing candidates.
# It consists of a primary search window (SearchApp) and a pop-up form for editing (EditWindow).
class SearchApp(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.withdraw()
        self.title("Search and Update Candidates")
        self.geometry("950x600")
        self.transient(parent)
        self.grab_set()
        self.create_search_widgets()
        center_window(self, parent)

    def create_search_widgets(self):
        """Builds the entire user interface for the search module."""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- Search Bar ---
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=10)
        ttk.Label(search_frame, text="Search by Name, Phone, PN, or EUID:").pack(side=tk.LEFT, padx=(0, 10))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind("<Return>", self.search_candidates)
        ttk.Button(search_frame, text="Search", command=self.search_candidates).pack(side=tk.LEFT, padx=(10, 0))
        
        # --- Results Table ---
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        ttk.Label(results_frame, text="Search Results:").pack(anchor=tk.W)
        columns = ('last_name', 'first_name', 'phone_number', 'pn_number', 'euid')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.results_tree.heading(col, text=col.replace('_', ' ').title())
        v_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscroll=v_scroll.set)
        h_scroll = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(xscroll=h_scroll.set)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.results_tree.bind("<Double-1>", self.open_edit_window)
        
        # --- Action Buttons ---
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        ttk.Button(action_frame, text="Edit Selected", command=self.open_edit_window).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(action_frame, text="Delete Selected", command=self.delete_candidate).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(action_frame, text="Bulk Update Orientation Letter", command=self.bulk_update_orientation_letter).pack(side=tk.LEFT, expand=True, padx=5)

    def search_candidates(self, event=None):
        """Performs a database search based on the user's input and populates the results table."""
        search_term = self.search_var.get().strip()
        if not search_term:
            messagebox.showwarning("Search Error", "Please enter a search term.", parent=self)
            return
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "SELECT candidate_id, last_name, first_name, phone_number, pn_number, euid FROM Candidates WHERE first_name LIKE ? OR last_name LIKE ? OR pn_number LIKE ? OR euid LIKE ? OR phone_number LIKE ? ORDER BY last_name, first_name;"
            like_term = f"%{search_term}%"
            cursor.execute(query, (like_term, like_term, like_term, like_term, like_term))
            results = cursor.fetchall()
            conn.close()
            if not results:
                self.results_tree.insert('', tk.END, values=("No candidates found.", "", "", "", ""))
            else:
                for row in results:
                    self.results_tree.insert('', tk.END, iid=row[0], values=(row[1], row[2], (row[3] or 'N/A'), (row[4] or 'N/A'), (row[5] or 'N/A')))
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Search failed: {e}", parent=self)

    def get_selected_candidate_id(self):
        """Helper function to get the ID of the currently selected candidate in the results tree."""
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select a candidate from the list.", parent=self)
            return None
        return selection[0]

    def open_edit_window(self, event=None):
        """Opens the EditWindow for the selected candidate."""
        candidate_id = self.get_selected_candidate_id()
        if candidate_id:
            EditWindow(self, candidate_id)

    def delete_candidate(self):
        """Deletes the selected candidate and all related records after confirmation."""
        candidate_id = self.get_selected_candidate_id()
        if not candidate_id:
            return
        item_values = self.results_tree.item(candidate_id, 'values')
        candidate_name = f"{item_values[1]} {item_values[0]}"
        if messagebox.askyesno("Confirm Deletion", f"WARNING: This will permanently delete '{candidate_name}' and all related records (interviews) from the database.\n\nThis action CANNOT be undone.\n\nAre you absolutely sure you want to proceed?", icon='warning', parent=self):
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                # Because of "ON DELETE CASCADE", deleting the candidate will also delete their links in Candidate_Interviewers.
                cursor.execute("DELETE FROM Candidates WHERE candidate_id = ?;", (candidate_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"'{candidate_name}' has been permanently deleted.", parent=self)
                self.search_candidates()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to delete candidate: {e}", parent=self)

    def bulk_update_orientation_letter(self):
        """Updates the 'orientation_letter_sent' flag for all fully cleared candidates starting next week."""
        if not messagebox.askyesno("Confirm Bulk Update", "This will mark 'Orientation Letter Sent' for ALL fully cleared candidates starting next week.\n\nAre you sure you want to proceed?", parent=self):
            return
        sql = """UPDATE Candidates SET orientation_letter_sent = 1 WHERE candidate_id IN (SELECT c.candidate_id FROM Candidates c JOIN Hiring_Classes hc ON c.fk_class_id = hc.class_id WHERE hc.class_date BETWEEN date('now', 'weekday 1') AND date('now', 'weekday 1', '+6 days') AND c.bg_ds_clear = 1 AND c.pre_board_complete = 1 AND c.myinfo_ready = 1 AND c.pn_number IS NOT NULL AND c.pn_number != '' AND c.euid IS NOT NULL AND c.euid != '');"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            updated_count = cursor.rowcount
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"'Orientation Letter Sent' status was successfully updated for {updated_count} candidate(s).", parent=self)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Bulk update failed: {e}", parent=self)

# ==================================================================
# EDIT CANDIDATE WINDOW
# ==================================================================
# This class defines the pop-up window for editing the details of a single candidate.
class EditWindow(tk.Toplevel):
    def __init__(self, parent, candidate_id):
        super().__init__(parent)
        self.withdraw()
        self.candidate_id = candidate_id
        self.title("Edit Candidate Details")
        self.geometry("600x750")
        self.transient(parent)
        self.grab_set()
        
        # --- Tkinter Variable Setup ---
        # Each UI element that can change (like an entry box or checkbox) is linked to a variable.
        self.status_var = tk.StringVar()
        self.screen_status_var = tk.StringVar()
        self.reject_reason_var = tk.StringVar()
        self.bg_clear_var = tk.BooleanVar()
        self.preboard_var = tk.BooleanVar()
        self.myinfo_var = tk.BooleanVar()
        self.letter_sent_var = tk.BooleanVar()
        self.pn_var = tk.StringVar()
        self.euid_var = tk.StringVar()
        self.notes_var = tk.StringVar()
        self.class_var = tk.StringVar()
        self.classes_map = {}
        self.department_var = tk.StringVar()
        self.job_detail_var = tk.StringVar()
        self.job_details_map = {}
        
        self.create_edit_widgets()
        self.load_candidate_data()
        center_window(self, parent)

    def create_edit_widgets(self):
        """Builds the entire user interface for the edit form."""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.name_label = ttk.Label(main_frame, text="Editing Candidate: ", font=('Helvetica', 12, 'bold'))
        self.name_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        self.context_frame = ttk.Frame(main_frame)
        self.context_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        self.job_label = ttk.Label(self.context_frame, text="Job: ", foreground="gray")
        self.job_label.pack(anchor=tk.W)
        
        # --- Form Layout ---
        # The form is built using the .grid() layout manager for precise alignment.
        row_counter = 2
        ttk.Label(main_frame, text="Hiring Class:").grid(row=row_counter, column=0, sticky=tk.W, pady=5)
        self.class_combobox = ttk.Combobox(main_frame, textvariable=self.class_var, state="readonly")
        self.class_combobox.grid(row=row_counter, column=1, sticky=tk.EW, pady=5)
        row_counter += 1
        
        ttk.Label(main_frame, text="Department:").grid(row=row_counter, column=0, sticky=tk.W, pady=5)
        self.department_combobox = ttk.Combobox(main_frame, textvariable=self.department_var, state="readonly")
        self.department_combobox.grid(row=row_counter, column=1, sticky=tk.EW, pady=5)
        self.department_combobox.bind("<<ComboboxSelected>>", self.on_department_select)
        row_counter += 1
        
        ttk.Label(main_frame, text="Job Details:").grid(row=row_counter, column=0, sticky=tk.W, pady=5)
        self.job_detail_combobox = ttk.Combobox(main_frame, textvariable=self.job_detail_var, state="disabled")
        self.job_detail_combobox.grid(row=row_counter, column=1, sticky=tk.EW, pady=5)
        row_counter += 1

        ttk.Label(main_frame, text="Candidate Status:").grid(row=row_counter, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(main_frame, textvariable=self.status_var, values=['Pending', 'Hired', 'Rejected', 'On Hold'], state="readonly").grid(row=row_counter, column=1, sticky=tk.EW, pady=5)
        row_counter += 1
        ttk.Label(main_frame, text="Screening Status:").grid(row=row_counter, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(main_frame, textvariable=self.screen_status_var, values=['', 'BG', 'DS', 'elink', 'DS/BG']).grid(row=row_counter, column=1, sticky=tk.EW, pady=5)
        row_counter += 1
        ttk.Label(main_frame, text="Rejection Reason:").grid(row=row_counter, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(main_frame, textvariable=self.reject_reason_var, values=['', 'DS', 'BG', 'NCNS', 'elink', 'Other']).grid(row=row_counter, column=1, sticky=tk.EW, pady=5)
        row_counter += 1
        ttk.Label(main_frame, text="PN Number:").grid(row=row_counter, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.pn_var).grid(row=row_counter, column=1, sticky=tk.EW, pady=5)
        row_counter += 1
        ttk.Label(main_frame, text="EUID:").grid(row=row_counter, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.euid_var).grid(row=row_counter, column=1, sticky=tk.EW, pady=5)
        row_counter += 1
        check_frame = ttk.Frame(main_frame)
        check_frame.grid(row=row_counter, column=1, sticky=tk.W, pady=10)
        ttk.Checkbutton(check_frame, text="BG/DS Clear", variable=self.bg_clear_var).pack(anchor=tk.W)
        ttk.Checkbutton(check_frame, text="Pre-Board Complete", variable=self.preboard_var).pack(anchor=tk.W)
        ttk.Checkbutton(check_frame, text="MyInfo Ready", variable=self.myinfo_var).pack(anchor=tk.W)
        ttk.Checkbutton(check_frame, text="Orientation Letter Sent", variable=self.letter_sent_var).pack(anchor=tk.W)
        row_counter += 1
        ttk.Label(main_frame, text="Notes:").grid(row=row_counter, column=0, sticky=tk.NW, pady=5)
        ttk.Entry(main_frame, textvariable=self.notes_var).grid(row=row_counter, column=1, sticky=tk.EW, pady=5)
        row_counter += 1
        ttk.Button(main_frame, text="Save Changes", command=self.save_changes).grid(row=row_counter, column=0, columnspan=2, pady=20)

    def on_department_select(self, event):
        """Event handler for the department dropdown to enable cascading functionality."""
        selected_dept = self.department_var.get()
        self.job_detail_combobox.set('')
        self.job_detail_combobox['state'] = 'readonly'
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "SELECT shift, employment_type, pay_structure, job_id FROM Jobs WHERE department = ? ORDER BY shift;"
            cursor.execute(query, (selected_dept,))
            job_details_data = cursor.fetchall()
            conn.close()
            self.job_details_map = {f"{row[0] or 'N/A'} | {row[1]} | {row[2]}": row[3] for row in job_details_data}
            self.job_detail_combobox['values'] = list(self.job_details_map.keys())
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load job details: {e}", parent=self)

    def load_candidate_data(self):
        """Fetches all data for the selected candidate and populates the form fields."""
        try:
            conn = get_db_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT department FROM Jobs ORDER BY department;")
            self.department_combobox['values'] = [row['department'] for row in cursor.fetchall()]
            cursor.execute("SELECT strftime('%Y-%m-%d', class_date), class_id FROM Hiring_Classes ORDER BY class_date DESC;")
            self.classes_map = {date_str: class_id for date_str, class_id in cursor.fetchall()}
            self.class_combobox['values'] = list(self.classes_map.keys())
            
            query = "SELECT c.*, j.department, j.shift, j.employment_type, j.pay_structure, hc.class_date FROM Candidates c LEFT JOIN Jobs j ON c.fk_job_id = j.job_id LEFT JOIN Hiring_Classes hc ON c.fk_class_id = hc.class_id WHERE c.candidate_id = ?;"
            cursor.execute(query, (self.candidate_id,))
            data = cursor.fetchone()
            conn.close()
            
            if data:
                self.name_label.config(text=f"Editing Candidate: {data['first_name']} {data['last_name']}")
                self.job_label.config(text=f"Current Job: {data['department'] or 'N/A'} | {data['shift'] or 'N/A'}")
                
                if data['department']:
                    self.department_var.set(data['department'])
                    self.on_department_select(None)
                    current_job_text = f"{data['shift'] or 'N/A'} | {data['employment_type']} | {data['pay_structure']}"
                    self.job_detail_var.set(current_job_text)

                if data['class_date']:
                    self.class_var.set(data['class_date'])
                self.status_var.set(data['candidate_status'] or '')
                self.screen_status_var.set(data['screening_status'] or '')
                self.reject_reason_var.set(data['rejection_reason'] or '')
                self.bg_clear_var.set(bool(data['bg_ds_clear']))
                self.preboard_var.set(bool(data['pre_board_complete']))
                self.myinfo_var.set(bool(data['myinfo_ready']))
                self.letter_sent_var.set(bool(data['orientation_letter_sent']))
                self.pn_var.set(data['pn_number'] or '')
                self.euid_var.set(data['euid'] or '')
                self.notes_var.set(data['notes'] or '')
        except sqlite3.Error as e:
            messagebox.showerror("Load Error", f"Could not load candidate data: {e}", parent=self)
            self.destroy()

    def save_changes(self):
        """Gathers all data from the form and saves it to the database using an UPDATE query."""
        new_fk_class_id = self.classes_map.get(self.class_var.get())
        new_fk_job_id = self.job_details_map.get(self.job_detail_var.get())
        sql = "UPDATE Candidates SET candidate_status = ?, screening_status = ?, rejection_reason = ?, bg_ds_clear = ?, pre_board_complete = ?, myinfo_ready = ?, orientation_letter_sent = ?, pn_number = ?, euid = ?, notes = ?, fk_class_id = ?, fk_job_id = ? WHERE candidate_id = ?;"
        data = (
            self.status_var.get(), self.screen_status_var.get(), self.reject_reason_var.get(), 
            self.bg_clear_var.get(), self.preboard_var.get(), self.myinfo_var.get(), 
            self.letter_sent_var.get(), self.pn_var.get().strip() or None, 
            self.euid_var.get().strip() or None, self.notes_var.get().strip(), 
            new_fk_class_id, new_fk_job_id, self.candidate_id
        )
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Candidate details updated successfully.", parent=self)
            # This is a key part of the interaction: it tells the parent SearchApp to refresh its results.
            if hasattr(self.master, 'search_candidates'):
                self.master.search_candidates()
            self.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Save Error", f"Could not save changes: {e}", parent=self)
