import sqlite3
import os

def view_users():
    db_path = 'finance_manager.db'
    
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("Error: 'users' table does not exist in the database.")
            return

        cursor.execute("SELECT id, username, full_name, email, mobile FROM users")
        rows = cursor.fetchall()
        
        if not rows:
            print("\n--- No users found in the database ---\n")
        else:
            print("\n" + "="*80)
            print(f"{'ID':<4} | {'Username':<15} | {'Full Name':<20} | {'Email':<25} | {'Mobile':<12}")
            print("-" * 80)
            for row in rows:
                user_id, username, full_name, email, mobile = row
                print(f"{user_id:<4} | {username:<15} | {full_name:<20} | {email:<25} | {mobile:<12}")
            print("="*80 + "\n")
            
        conn.close()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    view_users()
