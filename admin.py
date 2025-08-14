import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, Listbox
import datetime
from common import get_db_connection, center_window

class AdminApp(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent); self.withdraw(); self.title("HR System Administration"); self.geometry("1100x600")
        self.transient(parent); self.grab_set()
        self.create_tabs()
        self.refresh_all_tabs()
        center_window(self, parent)
        
    def create_tabs(self):
        notebook = ttk.Notebook(self); notebook.pack(pady=10, padx=10, fill="both", expand=True)
        jobs_frame = ttk.Frame(notebook, padding="10"); interviewers_frame = ttk.Frame(notebook, padding="10"); classes_frame = ttk.Frame(notebook, padding="10")
        notebook.add(jobs_frame, text='Manage Jobs'); notebook.add(interviewers_frame, text='Manage Interviewers'); notebook.add(classes_frame, text='Manage Hiring Classes')
        self.create_jobs_tab(jobs_frame); self.create_interviewers_tab(interviewers_frame); self.create_classes_tab(classes_frame)

    def refresh_all_tabs(self): self.load_jobs(); self.load_interviewers(); self.load_classes()

    def create_action_panel(self, parent, add_cmd, edit_cmd, delete_cmd):
        action_frame = ttk.LabelFrame(parent, text="Actions", padding="10"); action_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        ttk.Button(action_frame, text="Add New", command=add_cmd).pack(fill=tk.X, pady=5)
        ttk.Button(action_frame, text="Edit Selected", command=edit_cmd).pack(fill=tk.X, pady=5)
        ttk.Button(action_frame, text="Delete Selected", command=delete_cmd).pack(fill=tk.X, pady=5)

    def create_jobs_tab(self, parent_frame):
        display_frame = ttk.LabelFrame(parent_frame, text="Existing Jobs", padding="10"); display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cols = ('department', 'shift', 'pay', 'type'); self.jobs_tree = ttk.Treeview(display_frame, columns=cols, show='headings')
        for col in cols: self.jobs_tree.heading(col, text=col.replace('_', ' ').title())
        v_scroll = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.jobs_tree.yview); self.jobs_tree.configure(yscroll=v_scroll.set)
        h_scroll = ttk.Scrollbar(display_frame, orient=tk.HORIZONTAL, command=self.jobs_tree.xview); self.jobs_tree.configure(xscroll=h_scroll.set)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y); h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.jobs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.jobs_tree.bind("<Double-1>", self.open_edit_job_window)
        self.create_action_panel(parent_frame, self.open_add_job_window, self.open_edit_job_window, self.delete_job)

    def load_jobs(self):
        for item in self.jobs_tree.get_children(): self.jobs_tree.delete(item)
        try:
            conn = get_db_connection(); cursor = conn.cursor()
            cursor.execute("SELECT job_id, department, shift, pay_structure, employment_type FROM Jobs WHERE department IS NOT NULL AND department != '' ORDER BY department, shift")
            for row in cursor.fetchall(): self.jobs_tree.insert('', tk.END, iid=row[0], values=row[1:])
            conn.close()
        except sqlite3.Error as e: messagebox.showerror("DB Error", f"Failed to load jobs: {e}", parent=self)

    def open_add_job_window(self): AddJobWindow(self)
    def open_edit_job_window(self, event=None):
        selection = self.jobs_tree.selection()
        if not selection: 
            if event is None: messagebox.showwarning("Selection Error", "Please select a job to edit.", parent=self)
            return
        EditJobWindow(self, selection[0])

    def delete_job(self):
        selection = self.jobs_tree.selection()
        if not selection: messagebox.showwarning("Selection Error", "Please select a job to delete.", parent=self); return
        job_id = selection[0]
        conn = get_db_connection(); cursor = conn.cursor(); cursor.execute("SELECT COUNT(*) FROM Candidates WHERE fk_job_id = ?", (job_id,)); count = cursor.fetchone()[0]; conn.close()
        msg = f"Are you sure you want to delete the selected job?\n\nThis job is currently linked to {count} candidate(s)."
        if messagebox.askyesno("Confirm Deletion", msg, icon='warning', parent=self):
            try:
                conn = get_db_connection(); cursor = conn.cursor(); cursor.execute("DELETE FROM Jobs WHERE job_id = ?", (job_id,)); conn.commit(); conn.close()
                self.refresh_all_tabs()
            except sqlite3.Error as e: messagebox.showerror("DB Error", f"Failed to delete job: {e}", parent=self)

    def create_interviewers_tab(self, parent_frame):
        display_frame = ttk.LabelFrame(parent_frame, text="Existing Interviewers", padding="10"); display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.interviewers_listbox = Listbox(display_frame, height=15); self.interviewers_listbox.pack(fill=tk.BOTH, expand=True)
        self.interviewers_listbox.bind("<Double-1>", self.open_edit_interviewer_window)
        self.create_action_panel(parent_frame, self.open_add_interviewer_window, self.open_edit_interviewer_window, self.delete_interviewer)

    def load_interviewers(self):
        self.interviewers_listbox.delete(0, tk.END); self.interviewers_map = {}
        try:
            conn = get_db_connection(); cursor = conn.cursor()
            cursor.execute("SELECT interviewer_id, interviewer_name FROM Interviewers ORDER BY interviewer_name")
            for id, name in cursor.fetchall(): self.interviewers_listbox.insert(tk.END, name); self.interviewers_map[name] = id
            conn.close()
        except sqlite3.Error as e: messagebox.showerror("DB Error", f"Failed to load interviewers: {e}", parent=self)

    def open_add_interviewer_window(self): AddEditInterviewerWindow(self)
    def open_edit_interviewer_window(self, event=None):
        selection = self.interviewers_listbox.curselection()
        if not selection: 
            if event is None: messagebox.showwarning("Selection Error", "Please select an interviewer to edit.", parent=self)
            return
        name = self.interviewers_listbox.get(selection[0]); interviewer_id = self.interviewers_map.get(name)
        AddEditInterviewerWindow(self, interviewer_id, name)

    def delete_interviewer(self):
        selection = self.interviewers_listbox.curselection()
        if not selection: messagebox.showwarning("Selection Error", "Please select an interviewer to delete.", parent=self); return
        name = self.interviewers_listbox.get(selection[0]); interviewer_id = self.interviewers_map.get(name)
        conn = get_db_connection(); cursor = conn.cursor(); cursor.execute("SELECT COUNT(*) FROM Candidate_Interviewers WHERE fk_interviewer_id = ?", (interviewer_id,)); count = cursor.fetchone()[0]; conn.close()
        msg = f"Are you sure you want to delete '{name}'?\n\nThis person is linked to {count} candidate interview(s)."
        if messagebox.askyesno("Confirm Deletion", msg, icon='warning', parent=self):
            try:
                conn = get_db_connection(); cursor = conn.cursor(); cursor.execute("DELETE FROM Interviewers WHERE interviewer_id = ?", (interviewer_id,)); conn.commit(); conn.close()
                self.refresh_all_tabs()
            except sqlite3.Error as e: messagebox.showerror("DB Error", f"Failed to delete interviewer: {e}", parent=self)

    def create_classes_tab(self, parent_frame):
        display_frame = ttk.LabelFrame(parent_frame, text="Existing Class Dates", padding="10"); display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.classes_listbox = Listbox(display_frame, height=15); self.classes_listbox.pack(fill=tk.BOTH, expand=True)
        self.classes_listbox.bind("<Double-1>", self.open_edit_class_window)
        self.create_action_panel(parent_frame, self.open_add_class_window, self.open_edit_class_window, self.delete_class)

    def load_classes(self):
        self.classes_listbox.delete(0, tk.END); self.classes_map = {}
        try:
            conn = get_db_connection(); cursor = conn.cursor()
            cursor.execute("SELECT class_id, strftime('%Y-%m-%d', class_date) FROM Hiring_Classes ORDER BY class_date DESC")
            for id, date_str in cursor.fetchall(): self.classes_listbox.insert(tk.END, date_str); self.classes_map[date_str] = id
            conn.close()
        except sqlite3.Error as e: messagebox.showerror("DB Error", f"Failed to load classes: {e}", parent=self)
            
    def open_add_class_window(self): AddEditClassWindow(self)
    def open_edit_class_window(self, event=None):
        selection = self.classes_listbox.curselection()
        if not selection: 
            if event is None: messagebox.showwarning("Selection Error", "Please select a class to edit.", parent=self)
            return
        date_str = self.classes_listbox.get(selection[0]); class_id = self.classes_map.get(date_str)
        AddEditClassWindow(self, class_id, date_str)

    def delete_class(self):
        selection = self.classes_listbox.curselection()
        if not selection: messagebox.showwarning("Selection Error", "Please select a class to delete.", parent=self); return
        date_str = self.classes_listbox.get(selection[0]); class_id = self.classes_map.get(date_str)
        conn = get_db_connection(); cursor = conn.cursor(); cursor.execute("SELECT COUNT(*) FROM Candidates WHERE fk_class_id = ?", (class_id,)); count = cursor.fetchone()[0]; conn.close()
        msg = f"Are you sure you want to delete the class on '{date_str}'?\n\nThis class is linked to {count} candidate(s)."
        if messagebox.askyesno("Confirm Deletion", msg, icon='warning', parent=self):
            try:
                conn = get_db_connection(); cursor = conn.cursor(); cursor.execute("DELETE FROM Hiring_Classes WHERE class_id = ?", (class_id,)); conn.commit(); conn.close()
                self.refresh_all_tabs()
            except sqlite3.Error as e: messagebox.showerror("DB Error", f"Failed to delete class: {e}", parent=self)

class AddJobWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent); self.withdraw(); self.parent = parent; self.title("Add New Job"); self.geometry("400x350"); self.transient(parent); self.grab_set(); self.create_widgets(); center_window(self, parent)
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20"); main_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(main_frame, text="Department:").pack(anchor=tk.W); self.dept_entry = ttk.Entry(main_frame, width=40); self.dept_entry.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(main_frame, text="Shift:").pack(anchor=tk.W); self.shift_entry = ttk.Entry(main_frame, width=40); self.shift_entry.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(main_frame, text="Pay Structure:").pack(anchor=tk.W); self.pay_combo = ttk.Combobox(main_frame, values=['Hourly', 'Salary'], state="readonly"); self.pay_combo.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(main_frame, text="Employment Type:").pack(anchor=tk.W); self.type_combo = ttk.Combobox(main_frame, values=['Full-Time', 'Part-Time'], state="readonly"); self.type_combo.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(main_frame, text="Add Job", command=self.add_job).pack(pady=10)
    def add_job(self):
        dept = self.dept_entry.get().strip(); shift = self.shift_entry.get().strip(); pay = self.pay_combo.get(); emp_type = self.type_combo.get()
        if not all([dept, pay, emp_type]): messagebox.showwarning("Input Error", "Department, Pay Structure, and Employment Type are required.", parent=self); return
        try:
            conn = get_db_connection(); cursor = conn.cursor(); cursor.execute("INSERT INTO Jobs (department, shift, pay_structure, employment_type) VALUES (?, ?, ?, ?)", (dept, shift or None, pay, emp_type)); conn.commit(); conn.close()
            messagebox.showinfo("Success", "Job added successfully.", parent=self); self.parent.refresh_all_tabs(); self.destroy()
        except sqlite3.Error as e: messagebox.showerror("DB Error", f"Failed to add job: {e}", parent=self)

class EditJobWindow(tk.Toplevel):
    def __init__(self, parent, job_id):
        super().__init__(parent); self.withdraw(); self.parent = parent; self.job_id = job_id; self.title("Edit Job"); self.geometry("400x350"); self.transient(parent); self.grab_set(); self.create_widgets(); self.load_job_data(); center_window(self, parent)
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20"); main_frame.pack(fill=tk.BOTH, expand=True)
        self.dept_var = tk.StringVar(); self.shift_var = tk.StringVar(); self.pay_var = tk.StringVar(); self.type_var = tk.StringVar()
        ttk.Label(main_frame, text="Department:").pack(anchor=tk.W); ttk.Entry(main_frame, textvariable=self.dept_var, width=40).pack(fill=tk.X, pady=(0, 10))
        ttk.Label(main_frame, text="Shift:").pack(anchor=tk.W); ttk.Entry(main_frame, textvariable=self.shift_var, width=40).pack(fill=tk.X, pady=(0, 10))
        ttk.Label(main_frame, text="Pay Structure:").pack(anchor=tk.W); ttk.Combobox(main_frame, textvariable=self.pay_var, values=['Hourly', 'Salary'], state="readonly").pack(fill=tk.X, pady=(0, 10))
        ttk.Label(main_frame, text="Employment Type:").pack(anchor=tk.W); ttk.Combobox(main_frame, textvariable=self.type_var, values=['Full-Time', 'Part-Time'], state="readonly").pack(fill=tk.X, pady=(0, 10))
        ttk.Button(main_frame, text="Save Changes", command=self.save_changes).pack(pady=10)
    def load_job_data(self):
        try:
            conn = get_db_connection(); conn.row_factory = sqlite3.Row; cursor = conn.cursor(); cursor.execute("SELECT * FROM Jobs WHERE job_id = ?", (self.job_id,)); data = cursor.fetchone(); conn.close()
            if data: self.dept_var.set(data['department']); self.shift_var.set(data['shift'] or ''); self.pay_var.set(data['pay_structure']); self.type_var.set(data['employment_type'])
        except sqlite3.Error as e: messagebox.showerror("Load Error", f"Could not load job data: {e}", parent=self); self.destroy()
    def save_changes(self):
        dept = self.dept_var.get().strip(); shift = self.shift_var.get().strip(); pay = self.pay_var.get(); emp_type = self.type_var.get()
        if not all([dept, pay, emp_type]): messagebox.showwarning("Input Error", "Department, Pay Structure, and Employment Type are required.", parent=self); return
        try:
            conn = get_db_connection(); cursor = conn.cursor(); cursor.execute("UPDATE Jobs SET department = ?, shift = ?, pay_structure = ?, employment_type = ? WHERE job_id = ?", (dept, shift or None, pay, emp_type, self.job_id)); conn.commit(); conn.close()
            messagebox.showinfo("Success", "Job details updated successfully.", parent=self); self.parent.refresh_all_tabs(); self.destroy()
        except sqlite3.Error as e: messagebox.showerror("DB Error", f"Failed to update job: {e}", parent=self)

class AddEditInterviewerWindow(tk.Toplevel):
    def __init__(self, parent, interviewer_id=None, interviewer_name=""):
        super().__init__(parent); self.withdraw(); self.parent = parent; self.interviewer_id = interviewer_id; self.title("Edit Interviewer" if interviewer_id else "Add New Interviewer"); self.geometry("400x150"); self.transient(parent); self.grab_set()
        self.name_var = tk.StringVar(value=interviewer_name)
        main_frame = ttk.Frame(self, padding="20"); main_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(main_frame, text="Interviewer Name:").pack(anchor=tk.W); ttk.Entry(main_frame, textvariable=self.name_var, width=40).pack(fill=tk.X, pady=(0, 10))
        ttk.Button(main_frame, text="Save Changes", command=self.save).pack(); center_window(self, parent)
    def save(self):
        name = self.name_var.get().strip()
        if not name: messagebox.showwarning("Input Error", "Interviewer name cannot be empty.", parent=self); return
        try:
            conn = get_db_connection(); cursor = conn.cursor()
            if self.interviewer_id: cursor.execute("UPDATE Interviewers SET interviewer_name = ? WHERE interviewer_id = ?", (name, self.interviewer_id))
            else: cursor.execute("INSERT INTO Interviewers (interviewer_name) VALUES (?)", (name,))
            conn.commit(); conn.close(); self.parent.refresh_all_tabs(); self.destroy()
        except sqlite3.IntegrityError: messagebox.showerror("Input Error", f"An interviewer named '{name}' already exists.", parent=self)
        except sqlite3.Error as e: messagebox.showerror("DB Error", f"Failed to save interviewer: {e}", parent=self)

class AddEditClassWindow(tk.Toplevel):
    def __init__(self, parent, class_id=None, class_date=""):
        super().__init__(parent); self.withdraw(); self.parent = parent; self.class_id = class_id; self.title("Edit Class Date" if class_id else "Add New Class"); self.geometry("400x150"); self.transient(parent); self.grab_set()
        self.date_var = tk.StringVar(value=class_date)
        main_frame = ttk.Frame(self, padding="20"); main_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(main_frame, text="Class Date (YYYY-MM-DD):").pack(anchor=tk.W); ttk.Entry(main_frame, textvariable=self.date_var, width=40).pack(fill=tk.X, pady=(0, 10))
        ttk.Button(main_frame, text="Save Changes", command=self.save).pack(); center_window(self, parent)
    def save(self):
        date_str = self.date_var.get().strip()
        try: datetime.datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError: messagebox.showwarning("Input Error", "Invalid date format. Please use YYYY-MM-DD.", parent=self); return
        try:
            conn = get_db_connection(); cursor = conn.cursor()
            if self.class_id: cursor.execute("UPDATE Hiring_Classes SET class_date = ? WHERE class_id = ?", (date_str, self.class_id))
            else: cursor.execute("INSERT INTO Hiring_Classes (class_date) VALUES (?)", (date_str,))
            conn.commit(); conn.close(); self.parent.refresh_all_tabs(); self.destroy()
        except sqlite3.IntegrityError: messagebox.showerror("Input Error", f"The class date '{date_str}' already exists.", parent=self)
        except sqlite3.Error as e: messagebox.showerror("DB Error", f"Failed to save class date: {e}", parent=self)
