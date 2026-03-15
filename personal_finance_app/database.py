import sqlite3
from datetime import datetime
from models import Transaction, Goal, Investment

DB_NAME = 'finance_manager.db'

def get_connection():
    return sqlite3.connect(DB_NAME)

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trans_type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    
    # Budget table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            amount REAL NOT NULL,
            savings_goal REAL NOT NULL DEFAULT 0,
            current_savings REAL NOT NULL DEFAULT 0
        )
    ''')
    
    try:
        cursor.execute('ALTER TABLE budget ADD COLUMN savings_goal REAL NOT NULL DEFAULT 0')
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute('ALTER TABLE budget ADD COLUMN current_savings REAL NOT NULL DEFAULT 0')
    except sqlite3.OperationalError:
        pass

    # Goals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL NOT NULL DEFAULT 0
        )
    ''')

    # Investments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL
        )
    ''')
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            mobile TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Try adding new columns if the table already existed from the previous simple version
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN full_name TEXT NOT NULL DEFAULT ""')
        cursor.execute('ALTER TABLE users ADD COLUMN email TEXT NOT NULL DEFAULT ""')
        cursor.execute('ALTER TABLE users ADD COLUMN mobile TEXT NOT NULL DEFAULT ""')
    except sqlite3.OperationalError:
        pass
        
    conn.commit()
    conn.close()

def create_user(username: str, full_name: str, email: str, mobile: str, password_hash: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, full_name, email, mobile, password_hash) VALUES (?, ?, ?, ?, ?)', 
                   (username, full_name, email, mobile, password_hash))
    conn.commit()
    conn.close()

def get_user_by_username(username: str) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password_hash, full_name, email, mobile FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0], 
            "username": row[1], 
            "password_hash": row[2],
            "full_name": row[3],
            "email": row[4],
            "mobile": row[5]
        }
    return None

# --- Transactions & Budget ---

def add_transaction(trans_type: str, amount: float, category: str):
    conn = get_connection()
    cursor = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('INSERT INTO transactions (trans_type, amount, category, date) VALUES (?, ?, ?, ?)', (trans_type, amount, category, date_str))
    conn.commit()
    conn.close()

def set_budget(amount: float, savings_goal: float = 0.0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO budget (id, amount, savings_goal) VALUES (1, ?, ?)', (amount, savings_goal))
    conn.commit()
    conn.close()

def get_budget() -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT amount, savings_goal, current_savings FROM budget WHERE id = 1')
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"amount": row[0], "savings_goal": row[1], "current_savings": row[2] if len(row) > 2 else 0.0}
    return {"amount": 0.0, "savings_goal": 0.0, "current_savings": 0.0}

def add_to_savings(amount: float):
    conn = get_connection()
    cursor = conn.cursor()
    # Ensure there is at least one budget row to update
    cursor.execute('INSERT OR IGNORE INTO budget (id, amount, savings_goal, current_savings) VALUES (1, 0, 0, 0)')
    cursor.execute('UPDATE budget SET current_savings = current_savings + ? WHERE id = 1', (amount,))
    conn.commit()
    conn.close()

def get_transactions_by_type(trans_type: str) -> list[Transaction]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, trans_type, amount, category, date FROM transactions WHERE trans_type = ? ORDER BY date DESC', (trans_type,))
    rows = cursor.fetchall()
    conn.close()
    return [Transaction(id=r[0], trans_type=r[1], amount=r[2], category=r[3], date=r[4]) for r in rows]

def get_recent_expenses(limit=5) -> list[Transaction]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, trans_type, amount, category, date FROM transactions WHERE trans_type = "expense" ORDER BY date DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [Transaction(id=r[0], trans_type=r[1], amount=r[2], category=r[3], date=r[4]) for r in rows]

def delete_all_expenses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE trans_type = "expense"')
    conn.commit()
    conn.close()

def delete_expense(expense_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE trans_type = "expense" AND id = ?', (expense_id,))
    conn.commit()
    conn.close()

# --- Goals & Investments ---

def add_goal(name: str, target_amount: float, current_amount: float = 0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO goals (name, target_amount, current_amount) VALUES (?, ?, ?)', (name, target_amount, current_amount))
    conn.commit()
    conn.close()

def get_goals() -> list[Goal]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, target_amount, current_amount FROM goals')
    rows = cursor.fetchall()
    conn.close()
    return [Goal(id=r[0], name=r[1], target_amount=r[2], current_amount=r[3]) for r in rows]

def update_goal_progress(goal_id: int, added_amount: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE goals SET current_amount = current_amount + ? WHERE id = ?', (added_amount, goal_id))
    conn.commit()
    conn.close()

def add_investment(name: str, amount: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO investments (name, amount) VALUES (?, ?)', (name, amount))
    conn.commit()
    conn.close()

def get_total_investments() -> float:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(amount) FROM investments')
    row = cursor.fetchone()
    conn.close()
    return row[0] if row[0] else 0.0

def get_all_investments() -> list[Investment]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, amount FROM investments')
    rows = cursor.fetchall()
    conn.close()
    return [Investment(id=r[0], name=r[1], amount=r[2]) for r in rows]
