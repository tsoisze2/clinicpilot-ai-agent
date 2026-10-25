import sqlite3
import csv
import os

DB_NAME = "clinicpilot.db"
DATA_DIR = "data"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Updated schema to include the 'notes' column found in the CSV
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patient_bookings (
        booking_id TEXT PRIMARY KEY,
        patient_id TEXT,
        doctor_id TEXT,
        treatment_id TEXT,
        booking_date TEXT,
        booking_time TEXT,
        status TEXT,
        notes TEXT
    )
    ''')

    def load_csv_to_table(table_name, csv_filename):
        file_path = os.path.join(DATA_DIR, csv_filename)
        if not os.path.exists(file_path):
            print(f"Warning: '{file_path}' not found. Ensure datasets are in the 'data' directory.")
            return

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            headers = next(reader)
            
            headers = [h.strip().replace(" ", "_").lower() for h in headers]
            
            if table_name != "patient_bookings":
                columns = ", ".join([f"{header} TEXT" for header in headers])
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
            
            cursor.execute(f"DELETE FROM {table_name}")
            
            placeholders = ", ".join(["?" for _ in headers])
            insert_query = f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES ({placeholders})"
            
            for row in reader:
                cursor.execute(insert_query, row)
        
        print(f"Successfully seeded '{table_name}' from '{csv_filename}'.")

    load_csv_to_table("clinics", "clinics.csv")
    load_csv_to_table("doctors", "doctors.csv")
    load_csv_to_table("treatments", "treatments.csv")
    load_csv_to_table("patients", "patients.csv")
    load_csv_to_table("patient_bookings", "patient_bookings.csv")
    load_csv_to_table("patient_treatment_history", "patient_treatment_history.csv")

    conn.commit()
    conn.close()
    print(f"\nDatabase initialization complete. SQLite DB saved as '{DB_NAME}'.")

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    init_db()