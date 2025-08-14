import sqlite3
import csv
import os
import sys

# --- Version 1.1.2 ---

# --- Configuration ---
# Get the absolute path of the directory where the script is located
script_dir = os.path.dirname(os.path.realpath(__file__))
# Join the script directory with the database and CSV filenames
DB_PATH = os.path.join(script_dir, 'HR_Hiring_DB.db')
CSV_PATH = os.path.join(script_dir, 'historical_data.csv')

def get_db_connection():
    """Establishes a database connection and enables foreign key support."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def migrate_data():
    """Reads the historical_data.csv and populates the database."""
    if not os.path.exists(CSV_PATH):
        print(f"ERROR: The file 'historical_data.csv' was not found in the directory.")
        print("Please make sure it is saved in the same folder as this script.")
        return

    # This dictionary maps the exact CSV column headers to the database category and reason
    breakdown_mapping = {
        "Rejection_Pre_Not eligible for Rehire": ("pre_interview_rejection", "Not eligible for Rehire"),
        "Rejection_Pre_Background": ("pre_interview_rejection", "Background"),
        "Rejection_Pre_Not a good Fit": ("pre_interview_rejection", "Not a good Fit"),
        "Withdrawal_Pre_Schedule": ("pre_interview_withdrawal", "Schedule"),
        "Withdrawal_Pre_Other Job Offer": ("pre_interview_withdrawal", "Other Job Offer"),
        "Withdrawal_Pre_Pay": ("pre_interview_withdrawal", "Pay"),
        "Withdrawal_Pre_Other": ("pre_interview_withdrawal", "Other"),
        "Rejection_Post_Not eligible for Rehire": ("post_interview_rejection", "Not eligible for Rehire"),
        "Rejection_Post_Background": ("post_interview_rejection", "Background"),
        "Rejection_Post_Not a good Fit": ("post_interview_rejection", "Not a good Fit"),
        "Rejection_Post_NCNS": ("post_interview_rejection", "NCNS"),
        "Withdrawal_Post_Schedule": ("post_interview_withdrawal", "Schedule"),
        "Withdrawal_Post_Other Job Offer": ("post_interview_withdrawal", "Other Job Offer"),
        "Withdrawal_Post_Pay": ("post_interview_withdrawal", "Pay"),
        "Withdrawal_Post_Other": ("post_interview_withdrawal", "Other"),
    }

    encodings_to_try = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
    
    data_rows = []
    success = False
    fieldnames = []
    for encoding in encodings_to_try:
        try:
            with open(CSV_PATH, mode='r', encoding=encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                data_rows = list(reader)
                print(f"Successfully read CSV file using '{encoding}' encoding.")
                success = True
                break
        except (UnicodeDecodeError, KeyError):
            print(f"Failed to read with '{encoding}' encoding, trying next...")
            continue
    
    if not success:
        print("\nERROR: Could not read the CSV file with any of the common encodings.")
        print("Please open the file in a text editor, save it with 'UTF-8' encoding, and try again.")
        return

    # --- NEW: Robustly find the date column key ---
    date_key = None
    for name in fieldnames:
        # Normalize the name by removing BOM, stripping whitespace, and making it lowercase
        if name.lstrip('\ufeff').strip().lower() == 'date':
            date_key = name
            break

    if not date_key:
        print("\nDATA ERROR: Could not find a 'Date' column in your CSV file.")
        print(f"The headers found were: {fieldnames}")
        print("Please ensure one of the columns is named 'Date'.")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        for i, row in enumerate(data_rows):
            date_str = row[date_key]
            print(f"Processing row {i+1}: Date {date_str}...")

            # --- Step 1: Insert or Update the Daily_Metrics table ---
            apps_reviewed = int(row.get('Apps Reviewed', 0) or 0)
            interviews_scheduled = int(row.get('Interviews Scheduled', 0) or 0)
            hires_confirmed = int(row.get('Hires Confirmed', 0) or 0)

            cursor.execute("SELECT metric_id FROM Daily_Metrics WHERE metric_date = ?", (date_str,))
            result = cursor.fetchone()

            if result:
                metric_id = result[0]
                cursor.execute("""
                    UPDATE Daily_Metrics 
                    SET apps_reviewed = ?, interviews_scheduled = ?, hires_confirmed = ?
                    WHERE metric_id = ?
                """, (apps_reviewed, interviews_scheduled, hires_confirmed, metric_id))
            else:
                cursor.execute("""
                    INSERT INTO Daily_Metrics (metric_date, apps_reviewed, interviews_scheduled, hires_confirmed)
                    VALUES (?, ?, ?, ?)
                """, (date_str, apps_reviewed, interviews_scheduled, hires_confirmed))
                metric_id = cursor.lastrowid
            
            # --- Step 2: Clear old breakdowns and insert new ones ---
            cursor.execute("DELETE FROM Daily_Breakdowns WHERE fk_metric_id = ?", (metric_id,))

            breakdown_data_to_insert = []
            for header, (category, reason) in breakdown_mapping.items():
                count = int(row.get(header, 0) or 0)
                if count > 0:
                    breakdown_data_to_insert.append((metric_id, category, reason, count))
            
            if breakdown_data_to_insert:
                cursor.executemany("INSERT INTO Daily_Breakdowns (fk_metric_id, category, reason, count) VALUES (?, ?, ?, ?)", breakdown_data_to_insert)

        conn.commit()
        conn.close()
        print("\nMigration complete! All historical data has been successfully imported.")

    except sqlite3.Error as e:
        print(f"\nDATABASE ERROR: An error occurred during migration: {e}")
        print("The database has not been changed. Please check your data and try again.")
    except (KeyError, ValueError) as e:
        print(f"\nDATA ERROR: An error occurred processing the CSV file: {e}")
        print("Please ensure all column headers are spelled correctly and all data cells contain valid numbers.")
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: An unexpected error occurred: {e}")

if __name__ == "__main__":
    migrate_data()
