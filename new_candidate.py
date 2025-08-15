import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, Listbox
import datetime
import re
from common import get_db_connection, center_window

# ==================================================================
# NEW CANDIDATE MODULE
# ==================================================================
# This class defines the "New Candidate Entry" window. It is a data entry form
# designed for speed and accuracy, with features like data validation,
# automatic formatting, and cascading dropdowns to enforce data integrity.
class NewCandidateApp(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.withdraw()
        self.title("New Candidate Entry")
        self.geometry("600x900")
        self.transient(parent)
        self.grab_set()
        self.job_details_map = {}
        self.classes_map = {}
        self.interviewers_map = {}
        self.is_spanish_only_var = tk.BooleanVar()
        self.create_widgets()
        self.load_initial_data()
        center_window(self, parent)

    def load_initial_data(self):
        """Fetches initial data from the database to populate the dropdowns and listbox."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT department FROM Jobs ORDER BY department;")
            self.department_combobox['values'] = [row[0] for row in cursor.fetchall()]
            cursor.execute("SELECT strftime('%Y-%m-%d', class_date), class_id FROM Hiring_Classes ORDER BY class_date DESC;")
            self.classes_map = {row[0]: row[1] for row in cursor.fetchall()}
            self.class_combobox['values'] = list(self.classes_map.keys())
            cursor.execute("SELECT interviewer_name, interviewer_id FROM Interviewers ORDER BY interviewer_name;")
            self.interviewers_map = {row[0]: row[1] for row in cursor.fetchall()}
            self.interviewer_listbox.delete(0, tk.END)
            for name in self.interviewers_map.keys():
                self.interviewer_listbox.insert(tk.END, name)
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load initial data: {e}", parent=self)

    def on_department_select(self, event):
        """Event handler for when a department is selected. It populates the job details dropdown."""
        selected_dept = self.department_combobox.get()
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

    def format_phone_on_focus_out(self, event):
        """Automatically formats the phone number field when the user clicks away."""
        widget = event.widget
        digits = re.sub(r'\D', '', widget.get())
        if len(digits) > 10:
            digits = digits[:10]
        if digits:
            if len(digits) > 6:
                formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            elif len(digits) > 3:
                formatted = f"({digits[:3]}) {digits[3:]}"
            else:
                formatted = f"({digits[:3]}"
        else:
            formatted = ""
        widget.delete(0, tk.END)
        widget.insert(0, formatted)

    def format_date_on_focus_out(self, event):
        """Automatically formats date fields to YYYY-MM-DD when the user clicks away."""
        widget = event.widget
        date_str = widget.get().strip()
        if not date_str:
            return
        formats_to_try = ['%m/%d/%Y', '%m-%d-%Y', '%m.%d.%Y', '%m/%d/%y', '%m-%d-%y', '%m.%d.%y']
        parsed_date = None
        for fmt in formats_to_try:
            try:
                parsed_date = datetime.datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        if parsed_date:
            widget.delete(0, tk.END)
            widget.insert(0, parsed_date.strftime('%Y-%m-%d'))
        elif not re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            messagebox.showwarning("Invalid Date", f"Could not understand date: '{date_str}'.\nPlease use a format like MM/DD/YYYY.", parent=self)

    def create_widgets(self):
        """Builds the entire user interface for the module."""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(main_frame, text="* Indicates a mandatory field", foreground="red").grid(row=0, column=1, sticky=tk.W, pady=(0, 10))
        fields = {"First Name:": True, "Last Name:": True, "Phone Number:": False, "COC#:": False, "Interview Date:": False, "Original Hire Date:": False, "Original Term Date:": False, "Referred By:": False, "Notes:": False}
        self.entries = {}
        for i, (field, is_mandatory) in enumerate(fields.items(), start=1):
            label = ttk.Label(main_frame, text=f"*{field}" if is_mandatory else field)
            label.grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(main_frame, width=40)
            if field == "Phone Number:":
                entry.bind("<FocusOut>", self.format_phone_on_focus_out)
            elif "Date" in field:
                entry.bind("<FocusOut>", self.format_date_on_focus_out)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=5)
            self.entries[field] = entry
        current_row = len(fields) + 1
        ttk.Label(main_frame, text="Department:").grid(row=current_row, column=0, sticky=tk.W, pady=5)
        self.department_combobox = ttk.Combobox(main_frame, state="readonly")
        self.department_combobox.grid(row=current_row, column=1, sticky=tk.EW, pady=5)
        self.department_combobox.bind("<<ComboboxSelected>>", self.on_department_select)
        current_row += 1
        ttk.Label(main_frame, text="Job Details:").grid(row=current_row, column=0, sticky=tk.W, pady=5)
        self.job_detail_combobox = ttk.Combobox(main_frame, state="disabled")
        self.job_detail_combobox.grid(row=current_row, column=1, sticky=tk.EW, pady=5)
        current_row += 1
        ttk.Label(main_frame, text="Hiring Class:").grid(row=current_row, column=0, sticky=tk.W, pady=5)
        self.class_combobox = ttk.Combobox(main_frame, state="readonly")
        self.class_combobox.grid(row=current_row, column=1, sticky=tk.EW, pady=5)
        current_row += 1
        ttk.Checkbutton(main_frame, text="Spanish Only Speaker", variable=self.is_spanish_only_var).grid(row=current_row, column=1, sticky=tk.W, pady=5)
        current_row += 1
        ttk.Label(main_frame, text="Interviewers (Ctrl+Click):").grid(row=current_row, column=0, sticky=tk.W, pady=5)
        self.interviewer_listbox = Listbox(main_frame, selectmode=tk.MULTIPLE, exportselection=False, height=5)
        self.interviewer_listbox.grid(row=current_row, column=1, sticky=tk.EW, pady=5)
        current_row += 1
        ttk.Button(main_frame, text="Save New Candidate", command=self.save_candidate).grid(row=current_row, column=0, columnspan=2, pady=20)
        current_row += 1
        ttk.Button(main_frame, text="Clear Form", command=self.clear_form).grid(row=current_row, column=0, columnspan=2, pady=5)

    def save_candidate(self):
        """Validates form data and saves the new candidate to the database."""
        first_name = self.entries["First Name:"].get().strip()
        last_name = self.entries["Last Name:"].get().strip()
        if not first_name or not last_name:
            messagebox.showerror("Validation Error", "First Name and Last Name are required.", parent=self)
            return
        fk_job_id = self.job_details_map.get(self.job_detail_combobox.get())
        fk_class_id = self.classes_map.get(self.class_combobox.get())
        selected_interviewer_ids = [self.interviewers_map.get(self.interviewer_listbox.get(i)) for i in self.interviewer_listbox.curselection()]
        sql = """INSERT INTO Candidates (first_name, last_name, phone_number, coc_number, interview_date, rehire_date, original_term_date, referred_by, notes, fk_job_id, fk_class_id, is_spanish_only, candidate_status, bg_ds_clear, pre_board_complete, myinfo_ready, orientation_letter_sent) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', 0, 0, 0, 0);"""
        data = (first_name, last_name, self.entries["Phone Number:"].get().strip(), self.entries["COC#:"].get().strip(), self.entries["Interview Date:"].get().strip() or None, self.entries["Original Hire Date:"].get().strip() or None, self.entries["Original Term Date:"].get().strip() or None, self.entries["Referred By:"].get().strip(), self.entries["Notes:"].get().strip(), fk_job_id, fk_class_id, self.is_spanish_only_var.get())
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql, data)
            new_candidate_id = cursor.lastrowid
            if selected_interviewer_ids:
                links = [(new_candidate_id, i_id) for i_id in selected_interviewer_ids if i_id]
                cursor.executemany("INSERT INTO Candidate_Interviewers (fk_candidate_id, fk_interviewer_id) VALUES (?, ?);", links)
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Successfully saved candidate: {first_name} {last_name}", parent=self)
            self.clear_form()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save candidate: {e}", parent=self)

    def clear_form(self):
        """Resets all fields on the form to their default state."""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.department_combobox.set('')
        self.job_detail_combobox.set('')
        self.job_detail_combobox['state'] = 'disabled'
        self.class_combobox.set('')
        self.interviewer_listbox.selection_clear(0, tk.END)
        self.is_spanish_only_var.set(False)
