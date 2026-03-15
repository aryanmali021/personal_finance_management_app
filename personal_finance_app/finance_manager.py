"""
finance_manager.py
Contains the business logic for the Finance Application.
"""
from database import (
    initialize_db, 
    add_transaction, 
    set_budget, 
    get_budget, 
    get_transactions_by_type
)

class FinanceManager:
    def __init__(self):
        # Ensure database is initialized
        initialize_db()

    def add_income(self, amount: float, source: str):
        """Adds an income record."""
        if amount <= 0:
            raise ValueError("Income amount must be positive.")
        add_transaction('income', amount, source)
        print(f"Success: Added income of ${amount:.2f} from {source}.")

    def add_expense(self, amount: float, category: str):
        """Adds an expense record and checks against budget."""
        if amount <= 0:
            raise ValueError("Expense amount must be positive.")
        
        add_transaction('expense', amount, category)
        print(f"Success: Added expense of ${amount:.2f} for {category}.")
        
        # Check budget warning
        budget = self.get_monthly_budget()
        if budget > 0:
            total_expenses = self.get_total_expenses()
            if total_expenses > budget:
                print(f"*** WARNING: You have exceeded your monthly budget by ${total_expenses - budget:.2f} ***")

    def set_budget(self, amount: float):
        """Sets the monthly budget limit."""
        if amount < 0:
            raise ValueError("Budget cannot be negative.")
        set_budget(amount)
        print(f"Success: Monthly budget set to ${amount:.2f}.")

    def get_monthly_budget(self) -> float:
        """Returns the current monthly budget."""
        return get_budget()

    def get_total_income(self) -> float:
        """Calculates total income."""
        incomes = get_transactions_by_type('income')
        return sum(inc.amount for inc in incomes)

    def get_total_expenses(self) -> float:
        """Calculates total expenses."""
        expenses = get_transactions_by_type('expense')
        return sum(exp.amount for exp in expenses)

    def view_expenses(self):
        """Displays all expenses."""
        expenses = get_transactions_by_type('expense')
        if not expenses:
            print("No expenses recorded yet.")
            return

        print("\n--- Expense List ---")
        for exp in expenses:
            print(f"ID: {exp.id} | Date: {exp.date} | Category: {exp.category} | Amount: ${exp.amount:.2f}")
        print("--------------------")

    def view_summary(self):
        """Displays a summary report (budget, expenses, remaining, income, savings)."""
        budget = self.get_monthly_budget()
        total_income = self.get_total_income()
        total_expenses = self.get_total_expenses()
        remaining_budget = budget - total_expenses
        savings = total_income - total_expenses

        print("\n--- Monthly Summary Report ---")
        print(f"Total Income:        ${total_income:.2f}")
        print(f"Total Expenses:      ${total_expenses:.2f}")
        print(f"Current Savings:     ${savings:.2f}")
        print("------------------------------")
        print(f"Monthly Budget:      ${budget:.2f}")
        
        if budget > 0:
            if remaining_budget >= 0:
                print(f"Remaining Budget:    ${remaining_budget:.2f}")
            else:
                print(f"Budget Exceeded by:  ${abs(remaining_budget):.2f}")
        else:
            print("Remaining Budget:    No budget set.")
        print("------------------------------")

    def view_savings(self):
        """Displays total savings."""
        total_income = self.get_total_income()
        total_expenses = self.get_total_expenses()
        savings = total_income - total_expenses
        
        print("\n--- Savings Report ---")
        print(f"Total Income:   ${total_income:.2f}")
        print(f"Total Expenses: ${total_expenses:.2f}")
        print(f"Net Savings:    ${savings:.2f}")
        print("----------------------")
        if savings < 0:
            print("Watch out! You are spending more than you earn.")
        elif savings > 0:
            print("Great job! You have positive savings.")
