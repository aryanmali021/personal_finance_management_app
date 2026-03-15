# Personal Finance Management App

A command-line based personal finance manager written in Python. It helps you track your income, expenses, budget, and overall savings using a local SQLite database for storage.

## Requirements
- Python 3.6+

## How to Run
1. Open your terminal or command prompt.
2. Navigate to this directory (`c:\Users\Aryan\OneDrive\Documents\arya hack verse 2.0\personal_finance_app`).
3. Run the application by executing:
   ```bash
   python main.py
   ```

## Example Run

When you start the application, you will see a menu like this:

```
=== Personal Finance Management App ===
1. Add Income
2. Add Expense
3. Set Monthly Budget
4. View Expenses
5. View Summary
6. View Savings
7. Exit
=======================================
Enter your choice (1-7): 3
Enter monthly budget amount: 1000
Success: Monthly budget set to $1000.00.

=== Personal Finance Management App ===
...
Enter your choice (1-7): 1
Enter income amount: 2500
Enter income source (e.g., Salary, Bonus): Salary
Success: Added income of $2500.00 from Salary.

=== Personal Finance Management App ===
...
Enter your choice (1-7): 2
Enter expense amount: 150
Enter expense category (e.g., Food, Travel, Bills): Food
Success: Added expense of $150.00 for Food.

=== Personal Finance Management App ===
...
Enter your choice (1-7): 5

--- Monthly Summary Report ---
Total Income:        $2500.00
Total Expenses:      $150.00
Current Savings:     $2350.00
------------------------------
Monthly Budget:      $1000.00
Remaining Budget:    $850.00
------------------------------
```

## Features
- **Data Persistence**: Uses a local `finance_manager.db` SQLite database to save your inputs so you never lose your data.
- **Budget Warning**: If you add an expense that causes your total expenses to exceed your monthly budget, the app will issue a warning.
- **Modular Code**: Separated into `models.py`, `database.py`, `finance_manager.py` and `main.py` for easy maintenance.
