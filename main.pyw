import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import os
import datetime  #-- Not used, but here if needed  # noqa: F401
import sqlite3
from common import center_window, get_db_connection
from new_candidate import NewCandidateApp
from search_update import SearchApp
from historical_viewer import HistoricalViewerApp
from dashboard import DashboardApp
from applicant_tracker import ApplicantTrackerApp
from reports import ReportsApp
from admin import AdminApp

# --- Version 2.0.1 ---

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title("HR Management System")
        self.geometry("500x620")
        
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        
        BG_COLOR = '#cedbeb'
        PRIMARY_BLUE = '#084999'
        SECONDARY_BLUE = '#396dad'
        BUTTON_TEXT_COLOR = 'white'
        FONT_FAMILY = "Segoe UI"

        self.configure(bg=BG_COLOR)
        
        self.style.configure('TFrame', background=BG_COLOR)
        self.style.configure('TLabel', font=(FONT_FAMILY, 10), background=BG_COLOR, foreground=PRIMARY_BLUE)
        self.style.configure('Header.TLabel', font=(FONT_FAMILY, 18, 'bold'), background=BG_COLOR, foreground=PRIMARY_BLUE)
        self.style.configure('TButton', font=(FONT_FAMILY, 10, 'bold'), padding=12, background=PRIMARY_BLUE, foreground=BUTTON_TEXT_COLOR, borderwidth=0)
        self.style.map('TButton', background=[('active', SECONDARY_BLUE)], relief=[('pressed', 'sunken')])
        self.style.configure('TLabelframe', background=BG_COLOR)
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
            window_class(self)
        except Exception as e:
            messagebox.showerror("Application Error", f"Could not open window: {e}")

    def open_new_candidate_window(self):
        self.open_window(NewCandidateApp)

    def open_search_window(self):
        self.open_window(SearchApp)

    def open_historical_viewer_window(self):
        self.open_window(HistoricalViewerApp)

    def open_dashboard_window(self):
        self.open_window(DashboardApp)

    def open_admin_window(self):
        self.open_window(AdminApp)

    def open_reports_window(self):
        self.open_window(ReportsApp)

    def open_applicant_tracker_window(self):
        self.open_window(ApplicantTrackerApp)
    
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
            if not display_rows:
                html_content += "<p style='font-style: italic; color: #555;'>No new hires are fully cleared to start for the upcoming week.</p>"
            else:
                html_content += "<hr style='margin-top: 20px; margin-bottom: 20px; border: 0; border-top: 1px solid #ddd;'>"
                html_content += "<table><thead><tr>"
                for header in display_headers:
                    html_content += f"<th>{header}</th>"
                html_content += "</tr></thead><tbody>"
                for row in display_rows:
                    html_content += "<tr>"
                    for cell in row:
                        html_content += f"<td>{str(cell).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}</td>"
                    html_content += "</tr>"
                html_content += "</tbody></table>"
            html_content += "</div></body></html>"
            output_filename = 'weekly_report.html'
            with open(output_filename, 'w', encoding='utf-8') as file:
                file.write(html_content)
            full_path = os.path.abspath(output_filename)
            webbrowser.open_new_tab(f"file://{full_path}")
            messagebox.showinfo("Success", f"Report generated successfully and opened in your browser!\n\nSaved as: {full_path}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to generate report: {e}\n\nPlease ensure the 'V_Cleared_Hires_Next_Week' VIEW exists.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
