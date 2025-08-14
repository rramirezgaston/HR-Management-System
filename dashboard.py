import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from common import get_db_connection, center_window
from search_update import EditWindow

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
