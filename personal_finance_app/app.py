import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import (
    initialize_db,
    add_transaction,
    set_budget,
    get_budget,
    get_transactions_by_type,
    get_recent_expenses,
    get_goals,
    get_total_investments,
    add_investment,
    delete_all_expenses,
    delete_expense,
    update_goal_progress,
    get_all_investments,
    add_goal,
    create_user,
    get_all_investments,
    add_goal,
    create_user,
    get_user_by_username,
    add_to_savings
)

app = Flask(__name__)
# In a real app, use a secure random string or os.environ.get('SECRET_KEY')
app.secret_key = 'super_secret_finance_key'

# Initialize the database on startup
initialize_db()

# --- Seed data for demonstration if empty ---
def seed_initial_data():
    if get_budget()['amount'] == 0:
        set_budget(200000, 0)

    incomes = get_transactions_by_type('income')
    if not incomes:
        add_transaction('income', 150000, 'Salary')

    expenses = get_transactions_by_type('expense')
    if not expenses:
        add_transaction('expense', 100000, 'College')
        add_transaction('expense', 8150, 'Groceries')

# Run seed
seed_initial_data()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials. Please try again.")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([full_name, email, mobile, username, password, confirm_password]):
            return render_template('register.html', error="All fields are required.")
            
        if password != confirm_password:
            return render_template('register.html', error="Passwords do not match. Please try again.")
            
        existing_user = get_user_by_username(username)
        if existing_user:
            return render_template('register.html', error="Username already exists. Please choose a different one.")
            
        hashed_password = generate_password_hash(password)
        try:
            create_user(username, full_name, email, mobile, hashed_password)
            return redirect(url_for('login', registered=True))
        except Exception as e:
            return render_template('register.html', error=str(e))
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    """Render the main dashboard."""
    return render_template('index.html')


@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    if not session.get('logged_in'):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    """API endpoint returning all necessary data for the Dashboard."""
    
    # Calculate totals
    incomes = get_transactions_by_type('income')
    total_income = sum(inc.amount for inc in incomes)
    
    expenses = get_transactions_by_type('expense')
    total_expenses = sum(exp.amount for exp in expenses)
    
    budget_data = get_budget()
    budget = budget_data.get('amount', 0)
    savings_goal = budget_data.get('savings_goal', 0)
    total_savings = budget_data.get('current_savings', 0)
    
    total_investments = get_total_investments()

    # Format goals
    goals = get_goals()
    formatted_goals = [
        {
            "id": g.id,
            "name": g.name,
            "target": g.target_amount,
            "current": g.current_amount,
            "percentage": round((g.current_amount / g.target_amount) * 100) if g.target_amount > 0 else 0
        } for g in goals
    ]

    # Format recent expenses (top 5 for dashboard)
    recent_exp = get_recent_expenses(5)
    formatted_recent = [
        {
            "id": e.id,
            "amount": e.amount,
            "category": e.category,
            "date": e.date.split(" ")[0] # extract just YYYY-MM-DD
        } for e in recent_exp
    ]

    # Format ALL expenses for the Reports and Expenses tabs
    formatted_all_expenses = [
        {
            "id": e.id,
            "amount": e.amount,
            "category": e.category,
            "date": e.date.split(" ")[0]
        } for e in expenses
    ]

    # Generate insights
    insights = []
    
    # 1. Budget Alerts
    if total_expenses > budget and budget > 0:
        insights.append({"type": "danger", "message": f"Over Budget! You have exceeded your budget by ₹{total_expenses - budget}."})
    elif budget > 0 and (total_expenses / budget) >= 0.9:
        insights.append({"type": "warning", "message": f"Approaching Budget Limit. You have spent {round((total_expenses/budget)*100)}% of your budget."})

    # 2. Savings Alerts
    if total_savings < 0:
        insights.append({"type": "danger", "message": f"You are running a deficit! Expenses exceed income by ₹{abs(total_savings)}."})
    elif total_savings < savings_goal and savings_goal > 0:
        insights.append({"type": "warning", "message": f"Low Savings! You are ₹{savings_goal - total_savings} away from your savings goal."})
    elif total_savings >= savings_goal and savings_goal > 0:
        insights.append({"type": "success", "message": "Great job! You have reached your monthly savings goal."})
    
    # 3. Expense Insights
    if expenses:
        categories = {}
        for exp in expenses:
            categories[exp.category] = categories.get(exp.category, 0) + exp.amount
        biggest_category = max(categories, key=categories.get)
        pct = round((categories[biggest_category] / total_expenses) * 100) if total_expenses > 0 else 0
        insights.append({"type": "info", "message": f"{biggest_category} is your biggest expense at ₹{categories[biggest_category]} ({pct}% of total)."})

    # Format investments
    all_investments = get_all_investments()
    formatted_investments = [
        {
            "id": inv.id,
            "name": inv.name,
            "amount": inv.amount
        } for inv in all_investments
    ]

    return jsonify({
        "totals": {
            "income": total_income,
            "expenses": total_expenses,
            "budget": budget,
            "savings": total_savings,
            "savings_goal": savings_goal,
            "investments": total_investments
        },
        "goals": formatted_goals,
        "investments": formatted_investments,
        "insights": insights,
        "recent_expenses": formatted_recent,
        "all_expenses": formatted_all_expenses
    })


@app.route('/api/expense', methods=['POST'])
def add_expense_api():
    """API endpoint to add a new expense."""
    data = request.json
    try:
        amount = float(data.get('amount', 0))
        category = data.get('category', 'Uncategorized')
        
        if amount <= 0:
            return jsonify({"status": "error", "message": "Amount must be positive"}), 400
            
        add_transaction('expense', amount, category)
        return jsonify({"status": "success", "message": "Expense added successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/income', methods=['POST'])
def add_income_api():
    """API endpoint to add a new income."""
    data = request.json
    try:
        amount = float(data.get('amount', 0))
        source = data.get('source', 'Salary')
        
        if amount <= 0:
            return jsonify({"status": "error", "message": "Amount must be positive"}), 400
            
        add_transaction('income', amount, source)
        return jsonify({"status": "success", "message": "Income added successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/budget', methods=['POST'])
def update_budget_api():
    """API endpoint to update the monthly budget."""
    data = request.json
    try:
        amount = float(data.get('amount', 0))
        savings_goal = float(data.get('savings_goal', 0))
        if amount < 0 or savings_goal < 0:
            return jsonify({"status": "error", "message": "Budget and Savings Goal cannot be negative"}), 400
            
        set_budget(amount, savings_goal)
        return jsonify({"status": "success", "message": "Budget updated successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/savings/add', methods=['POST'])
def add_savings_api():
    """API endpoint to manually add to savings."""
    data = request.json
    try:
        amount = float(data.get('amount', 0))
        if amount <= 0:
             return jsonify({"status": "error", "message": "Amount must be positive."}), 400
        
        add_to_savings(amount)
        return jsonify({"status": "success", "message": "Savings added successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/expenses/reset', methods=['POST'])
def reset_expenses_api():
    """API endpoint to delete all expenses."""
    try:
        delete_all_expenses()
        return jsonify({"status": "success", "message": "All expenses have been reset"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/expense/<int:expense_id>', methods=['DELETE'])
def delete_expense_api(expense_id):
    """API endpoint to delete a specific expense."""
    if not session.get('logged_in'):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    try:
        delete_expense(expense_id)
        return jsonify({"status": "success", "message": "Expense deleted successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/profile', methods=['GET'])
def get_profile_api():
    """API endpoint to get the logged-in user profile details."""
    if not session.get('logged_in'):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    username = session.get('username')
    user = get_user_by_username(username)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404
        
    return jsonify({
        "status": "success",
        "user": {
            "username": user.get("username"),
            "full_name": user.get("full_name"),
            "email": user.get("email"),
            "mobile": user.get("mobile")
        }
    })


@app.route('/api/goals', methods=['POST'])
def add_goal_api():
    """API endpoint to add a new goal."""
    data = request.json
    try:
        name = data.get('name')
        target = float(data.get('target', 0))
        
        if not name or target <= 0:
            return jsonify({"status": "error", "message": "Valid name and positive target amount required"}), 400
            
        add_goal(name, target)
        return jsonify({"status": "success", "message": "Goal added successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/goals/<int:goal_id>/progress', methods=['POST'])
def add_goal_progress_api(goal_id):
    """API endpoint to add progress to a goal."""
    data = request.json
    try:
        amount = float(data.get('amount', 0))
        if amount <= 0:
            return jsonify({"status": "error", "message": "Amount must be positive"}), 400
            
        update_goal_progress(goal_id, amount)
        return jsonify({"status": "success", "message": "Progress added successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/investments', methods=['POST'])
def add_investment_api():
    """API endpoint to add a new investment."""
    data = request.json
    try:
        name = data.get('name')
        amount = float(data.get('amount', 0))
        
        if not name or amount <= 0:
            return jsonify({"status": "error", "message": "Valid name and positive amount required"}), 400
            
        add_investment(name, amount)
        return jsonify({"status": "success", "message": "Investment added successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/advisor', methods=['GET'])
def get_advisor_recommendations():
    import re
    if not session.get('logged_in'):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
        
    incomes = get_transactions_by_type('income')
    total_income = sum(inc.amount for inc in incomes)
    
    expenses = get_transactions_by_type('expense')
    total_expenses = sum(exp.amount for exp in expenses)
    
    budget_data = get_budget()
    budget = budget_data.get('amount', 0)
    
    total_savings = budget_data.get('current_savings', 0)
    total_investments = get_total_investments()
    
    advice = []
    
    if total_income == 0:
        advice.append("We don't have enough income data to provide a full analysis. Consider adding your monthly income first.")
        return jsonify({"status": "success", "advice": "<p>" + "</p><p>".join(advice) + "</p>"})
        
    savings_rate = (total_savings / total_income) * 100
    
    advice.append(f"**Financial Health Overview:** Your current savings rate is **{savings_rate:.1f}%**.")
    
    if savings_rate < 20:
        advice.append("A general rule of thumb is the 50/30/20 rule, where 20% of your income goes to savings. Try to reduce discretionary expenses to boost your savings.")
    elif savings_rate < 30:
        advice.append("Great job! You are saving a healthy amount. Let's look at ways to grow this money.")
    else:
        advice.append("Excellent! With a high savings rate, you have a wealth-building advantage. You should actively invest the surplus.")
        
    if total_expenses > budget and budget > 0:
        advice.append(f"⚠️ **Budget Alert:** You are currently over budget by ₹{total_expenses - budget}. It is highly recommended to cut unnecessary costs.")
        
    if expenses:
        categories = {}
        for exp in expenses:
            categories[exp.category] = categories.get(exp.category, 0) + exp.amount
        
        highest_category = max(categories, key=categories.get)
        highest_amount = categories[highest_category]
        pct_of_expenses = (highest_amount / total_expenses) * 100 if total_expenses > 0 else 0
        
        advice.append(f"**Expense Breakdown:** Your highest expense category is **{highest_category}** at **₹{highest_amount:.0f}** ({pct_of_expenses:.1f}% of all expenses).")
        if pct_of_expenses > 40:
             advice.append(f"🚨 This is a disproportionately large chunk of your spending! Consider reviewing your {highest_category} expenses in detail to find areas where you can cut back quickly.")
        else:
             advice.append(f"Monitoring your {highest_category} expenses could be the easiest way to free up more money for your savings.")
        
    emergency_fund_target = total_expenses * 6 if total_expenses > 0 else 50000
    if total_savings < emergency_fund_target and total_investments < emergency_fund_target:
        advice.append(f"**Emergency Fund:** Before aggressive investing, secure an emergency fund of at least 6 months of expenses (approx. ₹{emergency_fund_target}). Park this in an FD or a liquid fund.")
    else:
        advice.append("**Emergency Fund:** Your emergency fund looks solid. You can focus more on long-term wealth building.")
    
    advice.append("### Investment Suggestions")
    
    potential_sip = max(0, total_savings * 0.5) 
    
    if potential_sip > 1000:
        advice.append(f"Based on your savings, you could comfortably start an **SIP of around ₹{potential_sip:.0f} per month**.")
        advice.append("**Suggested Allocation (Medium Risk Profile):**")
        advice.append(f"- **Index Funds:** ₹{potential_sip * 0.5:.0f} (e.g., Nifty 50 Index Fund for stable long-term growth.)")
        advice.append(f"- **Flexi-Cap Funds:** ₹{potential_sip * 0.3:.0f} (Managed funds with flexibility across market caps.)")
        advice.append(f"- **Small-Cap Funds:** ₹{potential_sip * 0.2:.0f} (Higher returns but volatile. Good for 7+ years horizon.)")
    else:
        advice.append("You currently have limited surplus for SIPs. Start small, even with ₹500/month in an Index Mutual Fund, and build the habit of investing.")
         
    html_output = ""
    in_list = False
    for line in advice:
        line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
        
        if line.startswith('### '):
            if in_list:
                html_output += "</ul>\n"
                in_list = False
            html_output += f"<h3>{line[4:]}</h3>\n"
        elif line.startswith('- '):
            if not in_list:
                html_output += "<ul>\n"
                in_list = True
            html_output += f"<li>{line[2:]}</li>\n"
        else:
            if in_list:
                html_output += "</ul>\n"
                in_list = False
            html_output += f"<p>{line}</p>\n"
            
    if in_list:
        html_output += "</ul>\n"

    return jsonify({"status": "success", "advice": html_output})


if __name__ == '__main__':
    app.run(debug=True, port=8000)
