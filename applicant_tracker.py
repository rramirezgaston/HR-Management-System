import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from common import get_db_connection, center_window

class ApplicantTrackerApp(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.withdraw()
        self.title("Applicant Tracker")
        self.geometry("900x820")
        self.transient(parent)
        self.grab_set()

        self.style = ttk.Style(self)
        self.style.configure('Small.TButton', padding=(2, 2), font=("Segoe UI", 8))
        self.style.configure('Minus.Small.TButton', padding=(2, 2), font=("Segoe UI", 8), background='#aeb9c6')
        self.style.map('Minus.Small.TButton', background=[('active', '#c7d0d9')])

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

        date_frame = ttk.Frame(main_frame)
        date_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(date_frame, text="Select Date:", font=("Segoe UI", 11, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        self.date_entry = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.pack(side=tk.LEFT)
        self.date_entry.bind("<<DateEntrySelected>>", self.load_data_for_date)

        metrics_frame = ttk.LabelFrame(main_frame, text="Daily Metrics", padding="15")
        metrics_frame.pack(fill=tk.X, pady=(0, 15))
        
        core_metrics = ["Apps Reviewed", "Interviews Scheduled", "Hires Confirmed"]
        for i, metric in enumerate(core_metrics):
            self.metric_vars[metric] = tk.StringVar(value='0')
            self.create_metric_row(metrics_frame, metric, self.metric_vars[metric], i)

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

        ttk.Button(main_frame, text="Save Log for Selected Date", command=self.save_data).pack(pady=(20, 0))

    def _validate_and_revert(self, var, key):
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
        key = label.replace(" ", "_")
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
            
            for key, var in self.metric_vars.items(): self.previous_values[key.replace(" ", "_")] = var.get()
            for key, var in self.breakdown_vars.items(): self.previous_values[key] = var.get()

            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load data: {e}", parent=self)

    def save_data(self):
        selected_date = self.date_entry.get_date().strftime("%Y-%m-%d")
        
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
            self.load_data_for_date()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save data: {e}", parent=self)
