import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, Listbox
from tkcalendar import DateEntry
import datetime
import re
import os
import webbrowser

# --- Version 1.1.4 ---

# --- Configuration ---
# Get the absolute path of the directory where the script is located
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

# ==================================================================
# MAIN APPLICATION HUB
# ==================================================================
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title("HR Management System")
        self.geometry("500x620") # Increased height for new button
        
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        
        BG_COLOR = '#cedbeb'
        PRIMARY_BLUE = '#084999'
        SECONDARY_BLUE = '#396dad'
        LIGHT_BLUE = '#6b92c2'
        BUTTON_TEXT_COLOR = 'white'
        FONT_FAMILY = "Segoe UI"

        self.configure(bg=BG_COLOR)
        
        self.style.configure('TFrame', background=BG_COLOR)
        self.style.configure('TLabel', font=(FONT_FAMILY, 10), background=BG_COLOR, foreground=PRIMARY_BLUE)
        self.style.configure('Header.TLabel', font=(FONT_FAMILY, 18, 'bold'), background=BG_COLOR, foreground=PRIMARY_BLUE)
        self.style.configure('TButton', font=(FONT_FAMILY, 10, 'bold'), padding=12, background=PRIMARY_BLUE, foreground=BUTTON_TEXT_COLOR, borderwidth=0)
        self.style.map('TButton', background=[('active', SECONDARY_BLUE)], relief=[('pressed', 'sunken')])
        self.style.configure('TLabelframe', background=BG_COLOR, bordercolor=LIGHT_BLUE, relief='groove')
        self.style.configure('TLabelframe.Label', background=BG_COLOR, foreground=PRIMARY_BLUE, font=(FONT_FAMILY, 11, 'bold'))
        self.style.configure('Card.TFrame', background='white', relief='raised', borderwidth=1)

        main_frame = ttk.Frame(self, padding="40")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="HR Management System", style='Header.TLabel').pack(pady=(0, 25))

        ttk.Button(main_frame, text="New Candidate Entry", command=self.open_new_candidate_window).pack(fill=tk.X, pady=6)
        ttk.Button(main_frame, text="Search & Update Candidates", command=self.open_search_window).pack(fill=tk.X, pady=6)
        ttk.Button(main_frame, text="View Class Rosters", command=self.open_historical_viewer_window).pack(fill=tk.X, pady=6)
        ttk.Button(main_frame, text="HR Dashboard", command=self.open_dashboard_window).pack(fill=tk.X, pady=6)
        ttk.Button(main_frame, text="Applicant Tracker", command=self.open_applicant_tracker_window).pack(fill=tk.X, pady=6)
        ttk.Button(main_frame, text="Run Reports", command=self.open_reports_window).pack(fill=tk.X, pady=6)
        ttk.Button(main_frame, text="System Administration", command=self.open_admin_window).pack(fill=tk.X, pady=6)
        ttk.Button(main_frame, text="Generate Weekly Email Report", command=self.generate_weekly_report).pack(fill=tk.X, pady=6)
        
        center_window(self)

    def open_window(self, window_class):
        try:
            win = window_class(self)
        except Exception as e:
            messagebox.showerror("Application Error", f"Could not open window: {e}")

    def open_new_candidate_window(self): self.open_window(NewCandidateApp)
    def open_search_window(self): self.open_window(SearchApp)
    def open_historical_viewer_window(self): self.open_window(HistoricalViewerApp)
    def open_dashboard_window(self): self.open_window(DashboardApp)
    def open_admin_window(self): self.open_window(AdminApp)
    def open_reports_window(self): self.open_window(ReportsApp)
    def open_applicant_tracker_window(self): self.open_window(ApplicantTrackerApp)
    
    def generate_weekly_report(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            selector_query = "SELECT COUNT(*) FROM V_Cleared_Hires_Next_Week WHERE Department IN ('Perishables', 'Grocery', 'Freezer');"
            cursor.execute(selector_query)
            new_selectors_count = cursor.fetchone()[0]
            cursor.execute("SELECT * FROM V_Cleared_Hires_Next_Week;")
            rows = cursor.fetchall()
            headers = [description[0] for description in cursor.description]
            conn.close()
            display_headers, display_rows = headers, rows
            if 'Lang' in headers:
                lang_column_index = headers.index('Lang')
                if not any(row[lang_column_index] == 'S' for row in rows):
                    display_headers = [h for h in headers if h != 'Lang']
                    display_rows = [tuple(cell for i, cell in enumerate(row) if i != lang_column_index) for row in rows]
            today = datetime.date.today()
            next_monday = today + datetime.timedelta(days=-today.weekday(), weeks=1)
            report_date_str = next_monday.strftime('%B %d, %Y')
            html_content = f"""
            <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Weekly New Hire Report</title>
            <style>
              body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #333; }} .container {{ padding: 20px; }}
              table {{ border-collapse: collapse; width: auto; margin-top: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
              th, td {{ border: 1px solid #dddddd; text-align: left; padding: 12px; white-space: nowrap; }}
              thead th {{ background-color: #004a99; color: white; font-weight: bold; }} tbody tr:nth-child(even) {{ background-color: #f2f7fc; }}
              tbody tr:hover {{ background-color: #e6f0fa; }} p {{ font-size: 1.1em; margin-bottom: 1em; }}
            </style></head><body><div class="container">
            <p>Happy Friday,</p><p>This coming week, we will be having the following ({new_selectors_count}) New Selectors.</p>
            """
            if not display_rows: html_content += "<p style='font-style: italic; color: #555;'>No new hires are fully cleared to start for the upcoming week.</p>"
            else:
                html_content += "<hr style='margin-top: 20px; margin-bottom: 20px; border: 0; border-top: 1px solid #ddd;'>"
                html_content += "<table><thead><tr>"
                for header in display_headers: html_content += f"<th>{header}</th>"
                html_content += "</tr></thead><tbody>"
                for row in display_rows:
                    html_content += "<tr>"
                    for cell in row: html_content += f"<td>{str(cell).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}</td>"
                    html_content += "</tr>"
                html_content += "</tbody></table>"
            html_content += "</div></body></html>"
            output_filename = 'weekly_report.html'
            with open(output_filename, 'w', encoding='utf-8') as file: file.write(html_content)
            full_path = os.path.abspath(output_filename)
            webbrowser.open_new_tab(f"file://{full_path}")
            messagebox.showinfo("Success", f"Report generated successfully and opened in your browser!\n\nSaved as: {full_path}")
        except sqlite3.Error as e: messagebox.showerror("Database Error", f"Failed to generate report: {e}\n\nPlease ensure the 'V_Cleared_Hires_Next_Week' VIEW exists.")
        except Exception as e: messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)

# ==================================================================
# MODULE 1: NEW CANDIDATE ENTRY
# ==================================================================
class NewCandidateApp(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.withdraw()
        self.title("New Candidate Entry")
        self.geometry("600x900")
        self.transient(parent)
        self.grab_set()
        self.job_details_map = {}; self.classes_map = {}; self.interviewers_map = {}; self.is_spanish_only_var = tk.BooleanVar()
        self.create_widgets()
        self.load_initial_data()
        center_window(self, parent)

    def load_initial_data(self):
        try:
            conn = get_db_connection(); cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT department FROM Jobs ORDER BY department;"); self.department_combobox['values'] = [row[0] for row in cursor.fetchall()]
            cursor.execute("SELECT strftime('%Y-%m-%d', class_date), class_id FROM Hiring_Classes ORDER BY class_date DESC;"); self.classes_map = {row[0]: row[1] for row in cursor.fetchall()}; self.class_combobox['values'] = list(self.classes_map.keys())
            cursor.execute("SELECT interviewer_name, interviewer_id FROM Interviewers ORDER BY interviewer_name;"); self.interviewers_map = {row[0]: row[1] for row in cursor.fetchall()}
            self.interviewer_listbox.delete(0, tk.END)
            for name in self.interviewers_map.keys(): self.interviewer_listbox.insert(tk.END, name)
            conn.close()
        except Exception as e: messagebox.showerror("Database Error", f"Failed to load initial data: {e}", parent=self)

    def on_department_select(self, event):
        selected_dept = self.department_combobox.get()
        self.job_detail_combobox.set(''); self.job_detail_combobox['state'] = 'readonly'
        try:
            conn = get_db_connection(); cursor = conn.cursor()
            query = "SELECT shift, employment_type, pay_structure, job_id FROM Jobs WHERE department = ? ORDER BY shift;"
            cursor.execute(query, (selected_dept,)); job_details_data = cursor.fetchall(); conn.close()
            self.job_details_map = {f"{row[0] or 'N/A'} | {row[1]} | {row[2]}": row[3] for row in job_details_data}
            self.job_detail_combobox['values'] = list(self.job_details_map.keys())
        except Exception as e: messagebox.showerror("Database Error", f"Failed to load job details: {e}", parent=self)

    def format_phone_on_focus_out(self, event):
        widget = event.widget; digits = re.sub(r'\D', '', widget.get())
        if len(digits) > 10: digits = digits[:10]
        if digits:
            if len(digits) > 6: formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            elif len(digits) > 3: formatted = f"({digits[:3]}) {digits[3:]}"
            else: formatted = f"({digits[:3]}"
        else: formatted = ""
        widget.delete(0, tk.END); widget.insert(0, formatted)

    def format_date_on_focus_out(self, event):
        widget = event.widget; date_str = widget.get().strip()
        if not date_str: return
        formats_to_try = ['%m/%d/%Y', '%m-%d-%Y', '%m.%d.%Y', '%m/%d/%y', '%m-%d-%y', '%m.%d.%y']
        parsed_date = None
        for fmt in formats_to_try:
            try: parsed_date = datetime.datetime.strptime(date_str, fmt); break
            except ValueError: continue
        if parsed_date: widget.delete(0, tk.END); widget.insert(0, parsed_date.strftime('%Y-%m-%d'))
        elif not re.match(r'\d{4}-\d{2}-\d{2}', date_str): messagebox.showwarning("Invalid Date", f"Could not understand date: '{date_str}'.\nPlease use a format like MM/DD/YYYY.", parent=self)

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20"); main_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(main_frame, text="* Indicates a mandatory field", foreground="red").grid(row=0, column=1, sticky=tk.W, pady=(0, 10))
        fields = {"First Name:": True, "Last Name:": True, "Phone Number:": False, "COC#:": False, "Interview Date:": False, "Original Hire Date:": False, "Original Term Date:": False, "Referred By:": False, "Notes:": False}
        self.entries = {}
        for i, (field, is_mandatory) in enumerate(fields.items(), start=1):
            label = ttk.Label(main_frame, text=f"*{field}" if is_mandatory else field)
            label.grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(main_frame, width=40)
            if field == "Phone Number:": entry.bind("<FocusOut>", self.format_phone_on_focus_out)
            elif "Date" in field: entry.bind("<FocusOut>", self.format_date_on_focus_out)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=5)
            self.entries[field] = entry
        current_row = len(fields) + 1
        ttk.Label(main_frame, text="Department:").grid(row=current_row, column=0, sticky=tk.W, pady=5)
        self.department_combobox = ttk.Combobox(main_frame, state="readonly"); self.department_combobox.grid(row=current_row, column=1, sticky=tk.EW, pady=5)
        self.department_combobox.bind("<<ComboboxSelected>>", self.on_department_select); current_row += 1
        ttk.Label(main_frame, text="Job Details:").grid(row=current_row, column=0, sticky=tk.W, pady=5)
        self.job_detail_combobox = ttk.Combobox(main_frame, state="disabled"); self.job_detail_combobox.grid(row=current_row, column=1, sticky=tk.EW, pady=5); current_row += 1
        ttk.Label(main_frame, text="Hiring Class:").grid(row=current_row, column=0, sticky=tk.W, pady=5)
        self.class_combobox = ttk.Combobox(main_frame, state="readonly"); self.class_combobox.grid(row=current_row, column=1, sticky=tk.EW, pady=5); current_row += 1
        ttk.Checkbutton(main_frame, text="Spanish Only Speaker", variable=self.is_spanish_only_var).grid(row=current_row, column=1, sticky=tk.W, pady=5); current_row += 1
        ttk.Label(main_frame, text="Interviewers (Ctrl+Click):").grid(row=current_row, column=0, sticky=tk.W, pady=5)
        self.interviewer_listbox = Listbox(main_frame, selectmode=tk.MULTIPLE, exportselection=False, height=5); self.interviewer_listbox.grid(row=current_row, column=1, sticky=tk.EW, pady=5); current_row += 1
        ttk.Button(main_frame, text="Save New Candidate", command=self.save_candidate).grid(row=current_row, column=0, columnspan=2, pady=20); current_row += 1
        ttk.Button(main_frame, text="Clear Form", command=self.clear_form).grid(row=current_row, column=0, columnspan=2, pady=5)

    def save_candidate(self):
        first_name = self.entries["First Name:"].get().strip(); last_name = self.entries["Last Name:"].get().strip()
        if not first_name or not last_name: messagebox.showerror("Validation Error", "First Name and Last Name are required.", parent=self); return
        fk_job_id = self.job_details_map.get(self.job_detail_combobox.get())
        fk_class_id = self.classes_map.get(self.class_combobox.get())
        selected_interviewer_ids = [self.interviewers_map.get(self.interviewer_listbox.get(i)) for i in self.interviewer_listbox.curselection()]
        sql = """INSERT INTO Candidates (first_name, last_name, phone_number, coc_number, interview_date, rehire_date, original_term_date, referred_by, notes, fk_job_id, fk_class_id, is_spanish_only, candidate_status, bg_ds_clear, pre_board_complete, myinfo_ready, orientation_letter_sent) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', 0, 0, 0, 0);"""
        data = (first_name, last_name, self.entries["Phone Number:"].get().strip(), self.entries["COC#:"].get().strip(), self.entries["Interview Date:"].get().strip() or None, self.entries["Original Hire Date:"].get().strip() or None, self.entries["Original Term Date:"].get().strip() or None, self.entries["Referred By:"].get().strip(), self.entries["Notes:"].get().strip(), fk_job_id, fk_class_id, self.is_spanish_only_var.get())
        try:
            conn = get_db_connection(); cursor = conn.cursor(); cursor.execute(sql, data); new_candidate_id = cursor.lastrowid
            if selected_interviewer_ids:
                links = [(new_candidate_id, i_id) for i_id in selected_interviewer_ids if i_id]
                cursor.executemany("INSERT INTO Candidate_Interviewers (fk_candidate_id, fk_interviewer_id) VALUES (?, ?);", links)
            conn.commit(); conn.close()
            messagebox.showinfo("Success", f"Successfully saved candidate: {first_name} {last_name}", parent=self); self.clear_form()
        except sqlite3.Error as e: messagebox.showerror("Database Error", f"Failed to save candidate: {e}", parent=self)

    def clear_form(self):
        for entry in self.entries.values(): entry.delete(0, tk.END)
        self.department_combobox.set(''); self.job_detail_combobox.set(''); self.job_detail_combobox['state'] = 'disabled'
        self.class_combobox.set(''); self.interviewer_listbox.selection_clear(0, tk.END); self.is_spanish_only_var.set(False)

# ==================================================================
# MODULE 2: SEARCH AND UPDATE
# ==================================================================
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
        main_frame = ttk.Frame(self, padding="20"); main_frame.pack(fill=tk.BOTH, expand=True)
        search_frame = ttk.Frame(main_frame); search_frame.pack(fill=tk.X, pady=10)
        ttk.Label(search_frame, text="Search by Name, Phone, PN, or EUID:").pack(side=tk.LEFT, padx=(0, 10))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40); self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind("<Return>", self.search_candidates)
        ttk.Button(search_frame, text="Search", command=self.search_candidates).pack(side=tk.LEFT, padx=(10, 0))
        results_frame = ttk.Frame(main_frame); results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        ttk.Label(results_frame, text="Search Results:").pack(anchor=tk.W)
        columns = ('last_name', 'first_name', 'phone_number', 'pn_number', 'euid')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        for col in columns: self.results_tree.heading(col, text=col.replace('_', ' ').title())
        v_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview); self.results_tree.configure(yscroll=v_scroll.set)
        h_scroll = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview); self.results_tree.configure(xscroll=h_scroll.set)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y); h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.results_tree.bind("<Double-1>", self.open_edit_window)
        action_frame = ttk.Frame(main_frame); action_frame.pack(fill=tk.X, pady=10)
        ttk.Button(action_frame, text="Edit Selected", command=self.open_edit_window).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(action_frame, text="Delete Selected", command=self.delete_candidate).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(action_frame, text="Bulk Update Orientation Letter", command=self.bulk_update_orientation_letter).pack(side=tk.LEFT, expand=True, padx=5)

    def search_candidates(self, event=None):
        search_term = self.search_var.get().strip()
        if not search_term: messagebox.showwarning("Search Error", "Please enter a search term.", parent=self); return
        for item in self.results_tree.get_children(): self.results_tree.delete(item)
        try:
            conn = get_db_connection(); cursor = conn.cursor()
            query = "SELECT candidate_id, last_name, first_name, phone_number, pn_number, euid FROM Candidates WHERE first_name LIKE ? OR last_name LIKE ? OR pn_number LIKE ? OR euid LIKE ? OR phone_number LIKE ? ORDER BY last_name, first_name;"
            like_term = f"%{search_term}%"
            cursor.execute(query, (like_term, like_term, like_term, like_term, like_term)); results = cursor.fetchall(); conn.close()
            if not results: self.results_tree.insert('', tk.END, values=("No candidates found.", "", "", "", ""))
            else:
                for row in results: self.results_tree.insert('', tk.END, iid=row[0], values=(row[1], row[2], (row[3] or 'N/A'), (row[4] or 'N/A'), (row[5] or 'N/A')))
        except sqlite3.Error as e: messagebox.showerror("Database Error", f"Search failed: {e}", parent=self)

    def get_selected_candidate_id(self):
        selection = self.results_tree.selection()
        if not selection: messagebox.showwarning("Selection Error", "Please select a candidate from the list.", parent=self); return None
        return selection[0]

    def open_edit_window(self, event=None):
        candidate_id = self.get_selected_candidate_id()
        if candidate_id: EditWindow(self, candidate_id)

    def delete_candidate(self):
        candidate_id = self.get_selected_candidate_id()
        if not candidate_id: return
        item_values = self.results_tree.item(candidate_id, 'values'); candidate_name = f"{item_values[1]} {item_values[0]}"
        if messagebox.askyesno("Confirm Deletion", f"WARNING: This will permanently delete '{candidate_name}' and all related records (interviews) from the database.\n\nThis action CANNOT be undone.\n\nAre you absolutely sure you want to proceed?", icon='warning', parent=self):
            try:
                conn = get_db_connection(); cursor = conn.cursor()
                cursor.execute("DELETE FROM Candidate_Interviewers WHERE fk_candidate_id = ?;", (candidate_id,))
                cursor.execute("DELETE FROM Candidates WHERE candidate_id = ?;", (candidate_id,))
                conn.commit(); conn.close()
                messagebox.showinfo("Success", f"'{candidate_name}' has been permanently deleted.", parent=self)
                self.search_candidates()
            except sqlite3.Error as e: messagebox.showerror("Database Error", f"Failed to delete candidate: {e}", parent=self)

    def bulk_update_orientation_letter(self):
        if not messagebox.askyesno("Confirm Bulk Update", "This will mark 'Orientation Letter Sent' for ALL fully cleared candidates starting next week.\n\nAre you sure you want to proceed?", parent=self): return
        sql = """UPDATE Candidates SET orientation_letter_sent = 1 WHERE candidate_id IN (SELECT c.candidate_id FROM Candidates c JOIN Hiring_Classes hc ON c.fk_class_id = hc.class_id WHERE hc.class_date BETWEEN date('now', 'weekday 1') AND date('now', 'weekday 1', '+6 days') AND c.bg_ds_clear = 1 AND c.pre_board_complete = 1 AND c.myinfo_ready = 1 AND c.pn_number IS NOT NULL AND c.pn_number != '' AND c.euid IS NOT NULL AND c.euid != '');"""
        try:
            conn = get_db_connection(); cursor = conn.cursor(); cursor.execute(sql); updated_count = cursor.rowcount; conn.commit(); conn.close()
            messagebox.showinfo("Success", f"'Orientation Letter Sent' status was successfully updated for {updated_count} candidate(s).", parent=self)
        except sqlite3.Error as e: messagebox.showerror("Database Error", f"Bulk update failed: {e}", parent=self)

class EditWindow(tk.Toplevel):
    def __init__(self, parent, candidate_id):
        super().__init__(parent)
        self.withdraw(); self.candidate_id = candidate_id; self.title("Edit Candidate Details"); self.geometry("600x750")
        self.transient(parent); self.grab_set()
        self.status_var = tk.StringVar(); self.screen_status_var = tk.StringVar(); self.reject_reason_var = tk.StringVar()
        self.bg_clear_var = tk.BooleanVar(); self.preboard_var = tk.BooleanVar(); self.myinfo_var = tk.BooleanVar()
        self.letter_sent_var = tk.BooleanVar(); self.pn_var = tk.StringVar(); self.euid_var = tk.StringVar()
        self.notes_var = tk.StringVar(); self.class_var = tk.StringVar()
        self.classes_map = {}
        self.department_var = tk.StringVar()
        self.job_detail_var = tk.StringVar()
        self.job_details_map = {}
        self.create_edit_widgets()
        self.load_candidate_data()
        center_window(self, parent)

    def create_edit_widgets(self):
        main_frame = ttk.Frame(self, padding="20"); main_frame.pack(fill=tk.BOTH, expand=True)
        self.name_label = ttk.Label(main_frame, text="Editing Candidate: ", font=('Helvetica', 12, 'bold')); self.name_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        self.context_frame = ttk.Frame(main_frame); self.context_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        self.job_label = ttk.Label(self.context_frame, text="Job: ", foreground="gray"); self.job_label.pack(anchor=tk.W)
        row_counter = 2
        ttk.Label(main_frame, text="Hiring Class:").grid(row=row_counter, column=0, sticky=tk.W, pady=5)
        self.class_combobox = ttk.Combobox(main_frame, textvariable=self.class_var, state="readonly"); self.class_combobox.grid(row=row_counter, column=1, sticky=tk.EW, pady=5); row_counter += 1
        
        ttk.Label(main_frame, text="Department:").grid(row=row_counter, column=0, sticky=tk.W, pady=5)
        self.department_combobox = ttk.Combobox(main_frame, textvariable=self.department_var, state="readonly"); self.department_combobox.grid(row=row_counter, column=1, sticky=tk.EW, pady=5)
        self.department_combobox.bind("<<ComboboxSelected>>", self.on_department_select); row_counter += 1
        
        ttk.Label(main_frame, text="Job Details:").grid(row=row_counter, column=0, sticky=tk.W, pady=5)
        self.job_detail_combobox = ttk.Combobox(main_frame, textvariable=self.job_detail_var, state="disabled"); self.job_detail_combobox.grid(row=row_counter, column=1, sticky=tk.EW, pady=5); row_counter += 1

        ttk.Label(main_frame, text="Candidate Status:").grid(row=row_counter, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(main_frame, textvariable=self.status_var, values=['Pending', 'Hired', 'Rejected', 'On Hold'], state="readonly").grid(row=row_counter, column=1, sticky=tk.EW, pady=5); row_counter += 1
        ttk.Label(main_frame, text="Screening Status:").grid(row=row_counter, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(main_frame, textvariable=self.screen_status_var, values=['', 'BG', 'DS', 'elink', 'DS/BG']).grid(row=row_counter, column=1, sticky=tk.EW, pady=5); row_counter += 1
        ttk.Label(main_frame, text="Rejection Reason:").grid(row=row_counter, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(main_frame, textvariable=self.reject_reason_var, values=['', 'DS', 'BG', 'NCNS', 'elink', 'Other']).grid(row=row_counter, column=1, sticky=tk.EW, pady=5); row_counter += 1
        ttk.Label(main_frame, text="PN Number:").grid(row=row_counter, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.pn_var).grid(row=row_counter, column=1, sticky=tk.EW, pady=5); row_counter += 1
        ttk.Label(main_frame, text="EUID:").grid(row=row_counter, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.euid_var).grid(row=row_counter, column=1, sticky=tk.EW, pady=5); row_counter += 1
        check_frame = ttk.Frame(main_frame); check_frame.grid(row=row_counter, column=1, sticky=tk.W, pady=10)
        ttk.Checkbutton(check_frame, text="BG/DS Clear", variable=self.bg_clear_var).pack(anchor=tk.W)
        ttk.Checkbutton(check_frame, text="Pre-Board Complete", variable=self.preboard_var).pack(anchor=tk.W)
        ttk.Checkbutton(check_frame, text="MyInfo Ready", variable=self.myinfo_var).pack(anchor=tk.W)
        ttk.Checkbutton(check_frame, text="Orientation Letter Sent", variable=self.letter_sent_var).pack(anchor=tk.W); row_counter += 1
        ttk.Label(main_frame, text="Notes:").grid(row=row_counter, column=0, sticky=tk.NW, pady=5)
        ttk.Entry(main_frame, textvariable=self.notes_var).grid(row=row_counter, column=1, sticky=tk.EW, pady=5); row_counter += 1
        ttk.Button(main_frame, text="Save Changes", command=self.save_changes).grid(row=row_counter, column=0, columnspan=2, pady=20)

    def on_department_select(self, event):
        selected_dept = self.department_var.get()
        self.job_detail_combobox.set(''); self.job_detail_combobox['state'] = 'readonly'
        try:
            conn = get_db_connection(); cursor = conn.cursor()
            query = "SELECT shift, employment_type, pay_structure, job_id FROM Jobs WHERE department = ? ORDER BY shift;"
            cursor.execute(query, (selected_dept,)); job_details_data = cursor.fetchall(); conn.close()
            self.job_details_map = {f"{row[0] or 'N/A'} | {row[1]} | {row[2]}": row[3] for row in job_details_data}
            self.job_detail_combobox['values'] = list(self.job_details_map.keys())
        except Exception as e: messagebox.showerror("Database Error", f"Failed to load job details: {e}", parent=self)

    def load_candidate_data(self):
        try:
            conn = get_db_connection(); conn.row_factory = sqlite3.Row; cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT department FROM Jobs ORDER BY department;"); self.department_combobox['values'] = [row['department'] for row in cursor.fetchall()]
            cursor.execute("SELECT strftime('%Y-%m-%d', class_date), class_id FROM Hiring_Classes ORDER BY class_date DESC;")
            self.classes_map = {date_str: class_id for date_str, class_id in cursor.fetchall()}; self.class_combobox['values'] = list(self.classes_map.keys())
            
            query = "SELECT c.*, j.department, j.shift, j.employment_type, j.pay_structure, hc.class_date FROM Candidates c LEFT JOIN Jobs j ON c.fk_job_id = j.job_id LEFT JOIN Hiring_Classes hc ON c.fk_class_id = hc.class_id WHERE c.candidate_id = ?;"
            cursor.execute(query, (self.candidate_id,)); data = cursor.fetchone(); conn.close()
            
            if data:
                self.name_label.config(text=f"Editing Candidate: {data['first_name']} {data['last_name']}")
                self.job_label.config(text=f"Current Job: {data['department'] or 'N/A'} | {data['shift'] or 'N/A'}")
                
                if data['department']:
                    self.department_var.set(data['department'])
                    self.on_department_select(None)
                    current_job_text = f"{data['shift'] or 'N/A'} | {data['employment_type']} | {data['pay_structure']}"
                    self.job_detail_var.set(current_job_text)

                if data['class_date']: self.class_var.set(data['class_date'])
                self.status_var.set(data['candidate_status'] or ''); self.screen_status_var.set(data['screening_status'] or ''); self.reject_reason_var.set(data['rejection_reason'] or '')
                self.bg_clear_var.set(bool(data['bg_ds_clear'])); self.preboard_var.set(bool(data['pre_board_complete'])); self.myinfo_var.set(bool(data['myinfo_ready'])); self.letter_sent_var.set(bool(data['orientation_letter_sent']))
                self.pn_var.set(data['pn_number'] or ''); self.euid_var.set(data['euid'] or ''); self.notes_var.set(data['notes'] or '')
        except sqlite3.Error as e: messagebox.showerror("Load Error", f"Could not load candidate data: {e}", parent=self); self.destroy()

    def save_changes(self):
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
            conn = get_db_connection(); cursor = conn.cursor(); cursor.execute(sql, data); conn.commit(); conn.close()
            messagebox.showinfo("Success", "Candidate details updated successfully.", parent=self)
            if hasattr(self.master, 'search_candidates'):
                self.master.search_candidates()
            self.destroy()
        except sqlite3.Error as e: messagebox.showerror("Save Error", f"Could not save changes: {e}", parent=self)

# ==================================================================
# HISTORICAL VIEWER WINDOW
# ==================================================================
class HistoricalViewerApp(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.withdraw(); self.title("Class Roster Viewer and Editor"); self.geometry("1100x700")
        self.transient(parent); self.grab_set()
        self.classes_map = {}
        self.create_widgets()
        self.load_hiring_classes()
        center_window(self, parent)

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20"); main_frame.pack(fill=tk.BOTH, expand=True)
        selection_frame = ttk.Frame(main_frame); selection_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(selection_frame, text="Select a Hiring Class Date:").pack(side=tk.LEFT, padx=(0, 10))
        self.class_combobox = ttk.Combobox(selection_frame, state="readonly", width=30); self.class_combobox.pack(side=tk.LEFT, padx=5)
        ttk.Button(selection_frame, text="View Class Roster", command=self.view_class_roster).pack(side=tk.LEFT, padx=10)
        ttk.Button(selection_frame, text="Edit Selected Candidate", command=self.open_edit_window).pack(side=tk.LEFT, padx=10)
        paned_window = ttk.PanedWindow(main_frame, orient=tk.VERTICAL); paned_window.pack(fill=tk.BOTH, expand=True)
        self.started_frame = ttk.LabelFrame(paned_window, text="Started Candidates / Cleared to Start", padding="10"); paned_window.add(self.started_frame, weight=1)
        self.started_tree = self.create_results_tree(self.started_frame)
        self.not_started_frame = ttk.LabelFrame(paned_window, text="Did Not Start / Action Required", padding="10"); paned_window.add(self.not_started_frame, weight=1)
        self.not_started_tree = self.create_results_tree(self.not_started_frame)
        self.started_tree.bind("<Double-1>", self.open_edit_window)
        self.not_started_tree.bind("<Double-1>", self.open_edit_window)

    def create_results_tree(self, parent_frame):
        tree_frame = ttk.Frame(parent_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        columns = ('last_name', 'first_name', 'department', 'shift', 'status', 'notes'); tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=8)
        for col in columns: tree.heading(col, text=col.replace('_', ' ').title())
        tree.column('last_name', width=150, anchor=tk.W); tree.column('first_name', width=150, anchor=tk.W); tree.column('department', width=150, anchor=tk.W)
        tree.column('shift', width=100, anchor=tk.W); tree.column('status', width=200, anchor=tk.W); tree.column('notes', width=300, anchor=tk.W)
        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview); tree.configure(yscroll=v_scroll.set)
        h_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview); tree.configure(xscroll=h_scroll.set)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        return tree
        
    def load_hiring_classes(self):
        try:
            conn = get_db_connection(); cursor = conn.cursor()
            cursor.execute("SELECT strftime('%Y-%m-%d', class_date), class_id FROM Hiring_Classes ORDER BY class_date DESC;")
            self.classes_map = {date_str: class_id for date_str, class_id in cursor.fetchall()}; conn.close()
            self.class_combobox['values'] = list(self.classes_map.keys())
        except sqlite3.Error as e: messagebox.showerror("Database Error", f"Failed to load hiring classes: {e}", parent=self)

    def clear_trees(self):
        for item in self.started_tree.get_children(): self.started_tree.delete(item)
        for item in self.not_started_tree.get_children(): self.not_started_tree.delete(item)

    def view_class_roster(self):
        selected_date = self.class_combobox.get()
        if not selected_date: messagebox.showwarning("Selection Error", "Please select a hiring class date.", parent=self); return
        class_id = self.classes_map.get(selected_date); self.clear_trees()
        is_future_view = selected_date >= datetime.datetime.now().strftime('%Y-%m-%d')
        try:
            conn = get_db_connection(); conn.row_factory = sqlite3.Row; cursor = conn.cursor()
            query = "SELECT c.candidate_id, c.first_name, c.last_name, c.candidate_status, c.rejection_reason, c.notes, c.bg_ds_clear, c.pre_board_complete, c.myinfo_ready, c.pn_number, c.euid, j.department, j.shift FROM Candidates c LEFT JOIN Jobs j ON c.fk_job_id = j.job_id WHERE c.fk_class_id = ? ORDER BY c.last_name, c.first_name;"
            cursor.execute(query, (class_id,)); all_candidates = cursor.fetchall(); conn.close()
            if not all_candidates: messagebox.showinfo("No Data", "No candidates found for the selected class date.", parent=self); return

            if is_future_view:
                self.started_frame.config(text="Cleared to Start"); self.not_started_frame.config(text="Action Required"); self.not_started_tree.heading('status', text='Missing Items')
            else:
                self.started_frame.config(text="Started Candidates"); self.not_started_frame.config(text="Did Not Start / Rejected Candidates"); self.not_started_tree.heading('status', text='Final Status / Rejection Reason')

            for candidate in all_candidates:
                base_values = (candidate['last_name'], candidate['first_name'], candidate['department'] or 'N/A', candidate['shift'] or 'N/A')
                notes = candidate['notes'] or ''; candidate_id = candidate['candidate_id']
                if is_future_view:
                    is_cleared = (candidate['bg_ds_clear'] and candidate['pre_board_complete'] and candidate['myinfo_ready'] and candidate['pn_number'] and candidate['euid'])
                    if is_cleared: self.started_tree.insert('', tk.END, iid=candidate_id, values=(*base_values, "Cleared", notes))
                    else:
                        missing_items = []
                        if not candidate['bg_ds_clear']: missing_items.append("BG/DS Clear")
                        if not candidate['pre_board_complete']: missing_items.append("Pre-Board")
                        if not candidate['myinfo_ready']: missing_items.append("MyInfo Ready")
                        if not candidate['pn_number'] or not candidate['euid']: missing_items.append("PN/EUID")
                        self.not_started_tree.insert('', tk.END, iid=candidate_id, values=(*base_values, ", ".join(missing_items), notes))
                else:
                    if candidate['candidate_status'] == 'Hired': self.started_tree.insert('', tk.END, iid=candidate_id, values=(*base_values, "Hired", notes))
                    else: self.not_started_tree.insert('', tk.END, iid=candidate_id, values=(*base_values, candidate['rejection_reason'] or candidate['candidate_status'], notes))
        except sqlite3.Error as e: messagebox.showerror("Database Error", f"Failed to fetch roster: {e}", parent=self)

    def open_edit_window(self, event=None):
        selected_id = None
        focused_tree = self.focus_get()
        if focused_tree == self.started_tree and self.started_tree.selection(): selected_id = self.started_tree.selection()[0]
        elif focused_tree == self.not_started_tree and self.not_started_tree.selection(): selected_id = self.not_started_tree.selection()[0]
        
        if selected_id: EditWindow(self, selected_id)
        elif event is None: messagebox.showwarning("Selection Error", "Please select a candidate from one of the lists to edit.", parent=self)

# ==================================================================
# DASHBOARD WINDOW
# ==================================================================
class DashboardApp(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.withdraw(); self.title("HR Dashboard"); self.geometry("1100x700")
        self.transient(parent); self.grab_set()
        self.create_widgets()
        self.refresh_dashboard()
        center_window(self, parent)

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20"); main_frame.pack(fill=tk.BOTH, expand=True)
        header_frame = ttk.Frame(main_frame); header_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header_frame, text="Hiring Pipeline Overview", font=('Helvetica', 16, 'bold')).pack(side=tk.LEFT)
        ttk.Button(header_frame, text="Refresh Dashboard", command=self.refresh_dashboard).pack(side=tk.RIGHT)
        kpi_frame = ttk.Frame(main_frame); kpi_frame.pack(fill=tk.X, pady=10)
        self.hires_this_month_kpi = self.create_kpi_box(kpi_frame, "Hiring Activity This Month", "0")
        self.pending_candidates_kpi = self.create_kpi_box(kpi_frame, "Total Pending Candidates", "0")
        self.cleared_next_week_kpi = self.create_kpi_box(kpi_frame, "Cleared for Next Week", "0")
        hotlist_frame = ttk.LabelFrame(main_frame, text="Action Required: Pending Candidates", padding="10"); hotlist_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        columns = ('last_name', 'first_name', 'class_date', 'screening_status', 'notes')
        self.pending_tree = ttk.Treeview(hotlist_frame, columns=columns, show='headings')
        for col in columns: self.pending_tree.heading(col, text=col.replace('_', ' ').title())
        for col, width in zip(columns, [150, 150, 120, 150, 300]): self.pending_tree.column(col, width=width, anchor=tk.W)
        v_scroll = ttk.Scrollbar(hotlist_frame, orient=tk.VERTICAL, command=self.pending_tree.yview); self.pending_tree.configure(yscroll=v_scroll.set)
        h_scroll = ttk.Scrollbar(hotlist_frame, orient=tk.HORIZONTAL, command=self.pending_tree.xview); self.pending_tree.configure(xscroll=h_scroll.set)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y); h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.pending_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.pending_tree.bind("<Double-1>", self.open_edit_window)
        
        button_container = ttk.Frame(hotlist_frame)
        button_container.pack(fill=tk.X, pady=(10,0))
        ttk.Button(button_container, text="Edit Selected Pending Candidate", command=self.open_edit_window).pack(anchor=tk.W)

    def create_kpi_box(self, parent, label_text, initial_value):
        kpi_box = ttk.Frame(parent, padding="10", style='Card.TFrame'); kpi_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        value_label = ttk.Label(kpi_box, text=initial_value, font=('Helvetica', 24, 'bold'), foreground="#084999", background='white'); value_label.pack()
        ttk.Label(kpi_box, text=label_text, font=('Helvetica', 10), background='white').pack()
        return value_label

    def refresh_dashboard(self):
        try:
            conn = get_db_connection(); cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Candidates WHERE candidate_status != 'Rejected' AND strftime('%Y-%m', interview_date) = strftime('%Y-%m', 'now');")
            self.hires_this_month_kpi.config(text=str(cursor.fetchone()[0]))
            cursor.execute("SELECT COUNT(*) FROM Candidates WHERE candidate_status = 'Pending';")
            self.pending_candidates_kpi.config(text=str(cursor.fetchone()[0]))
            cursor.execute("SELECT COUNT(*) FROM V_Cleared_Hires_Next_Week;")
            self.cleared_next_week_kpi.config(text=str(cursor.fetchone()[0]))
            for item in self.pending_tree.get_children(): self.pending_tree.delete(item)
            pending_query = "SELECT c.candidate_id, c.last_name, c.first_name, hc.class_date, c.screening_status, c.notes FROM Candidates c JOIN Hiring_Classes hc ON c.fk_class_id = hc.class_id WHERE c.candidate_status = 'Pending' AND hc.class_date >= date('now') ORDER BY hc.class_date, c.last_name;"
            cursor.execute(pending_query); pending_candidates = cursor.fetchall()
            if not pending_candidates: self.pending_tree.insert('', tk.END, values=("No pending candidates found.", "", "", "", ""))
            else:
                for row in pending_candidates: self.pending_tree.insert('', tk.END, iid=row[0], values=row[1:])
            conn.close()
        except sqlite3.Error as e: messagebox.showerror("Database Error", f"Failed to refresh dashboard: {e}", parent=self)

    def open_edit_window(self, event=None):
        selection = self.pending_tree.selection()
        if not selection:
            if event is None: messagebox.showwarning("Selection Error", "Please select a candidate to edit.", parent=self)
            return
        candidate_id = selection[0]
        EditWindow(self, candidate_id)

# ==================================================================
# ADMIN WINDOW
# ==================================================================
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

# ==================================================================
# APPLICANT TRACKER MODULE
# ==================================================================
class ApplicantTrackerApp(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.withdraw()
        self.title("Applicant Tracker")
        self.geometry("900x820")
        self.transient(parent)
        self.grab_set()

        # --- Style for smaller buttons ---
        self.style = ttk.Style(self)
        self.style.configure('Small.TButton', padding=(2, 2), font=("Segoe UI", 8))
        self.style.configure('Minus.Small.TButton', padding=(2, 2), font=("Segoe UI", 8), background='#aeb9c6')
        self.style.map('Minus.Small.TButton', background=[('active', '#c7d0d9')])

        # --- Define reasons for each category ---
        self.rejection_reasons_pre = ["Not eligible for Rehire", "Background", "Not a good Fit"]
        self.rejection_reasons_post = ["Not eligible for Rehire", "Background", "Not a good Fit", "NCNS"]
        self.withdrawal_reasons = ["Schedule", "Other Job Offer", "Pay", "Other"]
        
        self.metric_vars = {}
        self.breakdown_vars = {}
        self.previous_values = {}

        self.create_widgets()
        self.load_data_for_date()
        center_window(self, parent)

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Date Selection ---
        date_frame = ttk.Frame(main_frame)
        date_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(date_frame, text="Select Date:", font=("Segoe UI", 11, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        self.date_entry = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.pack(side=tk.LEFT)
        self.date_entry.bind("<<DateEntrySelected>>", self.load_data_for_date)

        # --- Main Metrics Frame ---
        metrics_frame = ttk.LabelFrame(main_frame, text="Daily Metrics", padding="15")
        metrics_frame.pack(fill=tk.X, pady=(0, 15))
        
        core_metrics = ["Apps Reviewed", "Interviews Scheduled", "Hires Confirmed"]
        for i, metric in enumerate(core_metrics):
            self.metric_vars[metric] = tk.StringVar(value='0')
            self.create_metric_row(metrics_frame, metric, self.metric_vars[metric], i)

        # --- Breakdowns Frame ---
        breakdowns_frame = ttk.LabelFrame(main_frame, text="Breakdowns", padding="15")
        breakdowns_frame.pack(fill=tk.BOTH, expand=True)

        rejection_frame = ttk.LabelFrame(breakdowns_frame, text="Rejections", padding="10")
        rejection_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(rejection_frame, text="Pre-Interview:", font=("Segoe UI", 10, 'bold')).pack(anchor='w', pady=(0,5))
        for reason in self.rejection_reasons_pre:
            key = f"pre_interview_rejection_{reason}"
            self.breakdown_vars[key] = tk.StringVar(value='0')
            self.create_metric_row(rejection_frame, reason, self.breakdown_vars[key])

        ttk.Separator(rejection_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(rejection_frame, text="Post-Interview:", font=("Segoe UI", 10, 'bold')).pack(anchor='w', pady=(0,5))
        for reason in self.rejection_reasons_post:
            key = f"post_interview_rejection_{reason}"
            self.breakdown_vars[key] = tk.StringVar(value='0')
            self.create_metric_row(rejection_frame, reason, self.breakdown_vars[key])

        withdrawal_frame = ttk.LabelFrame(breakdowns_frame, text="Withdrawals", padding="10")
        withdrawal_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(withdrawal_frame, text="Pre-Interview:", font=("Segoe UI", 10, 'bold')).pack(anchor='w', pady=(0,5))
        for reason in self.withdrawal_reasons:
            key = f"pre_interview_withdrawal_{reason}"
            self.breakdown_vars[key] = tk.StringVar(value='0')
            self.create_metric_row(withdrawal_frame, reason, self.breakdown_vars[key])
            
        ttk.Separator(withdrawal_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(withdrawal_frame, text="Post-Interview:", font=("Segoe UI", 10, 'bold')).pack(anchor='w', pady=(0,5))
        for reason in self.withdrawal_reasons:
            key = f"post_interview_withdrawal_{reason}"
            self.breakdown_vars[key] = tk.StringVar(value='0')
            self.create_metric_row(withdrawal_frame, reason, self.breakdown_vars[key])

        # --- Save Button ---
        ttk.Button(main_frame, text="Save Log for Selected Date", command=self.save_data).pack(pady=(20, 0))

    def _validate_and_revert(self, var, key):
        """Validates entry fields on focus out to ensure they are non-negative integers."""
        current_value = var.get()
        try:
            val = int(current_value)
            if val < 0:
                var.set(self.previous_values.get(key, '0'))
            else:
                self.previous_values[key] = str(val)
        except (ValueError, TypeError):
            var.set(self.previous_values.get(key, '0'))

    def create_metric_row(self, parent, label, var, row_num=None):
        frame = ttk.Frame(parent)
        key = label.replace(" ", "_") # Create a unique key for the dictionary
        self.previous_values[key] = var.get()

        if row_num is not None:
            frame.pack(fill=tk.X, pady=4, padx=5)
        else:
            frame.pack(fill=tk.X, pady=2, padx=5)
            
        ttk.Label(frame, text=label, width=25).pack(side=tk.LEFT)
        
        entry = ttk.Entry(frame, textvariable=var, width=8, justify='center')
        entry.bind("<FocusOut>", lambda event, v=var, k=key: self._validate_and_revert(v, k))
        entry.pack(side=tk.LEFT, padx=5)

        def decrement():
            try:
                current_val = int(var.get())
                if current_val > 0:
                    var.set(str(current_val - 1))
                    self.previous_values[key] = var.get()
            except ValueError:
                var.set(self.previous_values.get(key, '0'))

        def increment():
            try:
                current_val = int(var.get())
                var.set(str(current_val + 1))
                self.previous_values[key] = var.get()
            except ValueError:
                var.set(self.previous_values.get(key, '0'))

        ttk.Button(frame, text="-", style='Minus.Small.TButton', width=2, command=decrement).pack(side=tk.LEFT)
        ttk.Button(frame, text="+", style='Small.TButton', width=2, command=increment).pack(side=tk.LEFT)

    def load_data_for_date(self, event=None):
        selected_date = self.date_entry.get_date().strftime("%Y-%m-%d")
        
        for var in self.metric_vars.values(): var.set('0')
        for var in self.breakdown_vars.values(): var.set('0')

        try:
            conn = get_db_connection(); conn.row_factory = sqlite3.Row; cursor = conn.cursor()
            cursor.execute("SELECT * FROM Daily_Metrics WHERE metric_date = ?", (selected_date,))
            metric_data = cursor.fetchone()

            if metric_data:
                self.metric_vars["Apps Reviewed"].set(str(metric_data["apps_reviewed"]))
                self.metric_vars["Interviews Scheduled"].set(str(metric_data["interviews_scheduled"]))
                self.metric_vars["Hires Confirmed"].set(str(metric_data["hires_confirmed"]))

                cursor.execute("SELECT * FROM Daily_Breakdowns WHERE fk_metric_id = ?", (metric_data["metric_id"],))
                breakdown_data = cursor.fetchall()
                for row in breakdown_data:
                    key = f"{row['category']}_{row['reason']}"
                    if key in self.breakdown_vars:
                        self.breakdown_vars[key].set(str(row['count']))
            
            # Store initial values after loading
            for key, var in self.metric_vars.items(): self.previous_values[key.replace(" ", "_")] = var.get()
            for key, var in self.breakdown_vars.items(): self.previous_values[key] = var.get()

            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load data: {e}", parent=self)

    def save_data(self):
        selected_date = self.date_entry.get_date().strftime("%Y-%m-%d")
        
        # Final validation before saving
        for key, var in {**self.metric_vars, **self.breakdown_vars}.items():
            self._validate_and_revert(var, key.replace(" ", "_"))

        try:
            conn = get_db_connection(); cursor = conn.cursor()
            
            cursor.execute("SELECT metric_id FROM Daily_Metrics WHERE metric_date = ?", (selected_date,))
            result = cursor.fetchone()
            
            apps_reviewed = int(self.metric_vars["Apps Reviewed"].get())
            interviews_scheduled = int(self.metric_vars["Interviews Scheduled"].get())
            hires_confirmed = int(self.metric_vars["Hires Confirmed"].get())

            if result:
                metric_id = result[0]
                cursor.execute("UPDATE Daily_Metrics SET apps_reviewed = ?, interviews_scheduled = ?, hires_confirmed = ? WHERE metric_id = ?", 
                               (apps_reviewed, interviews_scheduled, hires_confirmed, metric_id))
            else:
                cursor.execute("INSERT INTO Daily_Metrics (metric_date, apps_reviewed, interviews_scheduled, hires_confirmed) VALUES (?, ?, ?, ?)", 
                               (selected_date, apps_reviewed, interviews_scheduled, hires_confirmed))
                metric_id = cursor.lastrowid

            cursor.execute("DELETE FROM Daily_Breakdowns WHERE fk_metric_id = ?", (metric_id,))

            breakdown_data = []
            for key, var in self.breakdown_vars.items():
                count = int(var.get())
                if count > 0:
                    parts = key.split('_')
                    category = f"{parts[0]}_{parts[1]}_{parts[2]}"
                    reason = " ".join(parts[3:])
                    breakdown_data.append((metric_id, category, reason, count))
            
            if breakdown_data:
                cursor.executemany("INSERT INTO Daily_Breakdowns (fk_metric_id, category, reason, count) VALUES (?, ?, ?, ?)", breakdown_data)

            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Data for {selected_date} saved successfully.", parent=self)
            self.load_data_for_date() # Reload to update previous_values
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save data: {e}", parent=self)


# ==================================================================
# MODULE 6: REPORTS
# ==================================================================
class ReportsApp(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.withdraw()
        self.title("Run Analytical Reports")
        self.geometry("900x600")
        self.transient(parent)
        self.grab_set()
        self.create_widgets()
        center_window(self, parent)

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20"); main_frame.pack(fill=tk.BOTH, expand=True)
        controls_frame = ttk.LabelFrame(main_frame, text="Report Options", padding="10"); controls_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(controls_frame, text="Select Report:").pack(side=tk.LEFT, padx=(0, 10))
        self.report_var = tk.StringVar()
        report_options = ["Weekly Activity Snapshot", "Referral Leaderboard", "Hires by Department", "Search by Referrer", "Last Week's Referrals", "Referrals by Class Week"]
        self.report_combo = ttk.Combobox(controls_frame, textvariable=self.report_var, values=report_options, state="readonly", width=30); self.report_combo.pack(side=tk.LEFT, padx=5)
        self.report_combo.bind("<<ComboboxSelected>>", self.on_report_select)
        self.dynamic_controls_frame = ttk.Frame(controls_frame); self.dynamic_controls_frame.pack(side=tk.LEFT, padx=20)
        self.generate_button = ttk.Button(controls_frame, text="Generate", command=self.run_report); self.generate_button.pack(side=tk.LEFT)
        
        self.results_frame = ttk.Frame(main_frame)
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        self.single_tree_frame, self.single_tree = self.create_single_results_tree(self.results_frame)
        self.referral_paned_window = ttk.PanedWindow(self.results_frame, orient=tk.VERTICAL)
        self.referrals_frame = ttk.LabelFrame(self.referral_paned_window, text="Candidates WITH Referrals", padding="10"); self.referral_paned_window.add(self.referrals_frame, weight=1)
        self.referrals_tree = self.create_referral_tree(self.referrals_frame)
        self.no_referrals_frame = ttk.LabelFrame(self.referral_paned_window, text="Candidates WITHOUT Referrals", padding="10"); self.referral_paned_window.add(self.no_referrals_frame, weight=1)
        self.no_referrals_tree = self.create_referral_tree(self.no_referrals_frame, show_referrer=False)
        
    def create_single_results_tree(self, parent):
        frame = ttk.Frame(parent)
        tree = ttk.Treeview(frame, show='headings')
        v_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview); tree.configure(yscroll=v_scroll.set)
        h_scroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview); tree.configure(xscroll=h_scroll.set)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y); h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        return frame, tree

    def create_referral_tree(self, parent, show_referrer=True):
        cols = ('last_name', 'first_name', 'referred_by', 'department', 'status') if show_referrer else ('last_name', 'first_name', 'department', 'status')
        tree = ttk.Treeview(parent, columns=cols, show='headings')
        for col in cols: tree.heading(col, text=col.replace('_', ' ').title())
        v_scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview); tree.configure(yscroll=v_scroll.set)
        h_scroll = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=tree.xview); tree.configure(xscroll=h_scroll.set)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y); h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        return tree

    def on_report_select(self, event):
        report_type = self.report_var.get()
        for widget in self.dynamic_controls_frame.winfo_children(): widget.destroy()
        
        self.single_tree_frame.pack_forget()
        self.referral_paned_window.pack_forget()
        
        if report_type == "Search by Referrer":
            ttk.Label(self.dynamic_controls_frame, text="Referrer Name:").pack(side=tk.LEFT)
            self.referrer_search_entry = ttk.Entry(self.dynamic_controls_frame, width=25); self.referrer_search_entry.pack(side=tk.LEFT)
            self.single_tree_frame.pack(fill=tk.BOTH, expand=True)
        elif report_type == "Hires by Department":
            ttk.Label(self.dynamic_controls_frame, text="Start Date (YYYY-MM-DD):").pack(side=tk.LEFT)
            self.start_date_entry = ttk.Entry(self.dynamic_controls_frame, width=12); self.start_date_entry.pack(side=tk.LEFT, padx=(0, 5))
            ttk.Label(self.dynamic_controls_frame, text="End Date:").pack(side=tk.LEFT)
            self.end_date_entry = ttk.Entry(self.dynamic_controls_frame, width=12); self.end_date_entry.pack(side=tk.LEFT)
            self.single_tree_frame.pack(fill=tk.BOTH, expand=True)
        elif report_type == "Last Week's Referrals" or report_type == "Referrals by Class Week":
            self.referral_paned_window.pack(fill=tk.BOTH, expand=True)
            if report_type == "Referrals by Class Week":
                ttk.Label(self.dynamic_controls_frame, text="Select Class:").pack(side=tk.LEFT)
                self.class_report_combo = ttk.Combobox(self.dynamic_controls_frame, state="readonly")
                self.class_report_combo.pack(side=tk.LEFT)
                try:
                    conn = get_db_connection(); cursor = conn.cursor()
                    cursor.execute("SELECT strftime('%Y-%m-%d', class_date) FROM Hiring_Classes ORDER BY class_date DESC;")
                    self.class_report_combo['values'] = [row[0] for row in cursor.fetchall()]
                    conn.close()
                except Exception as e: messagebox.showerror("DB Error", f"Could not load class dates: {e}", parent=self)
        else:
            self.single_tree_frame.pack_forget()
            self.referral_paned_window.pack_forget()

    def run_report(self):
        report_type = self.report_var.get()
        if not report_type: messagebox.showwarning("Selection Error", "Please select a report to run.", parent=self); return
        
        try:
            conn = get_db_connection(); conn.row_factory = sqlite3.Row; cursor = conn.cursor()
            
            if report_type == "Weekly Activity Snapshot":
                self.generate_weekly_activity_report(cursor)
            elif report_type == "Referral Leaderboard":
                for item in self.single_tree.get_children(): self.single_tree.delete(item)
                self.setup_treeview(self.single_tree, ['Referrer', 'Total Referrals'])
                query = "SELECT referred_by, COUNT(*) FROM Candidates WHERE referred_by IS NOT NULL AND referred_by != '' GROUP BY referred_by ORDER BY COUNT(*) DESC;"
                cursor.execute(query)
                results = cursor.fetchall()
                if not results: self.single_tree.insert('', tk.END, values=("No results found.",))
                else:
                    for row in results: self.single_tree.insert('', tk.END, values=tuple(row))

            elif report_type == "Hires by Department":
                for item in self.single_tree.get_children(): self.single_tree.delete(item)
                self.setup_treeview(self.single_tree, ['Department', 'Total Hires'])
                start_date = self.start_date_entry.get().strip(); end_date = self.end_date_entry.get().strip()
                query = "SELECT j.department, COUNT(*) FROM Candidates c JOIN Jobs j ON c.fk_job_id = j.job_id WHERE c.candidate_status = 'Hired'"; params = []
                if start_date: query += " AND c.interview_date >= ?"; params.append(start_date)
                if end_date: query += " AND c.interview_date <= ?"; params.append(end_date)
                query += " GROUP BY j.department ORDER BY COUNT(*) DESC;"
                cursor.execute(query, params)
                results = cursor.fetchall()
                if not results: self.single_tree.insert('', tk.END, values=("No results found.",))
                else:
                    for row in results: self.single_tree.insert('', tk.END, values=tuple(row))

            elif report_type == "Search by Referrer":
                for item in self.single_tree.get_children(): self.single_tree.delete(item)
                self.setup_treeview(self.single_tree, ['Last Name', 'First Name', 'Department', 'Status'])
                referrer_name = self.referrer_search_entry.get().strip()
                if not referrer_name: messagebox.showwarning("Input Error", "Please enter a referrer name to search.", parent=self); conn.close(); return
                query = "SELECT c.last_name, c.first_name, j.department, c.candidate_status FROM Candidates c LEFT JOIN Jobs j ON c.fk_job_id = j.job_id WHERE c.referred_by LIKE ? ORDER BY c.last_name;"
                cursor.execute(query, (f"%{referrer_name}%",))
                results = cursor.fetchall()
                if not results: self.single_tree.insert('', tk.END, values=("No results found.",))
                else:
                    for row in results: self.single_tree.insert('', tk.END, values=tuple(row))
            
            elif report_type == "Last Week's Referrals" or report_type == "Referrals by Class Week":
                for tree in [self.referrals_tree, self.no_referrals_tree]:
                    for item in tree.get_children(): tree.delete(item)
                
                if report_type == "Last Week's Referrals":
                    query = "SELECT c.last_name, c.first_name, j.department, c.candidate_status, c.referred_by FROM Candidates c LEFT JOIN Jobs j ON c.fk_job_id = j.job_id WHERE c.interview_date BETWEEN date('now', 'weekday 1', '-7 days') AND date('now', 'weekday 1', '-1 day');"
                    cursor.execute(query)
                else: # Referrals by Class Week
                    class_date = self.class_report_combo.get()
                    if not class_date: messagebox.showwarning("Input Error", "Please select a class date.", parent=self); conn.close(); return
                    query = "SELECT c.last_name, c.first_name, j.department, c.candidate_status, c.referred_by FROM Candidates c LEFT JOIN Jobs j ON c.fk_job_id = j.job_id JOIN Hiring_Classes hc ON c.fk_class_id = hc.class_id WHERE hc.class_date = ?;"
                    cursor.execute(query, (class_date,))

                results = cursor.fetchall()
                if not results: 
                    self.referrals_tree.insert('', tk.END, values=("No candidates found for this period.",))
                    self.no_referrals_tree.insert('', tk.END, values=("No candidates found for this period.",))
                else:
                    for row in results:
                        if row['referred_by']: self.referrals_tree.insert('', tk.END, values=(row['last_name'], row['first_name'], row['referred_by'], row['department'], row['candidate_status']))
                        else: self.no_referrals_tree.insert('', tk.END, values=(row['last_name'], row['first_name'], row['department'], row['candidate_status']))

            conn.close()
        except sqlite3.Error as e: messagebox.showerror("Database Error", f"Failed to run report: {e}", parent=self)
        except Exception as e: messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)

    def setup_treeview(self, tree, columns):
        tree['columns'] = columns
        for col in columns:
            tree.heading(col, text=col.replace('_', ' ').title())
            tree.column(col, width=150, anchor=tk.W)

    def generate_weekly_activity_report(self, cursor):
        today = datetime.date.today()
        # weekday() is Monday=0...Sunday=6. To get to last Saturday, we subtract (today.weekday() + 2) days.
        last_saturday = today - datetime.timedelta(days=today.weekday() + 2)
        last_sunday = last_saturday - datetime.timedelta(days=6)
        
        date_range_str = f"{last_sunday.strftime('%B %d, %Y')} - {last_saturday.strftime('%B %d, %Y')}"
        
        # --- Fetch Data ---
        cursor.execute("SELECT SUM(apps_reviewed), SUM(interviews_scheduled), SUM(hires_confirmed) FROM Daily_Metrics WHERE metric_date BETWEEN ? AND ?", (last_sunday, last_saturday))
        metrics = cursor.fetchone()
        
        cursor.execute("SELECT category, reason, SUM(count) FROM Daily_Breakdowns db JOIN Daily_Metrics dm ON db.fk_metric_id = dm.metric_id WHERE dm.metric_date BETWEEN ? AND ? GROUP BY category, reason", (last_sunday, last_saturday))
        breakdowns = cursor.fetchall()

        # --- Process Data ---
        data = {
            "Apps Received": metrics['SUM(apps_reviewed)'] or 0,
            "Interviews": metrics['SUM(interviews_scheduled)'] or 0,
            "Offers": metrics['SUM(hires_confirmed)'] or 0,
            "Withdrew": 0,
            "Decline": 0,
            "NCNS": 0
        }
        for category, reason, count in breakdowns:
            if 'withdrawal' in category:
                data["Withdrew"] += count
            elif 'rejection' in category:
                if reason == 'NCNS':
                    data["NCNS"] += count
                else:
                    data["Decline"] += count

        # --- Generate HTML ---
        html_content = f"""
        <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Weekly Activity Snapshot</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; color: #333; }}
            .container {{ padding: 20px; border: 1px solid #6b92c2; width: 350px; margin: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); background-color: #cedbeb; }}
            h2 {{ color: #084999; text-align: center; }}
            p {{ text-align: center; margin-top: -10px; color: #396dad; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ border: 1px solid #6b92c2; text-align: left; padding: 10px; font-size: 1.1em; }}
            th {{ background-color: #396dad; color: white; }}
            td:nth-child(2) {{ text-align: center; font-weight: bold; }}
            tbody tr:nth-child(even) {{ background-color: #ffffff; }}
            tbody tr:nth-child(odd) {{ background-color: #e8eef4; }}
        </style></head><body><div class="container">
        <h2>Weekly Activity Snapshot</h2><p>{date_range_str}</p>
        <table>
            <thead><tr><th>Categories</th><th>Total</th></tr></thead>
            <tbody>
                <tr><td>Apps Received</td><td>{data['Apps Received']}</td></tr>
                <tr><td>Interviews</td><td>{data['Interviews']}</td></tr>
                <tr><td>Offers</td><td>{data['Offers']}</td></tr>
                <tr><td>Withdrew</td><td>{data['Withdrew']}</td></tr>
                <tr><td>Decline</td><td>{data['Decline']}</td></tr>
                <tr><td>NCNS</td><td>{data['NCNS']}</td></tr>
            </tbody>
        </table></div></body></html>
        """
        
        output_filename = 'weekly_activity_snapshot.html'
        with open(output_filename, 'w', encoding='utf-8') as file: file.write(html_content)
        full_path = os.path.abspath(output_filename)
        webbrowser.open_new_tab(f"file://{full_path}")
        messagebox.showinfo("Success", f"Report generated successfully and opened in your browser!\n\nSaved as: {full_path}", parent=self)

# --- Run the Main Application ---
if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        messagebox.showerror("Database Not Found", f"The database file could not be found at:\n{DB_PATH}\n\nPlease ensure the application and database are in the correct folder.")
    else:
        app = MainApp()
        app.mainloop()
