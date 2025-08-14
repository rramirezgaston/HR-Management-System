import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import webbrowser
import os
from common import get_db_connection, center_window

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
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        controls_frame = ttk.LabelFrame(main_frame, text="Report Options", padding="10")
        controls_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(controls_frame, text="Select Report:").pack(side=tk.LEFT, padx=(0, 10))
        self.report_var = tk.StringVar()
        report_options = ["Weekly Activity Snapshot", "Referral Leaderboard", "Hires by Department", "Search by Referrer", "Last Week's Referrals", "Referrals by Class Week"]
        self.report_combo = ttk.Combobox(controls_frame, textvariable=self.report_var, values=report_options, state="readonly", width=30)
        self.report_combo.pack(side=tk.LEFT, padx=5)
        self.report_combo.bind("<<ComboboxSelected>>", self.on_report_select)
        self.dynamic_controls_frame = ttk.Frame(controls_frame)
        self.dynamic_controls_frame.pack(side=tk.LEFT, padx=20)
        self.generate_button = ttk.Button(controls_frame, text="Generate", command=self.run_report)
        self.generate_button.pack(side=tk.LEFT)
        
        self.results_frame = ttk.Frame(main_frame)
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        self.single_tree_frame, self.single_tree = self.create_single_results_tree(self.results_frame)
        self.referral_paned_window = ttk.PanedWindow(self.results_frame, orient=tk.VERTICAL)
        self.referrals_frame = ttk.LabelFrame(self.referral_paned_window, text="Candidates WITH Referrals", padding="10")
        self.referral_paned_window.add(self.referrals_frame, weight=1)
        self.referrals_tree = self.create_referral_tree(self.referrals_frame)
        self.no_referrals_frame = ttk.LabelFrame(self.referral_paned_window, text="Candidates WITHOUT Referrals", padding="10")
        self.referral_paned_window.add(self.no_referrals_frame, weight=1)
        self.no_referrals_tree = self.create_referral_tree(self.no_referrals_frame, show_referrer=False)
        
    def create_single_results_tree(self, parent):
        frame = ttk.Frame(parent)
        tree = ttk.Treeview(frame, show='headings')
        v_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=v_scroll.set)
        h_scroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(xscroll=h_scroll.set)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        return frame, tree

    def create_referral_tree(self, parent, show_referrer=True):
        cols = ('last_name', 'first_name', 'referred_by', 'department', 'status') if show_referrer else ('last_name', 'first_name', 'department', 'status')
        tree = ttk.Treeview(parent, columns=cols, show='headings')
        for col in cols:
            tree.heading(col, text=col.replace('_', ' ').title())
        v_scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=v_scroll.set)
        h_scroll = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(xscroll=h_scroll.set)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        return tree

    def on_report_select(self, event):
        report_type = self.report_var.get()
        for widget in self.dynamic_controls_frame.winfo_children():
            widget.destroy()
        
        self.single_tree_frame.pack_forget()
        self.referral_paned_window.pack_forget()
        
        if report_type == "Search by Referrer":
            ttk.Label(self.dynamic_controls_frame, text="Referrer Name:").pack(side=tk.LEFT)
            self.referrer_search_entry = ttk.Entry(self.dynamic_controls_frame, width=25)
            self.referrer_search_entry.pack(side=tk.LEFT)
            self.single_tree_frame.pack(fill=tk.BOTH, expand=True)
        elif report_type == "Hires by Department":
            ttk.Label(self.dynamic_controls_frame, text="Start Date (YYYY-MM-DD):").pack(side=tk.LEFT)
            self.start_date_entry = ttk.Entry(self.dynamic_controls_frame, width=12)
            self.start_date_entry.pack(side=tk.LEFT, padx=(0, 5))
            ttk.Label(self.dynamic_controls_frame, text="End Date:").pack(side=tk.LEFT)
            self.end_date_entry = ttk.Entry(self.dynamic_controls_frame, width=12)
            self.end_date_entry.pack(side=tk.LEFT)
            self.single_tree_frame.pack(fill=tk.BOTH, expand=True)
        elif report_type == "Last Week's Referrals" or report_type == "Referrals by Class Week":
            self.referral_paned_window.pack(fill=tk.BOTH, expand=True)
            if report_type == "Referrals by Class Week":
                ttk.Label(self.dynamic_controls_frame, text="Select Class:").pack(side=tk.LEFT)
                self.class_report_combo = ttk.Combobox(self.dynamic_controls_frame, state="readonly")
                self.class_report_combo.pack(side=tk.LEFT)
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT strftime('%Y-%m-%d', class_date) FROM Hiring_Classes ORDER BY class_date DESC;")
                    self.class_report_combo['values'] = [row[0] for row in cursor.fetchall()]
                    conn.close()
                except Exception as e:
                    messagebox.showerror("DB Error", f"Could not load class dates: {e}", parent=self)
        else:
            self.single_tree_frame.pack_forget()
            self.referral_paned_window.pack_forget()

    def run_report(self):
        report_type = self.report_var.get()
        if not report_type:
            messagebox.showwarning("Selection Error", "Please select a report to run.", parent=self)
            return
        
        try:
            conn = get_db_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if report_type == "Weekly Activity Snapshot":
                self.generate_weekly_activity_report(cursor)
            elif report_type == "Referral Leaderboard":
                for item in self.single_tree.get_children():
                    self.single_tree.delete(item)
                self.setup_treeview(self.single_tree, ['Referrer', 'Total Referrals'])
                query = "SELECT referred_by, COUNT(*) FROM Candidates WHERE referred_by IS NOT NULL AND referred_by != '' GROUP BY referred_by ORDER BY COUNT(*) DESC;"
                cursor.execute(query)
                results = cursor.fetchall()
                if not results:
                    self.single_tree.insert('', tk.END, values=("No results found.",))
                else:
                    for row in results:
                        self.single_tree.insert('', tk.END, values=tuple(row))

            elif report_type == "Hires by Department":
                for item in self.single_tree.get_children():
                    self.single_tree.delete(item)
                self.setup_treeview(self.single_tree, ['Department', 'Total Hires'])
                start_date = self.start_date_entry.get().strip()
                end_date = self.end_date_entry.get().strip()
                query = "SELECT j.department, COUNT(*) FROM Candidates c JOIN Jobs j ON c.fk_job_id = j.job_id WHERE c.candidate_status = 'Hired'"
                params = []
                if start_date:
                    query += " AND c.interview_date >= ?"
                    params.append(start_date)
                if end_date:
                    query += " AND c.interview_date <= ?"
                    params.append(end_date)
                query += " GROUP BY j.department ORDER BY COUNT(*) DESC;"
                cursor.execute(query, params)
                results = cursor.fetchall()
                if not results:
                    self.single_tree.insert('', tk.END, values=("No results found.",))
                else:
                    for row in results:
                        self.single_tree.insert('', tk.END, values=tuple(row))

            elif report_type == "Search by Referrer":
                for item in self.single_tree.get_children():
                    self.single_tree.delete(item)
                self.setup_treeview(self.single_tree, ['Last Name', 'First Name', 'Department', 'Status'])
                referrer_name = self.referrer_search_entry.get().strip()
                if not referrer_name:
                    messagebox.showwarning("Input Error", "Please enter a referrer name to search.", parent=self)
                    conn.close()
                    return
                query = "SELECT c.last_name, c.first_name, j.department, c.candidate_status FROM Candidates c LEFT JOIN Jobs j ON c.fk_job_id = j.job_id WHERE c.referred_by LIKE ? ORDER BY c.last_name;"
                cursor.execute(query, (f"%{referrer_name}%",))
                results = cursor.fetchall()
                if not results:
                    self.single_tree.insert('', tk.END, values=("No results found.",))
                else:
                    for row in results:
                        self.single_tree.insert('', tk.END, values=tuple(row))
            
            elif report_type == "Last Week's Referrals" or report_type == "Referrals by Class Week":
                for tree in [self.referrals_tree, self.no_referrals_tree]:
                    for item in tree.get_children():
                        tree.delete(item)
                
                if report_type == "Last Week's Referrals":
                    query = "SELECT c.last_name, c.first_name, j.department, c.candidate_status, c.referred_by FROM Candidates c LEFT JOIN Jobs j ON c.fk_job_id = j.job_id WHERE c.interview_date BETWEEN date('now', 'weekday 1', '-7 days') AND date('now', 'weekday 1', '-1 day');"
                    cursor.execute(query)
                else: # Referrals by Class Week
                    class_date = self.class_report_combo.get()
                    if not class_date:
                        messagebox.showwarning("Input Error", "Please select a class date.", parent=self)
                        conn.close()
                        return
                    query = "SELECT c.last_name, c.first_name, j.department, c.candidate_status, c.referred_by FROM Candidates c LEFT JOIN Jobs j ON c.fk_job_id = j.job_id JOIN Hiring_Classes hc ON c.fk_class_id = hc.class_id WHERE hc.class_date = ?;"
                    cursor.execute(query, (class_date,))

                results = cursor.fetchall()
                if not results: 
                    self.referrals_tree.insert('', tk.END, values=("No candidates found for this period.",))
                    self.no_referrals_tree.insert('', tk.END, values=("No candidates found for this period.",))
                else:
                    for row in results:
                        if row['referred_by']:
                            self.referrals_tree.insert('', tk.END, values=(row['last_name'], row['first_name'], row['referred_by'], row['department'], row['candidate_status']))
                        else:
                            self.no_referrals_tree.insert('', tk.END, values=(row['last_name'], row['first_name'], row['department'], row['candidate_status']))

            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to run report: {e}", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)

    def setup_treeview(self, tree, columns):
        tree['columns'] = columns
        for col in columns:
            tree.heading(col, text=col.replace('_', ' ').title())
            tree.column(col, width=150, anchor=tk.W)

    def generate_weekly_activity_report(self, cursor):
        today = datetime.date.today()
        last_saturday = today - datetime.timedelta(days=today.weekday() + 2)
        last_sunday = last_saturday - datetime.timedelta(days=6)
        
        date_range_str = f"{last_sunday.strftime('%B %d, %Y')} - {last_saturday.strftime('%B %d, %Y')}"
        
        cursor.execute("SELECT SUM(apps_reviewed), SUM(interviews_scheduled), SUM(hires_confirmed) FROM Daily_Metrics WHERE metric_date BETWEEN ? AND ?", (last_sunday, last_saturday))
        metrics = cursor.fetchone()
        
        cursor.execute("SELECT category, reason, SUM(count) FROM Daily_Breakdowns db JOIN Daily_Metrics dm ON db.fk_metric_id = dm.metric_id WHERE dm.metric_date BETWEEN ? AND ? GROUP BY category, reason", (last_sunday, last_saturday))
        breakdowns = cursor.fetchall()

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
        with open(output_filename, 'w', encoding='utf-8') as file:
            file.write(html_content)
        full_path = os.path.abspath(output_filename)
        webbrowser.open_new_tab(f"file://{full_path}")
        messagebox.showinfo("Success", f"Report generated successfully and opened in your browser!\n\nSaved as: {full_path}", parent=self)
