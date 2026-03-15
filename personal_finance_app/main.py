"""
main.py
The main entry point for the Finance Application, provides the CLI interface.
"""
import sys
from finance_manager import FinanceManager

def display_menu():
    print("\n=== Personal Finance Management App ===")
    print("1. Add Income")
    print("2. Add Expense")
    print("3. Set Monthly Budget")
    print("4. View Expenses")
    print("5. View Summary")
    print("6. View Savings")
    print("7. Exit")
    print("=======================================")

def main():
    try:
        manager = FinanceManager()
    except Exception as e:
        print(f"Failed to initialize the application: {e}")
        sys.exit(1)
        
    while True:
        display_menu()
        choice = input("Enter your choice (1-7): ").strip()
        
        try:
            if choice == '1':
                amount_str = input("Enter income amount: ")
                source = input("Enter income source (e.g., Salary, Bonus): ")
                amount = float(amount_str)
                manager.add_income(amount, source)
                
            elif choice == '2':
                amount_str = input("Enter expense amount: ")
                category = input("Enter expense category (e.g., Food, Travel, Bills): ")
                amount = float(amount_str)
                manager.add_expense(amount, category)
                
            elif choice == '3':
                amount_str = input("Enter monthly budget amount: ")
                amount = float(amount_str)
                manager.set_budget(amount)
                
            elif choice == '4':
                manager.view_expenses()
                
            elif choice == '5':
                manager.view_summary()
                
            elif choice == '6':
                manager.view_savings()
                
            elif choice == '7':
                print("Thank you for using the Personal Finance Management App. Goodbye!")
                sys.exit(0)
                
            else:
                print("Invalid choice. Please enter a number between 1 and 7.")
                
        except ValueError as e:
            # Handle float conversion errors specifically
            if "could not convert string to float" in str(e):
                print("Error: Please enter a valid number for the amount.")
            else:
                print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
