// Format currency
const formatCurrency = (amount) => {
    return '₹' + amount.toLocaleString('en-IN');
};

let reportChart = null; // Global chart instance

// Fetch Dashboard Data
const loadDashboard = async () => {
    try {
        const response = await fetch('/api/dashboard');
        const data = await response.json();
        
        // Populate Summary Cards
        document.getElementById('val-expenses').innerText = formatCurrency(data.totals.expenses);
        document.getElementById('val-budget').innerText = formatCurrency(data.totals.budget);
        
        // Handle Over Budget Alert
        const alertBanner = document.getElementById('over-budget-alert');
        const alertText = document.getElementById('over-budget-text');
        if (alertBanner && alertText) {
            if (data.totals.expenses > data.totals.budget && data.totals.budget > 0) {
                const overage = data.totals.expenses - data.totals.budget;
                alertText.innerText = `You have exceeded your monthly budget by ${formatCurrency(overage)}.`;
                alertBanner.style.display = 'flex';
            } else {
                alertBanner.style.display = 'none';
            }
        }
        
        // Update Budget View tab
        const bvt = document.getElementById('budget-view-val');
        if(bvt) bvt.innerText = formatCurrency(data.totals.budget);
        
        const bsv = document.getElementById('budget-savings-val');
        if(bsv) bsv.innerText = formatCurrency(data.totals.savings_goal);

        // Update Savings view tab
        const vals = document.getElementById('val-savings');
        if(vals) vals.innerText = formatCurrency(data.totals.savings);
        
        const valsg = document.getElementById('val-savings-goal');
        if(valsg) valsg.innerText = `Target: ${formatCurrency(data.totals.savings_goal)}`;
        
        // Update Reports view macro summary headers
        const rIn = document.getElementById('report-val-income');
        if(rIn) rIn.innerText = formatCurrency(data.totals.income);
        
        const rEx = document.getElementById('report-val-expenses');
        if(rEx) rEx.innerText = formatCurrency(data.totals.expenses);
        
        const rSa = document.getElementById('report-val-savings');
        if(rSa) rSa.innerText = formatCurrency(data.totals.savings);
        
        const rInv = document.getElementById('report-val-investments');
        if(rInv) rInv.innerText = formatCurrency(data.totals.investments);
        
        const salert = document.getElementById('savings-alert');
        if(salert) {
            if(data.totals.savings >= data.totals.savings_goal && data.totals.savings_goal > 0) {
                salert.innerHTML = `<span style="color: #00B894; font-weight: 600;"><i class="fas fa-check-circle"></i> Awesome! You've met or exceeded your savings goal!</span>`;
            } else if (data.totals.savings < 0) {
                salert.innerHTML = `<span style="color: #FF7675; font-weight: 600;"><i class="fas fa-exclamation-circle"></i> You are currently running a deficit. Your expenses exceed your income!</span>`;
            } else if (data.totals.savings_goal > 0) {
                const diff = data.totals.savings_goal - data.totals.savings;
                salert.innerHTML = `<span style="color: #E17055; font-weight: 600;">You are ${formatCurrency(diff)} away from reaching your savings goal.</span>`;
            } else {
                salert.innerHTML = '';
            }
        }
        
        // Populate Recent Expenses
        const recentTbody = document.getElementById('recent-expenses-body');
        const allTbody = document.getElementById('all-expenses-body');
        const reportTbody = document.getElementById('report-expenses-body');
        
        if (data.recent_expenses.length === 0) {
            recentTbody.innerHTML = '<tr><td colspan="3" class="text-center">No recent expenses</td></tr>';
            if (allTbody) allTbody.innerHTML = '<tr><td colspan="3" class="text-center">No expenses recorded yet.</td></tr>';
            if (reportTbody) reportTbody.innerHTML = '<tr><td colspan="3" class="text-center">No expenses recorded yet.</td></tr>';
        } else {
            let recentHTML = '';
            data.recent_expenses.forEach(exp => {
                recentHTML += `
                        <tr>
                            <td>${exp.date}</td>
                            <td>${exp.category}</td>
                            <td class="text-red" style="display:flex; justify-content:space-between; align-items:center;">
                                <strong>${formatCurrency(exp.amount)}</strong>
                                <button class="btn btn-sm bg-red" style="color:white; padding: 4px 8px;" onclick="deleteExpense(${exp.id})" title="Delete Expense"><i class="fas fa-trash"></i></button>
                            </td>
                        </tr>
                `;
            });
            recentTbody.innerHTML = recentHTML;
            
            // Populate All Expenses view
            if(allTbody && data.all_expenses) {
                let allHTML = '';
                data.all_expenses.forEach(exp => {
                    allHTML += `
                        <tr>
                            <td>${exp.date}</td>
                            <td>${exp.category}</td>
                            <td class="text-red" style="display:flex; justify-content:space-between; align-items:center;">
                                <strong>${formatCurrency(exp.amount)}</strong>
                                <button class="btn btn-sm bg-red" style="color:white; padding: 4px 8px;" onclick="deleteExpense(${exp.id})" title="Delete Expense"><i class="fas fa-trash"></i></button>
                            </td>
                        </tr>
                    `;
                });
                allTbody.innerHTML = allHTML;
            }

            // Populate Reports View (Category Grouping)
            if(reportTbody && data.all_expenses) {
                const categoryTotals = {};
                let grandTotal = 0;
                
                data.all_expenses.forEach(exp => {
                    categoryTotals[exp.category] = (categoryTotals[exp.category] || 0) + exp.amount;
                    grandTotal += exp.amount;
                });

                let reportHTML = '';
                for (const [category, total] of Object.entries(categoryTotals)) {
                    const percentage = grandTotal > 0 ? ((total / grandTotal) * 100).toFixed(1) : 0;
                    reportHTML += `
                        <tr>
                            <td><strong>${category}</strong></td>
                            <td class="text-red"><strong>${formatCurrency(total)}</strong></td>
                            <td>${percentage}%</td>
                        </tr>
                    `;
                }
                
                if(Object.keys(categoryTotals).length === 0) {
                    reportHTML = '<tr><td colspan="3" class="text-center">No expenses recorded yet.</td></tr>';
                }
                
                reportTbody.innerHTML = reportHTML;
                
                // Update the chart
                updateReportChart(categoryTotals);
            }
        }

        // Populate Goals View
        const goalsContainer = document.getElementById('goals-container');
        if (goalsContainer && data.goals) {
            if (data.goals.length === 0) {
                goalsContainer.innerHTML = '<div class="card"><p class="text-center text-muted" style="margin: 0;">No goals created yet. Click "Add Goal" to start.</p></div>';
            } else {
                let goalsHTML = `<div class="card full-width p-0"><div style="padding: 20px;">`;
                data.goals.forEach(g => {
                    goalsHTML += `
                        <div class="goal-item" style="margin-bottom: 25px;">
                            <div class="goal-info">
                                <div class="goal-name">
                                    <i class="fas fa-bullseye text-pink"></i>
                                    ${g.name}
                                </div>
                                <div class="goal-pct">${g.percentage}%</div>
                            </div>
                            <div class="progress-bar-container">
                                <div class="progress-bar" style="width: ${g.percentage}%"></div>
                            </div>
                            <div class="goal-amounts" style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                                <div>
                                    <span class="text-main" style="font-weight: 600;">${formatCurrency(g.current)}</span> 
                                    <span class="text-muted">of ${formatCurrency(g.target)}</span>
                                </div>
                                <button class="btn btn-sm btn-outline-purple" onclick="openAddProgressModal(${g.id})"><i class="fas fa-plus"></i> Add Funds</button>
                            </div>
                        </div>
                    `;
                });
                goalsHTML += `</div></div>`;
                goalsContainer.innerHTML = goalsHTML;
            }
        }

        // Populate Investments View
        const invTbody = document.getElementById('investments-body');
        if (invTbody && data.investments) {
            if (data.investments.length === 0) {
                invTbody.innerHTML = '<tr><td colspan="2" class="text-center">No investments added yet</td></tr>';
            } else {
                let invHTML = '';
                data.investments.forEach(inv => {
                    invHTML += `
                        <tr>
                            <td><strong>${inv.name}</strong></td>
                            <td class="text-green"><strong>${formatCurrency(inv.amount)}</strong></td>
                        </tr>
                    `;
                });
                invTbody.innerHTML = invHTML;
            }
        }

        // Populate Notifications
        const notifBadge = document.getElementById('notif-badge');
        const notifList = document.getElementById('notif-list');
        if (notifBadge && notifList && data.insights) {
            if (data.insights.length > 0) {
                notifBadge.innerText = data.insights.length;
                notifBadge.style.display = 'block';
                
                let notifHTML = '';
                data.insights.forEach(ins => {
                    let iconCode = `<i class="fas fa-info-circle text-blue"></i>`;
                    let bgColor = `transparent`;
                    
                    if (ins.type === 'danger') {
                        iconCode = `<i class="fas fa-exclamation-triangle text-red"></i>`;
                        bgColor = `rgba(255, 118, 117, 0.05)`;
                    } else if (ins.type === 'warning') {
                        iconCode = `<i class="fas fa-exclamation-circle text-orange"></i>`;
                        bgColor = `rgba(225, 112, 85, 0.05)`;
                    } else if (ins.type === 'success') {
                        iconCode = `<i class="fas fa-check-circle text-green"></i>`;
                    }
                    
                    notifHTML += `
                        <div style="padding: 15px; border-bottom: 1px solid #eee; display: flex; gap: 12px; align-items: start; background: ${bgColor}; transition: background 0.2s;">
                            <div style="margin-top: 2px; font-size: 1.1rem;">${iconCode}</div>
                            <div style="font-size: 0.85rem; color: var(--text-main); line-height: 1.4;">${ins.message}</div>
                        </div>
                    `;
                });
                notifList.innerHTML = notifHTML;
            } else {
                notifBadge.style.display = 'none';
                notifList.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-muted); font-size: 0.9rem;">No new notifications!</div>';
            }
        }

    } catch (error) {
        console.error("Error loading dashboard data:", error);
    }
};

// Modal Logic
const incomeModal = document.getElementById('incomeModal');
const savingsModal = document.getElementById('savingsModal');
const expenseModal = document.getElementById('expenseModal');
const addGoalModal = document.getElementById('addGoalModal');
const addProgressModal = document.getElementById('addProgressModal');
const addInvestmentModal = document.getElementById('addInvestmentModal');

function openIncomeModal() { incomeModal.style.display = 'block'; }
function closeIncomeModal() { incomeModal.style.display = 'none'; }

function openSavingsModal() { savingsModal.style.display = 'block'; }
function closeSavingsModal() { savingsModal.style.display = 'none'; }

function openExpenseModal() { expenseModal.style.display = 'block'; }
function closeExpenseModal() { expenseModal.style.display = 'none'; }

function openAddGoalModal() { addGoalModal.style.display = 'block'; }
function closeAddGoalModal() { addGoalModal.style.display = 'none'; }

function openAddProgressModal(goalId) {
    document.getElementById('progressGoalId').value = goalId;
    addProgressModal.style.display = 'block';
}
function closeAddProgressModal() { addProgressModal.style.display = 'none'; }

function openAddInvestmentModal() { addInvestmentModal.style.display = 'block'; }
function closeAddInvestmentModal() { addInvestmentModal.style.display = 'none'; }

async function openProfileModal() {
    try {
        const response = await fetch('/api/profile');
        const result = await response.json();
        if (result.status === 'success') {
            document.getElementById('profileFullName').innerText = result.user.full_name || 'N/A';
            document.getElementById('profileUsername').innerText = result.user.username;
            document.getElementById('profileEmail').innerText = result.user.email || 'N/A';
            document.getElementById('profileMobile').innerText = result.user.mobile || 'N/A';
            document.getElementById('profileModal').style.display = 'block';
        } else {
            alert("Error loading profile: " + result.message);
        }
    } catch (error) {
        console.error("Error fetching profile:", error);
    }
}

function closeProfileModal() {
    const modal = document.getElementById('profileModal');
    if (modal) modal.style.display = 'none';
}

// Toggle AI Advisor Panel
function toggleAIPanel() {
    const panel = document.getElementById('ai-advisor-panel');
    if (panel.style.display === 'none' || panel.style.display === '') {
        panel.style.display = 'flex';
    } else {
        panel.style.display = 'none';
    }
}

// Toggle Notifications Dropdown
function toggleNotifications() {
    const dropdown = document.getElementById('notif-dropdown');
    if (dropdown.style.display === 'none' || dropdown.style.display === '') {
        dropdown.style.display = 'block';
    } else {
        dropdown.style.display = 'none';
    }
}

// Close modal or dropdown when clicking outside
window.onclick = function(event) {
    if (event.target == incomeModal) {
        closeIncomeModal();
    }
    if (event.target == savingsModal) {
        closeSavingsModal();
    }
    if (event.target == expenseModal) {
        closeExpenseModal();
    }
    if (event.target == addGoalModal) {
        closeAddGoalModal();
    }
    if (event.target == addProgressModal) {
        closeAddProgressModal();
    }
    if (event.target == addInvestmentModal) {
        closeAddInvestmentModal();
    }
    
    const profileModal = document.getElementById('profileModal');
    if (profileModal && event.target == profileModal) {
        closeProfileModal();
    }
    
    // Close notifications if clicking outside
    const notifWrapper = document.querySelector('.notification-wrapper');
    const notifDropdown = document.getElementById('notif-dropdown');
    if (notifWrapper && notifDropdown) {
        if (!notifWrapper.contains(event.target)) {
            notifDropdown.style.display = 'none';
        }
    }

    // Close AI Panel if clicking outside (excluding the FAB)
    const aiPanel = document.getElementById('ai-advisor-panel');
    const aiFab = document.querySelector('.ai-fab');
    if (aiPanel && aiFab && aiPanel.style.display === 'flex') {
        if (!aiPanel.contains(event.target) && !aiFab.contains(event.target)) {
            aiPanel.style.display = 'none';
        }
    }
}

// Handle Add Income Form Submit
document.getElementById('incomeForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const amount = document.getElementById('incAmount').value;
    const source = document.getElementById('incSource').value;
    
    try {
        const response = await fetch('/api/income', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ amount, source })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            closeIncomeModal();
            document.getElementById('incomeForm').reset();
            // Reload dashboard to show new data
            loadDashboard();
        } else {
            alert("Error: " + result.message);
        }
    } catch (error) {
        console.error("Error adding income:", error);
    }
});

// Handle Add Savings Form Submit
document.getElementById('savingsForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const amount = document.getElementById('savAmount').value;
    
    try {
        const response = await fetch('/api/savings/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ amount })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            closeSavingsModal();
            document.getElementById('savingsForm').reset();
            loadDashboard();
        } else {
            alert("Error: " + result.message);
        }
    } catch (error) {
        console.error("Error adding savings:", error);
    }
});

// Handle Form Submit
document.getElementById('expenseForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const amount = document.getElementById('expAmount').value;
    const category = document.getElementById('expCategory').value;
    
    try {
        const response = await fetch('/api/expense', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ amount, category })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            closeExpenseModal();
            document.getElementById('expenseForm').reset();
            // Reload dashboard to show new data
            loadDashboard();
        } else {
            alert("Error: " + result.message);
        }
    } catch (error) {
        console.error("Error adding expense:", error);
    }
});

// Handle Add Goal Submit
document.getElementById('addGoalForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('goalName').value;
    const target = document.getElementById('goalTarget').value;
    
    try {
        const response = await fetch('/api/goals', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, target })
        });
        const result = await response.json();
        
        if (result.status === 'success') {
            closeAddGoalModal();
            document.getElementById('addGoalForm').reset();
            loadDashboard();
        } else {
            alert("Error: " + result.message);
        }
    } catch (error) {
        console.error("Error adding goal:", error);
    }
});

// Handle Add Progress Submit
document.getElementById('addProgressForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const goalId = document.getElementById('progressGoalId').value;
    const amount = document.getElementById('progressAmount').value;
    
    try {
        const response = await fetch(`/api/goals/${goalId}/progress`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount })
        });
        const result = await response.json();
        
        if (result.status === 'success') {
            closeAddProgressModal();
            document.getElementById('addProgressForm').reset();
            loadDashboard();
        } else {
            alert("Error: " + result.message);
        }
    } catch (error) {
        console.error("Error adding progress:", error);
    }
});

// Handle Add Investment Submit
document.getElementById('addInvestmentForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('invName').value;
    const amount = document.getElementById('invAmount').value;
    
    try {
        const response = await fetch('/api/investments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, amount })
        });
        const result = await response.json();
        
        if (result.status === 'success') {
            closeAddInvestmentModal();
            document.getElementById('addInvestmentForm').reset();
            loadDashboard();
        } else {
            alert("Error: " + result.message);
        }
    } catch (error) {
        console.error("Error adding investment:", error);
    }
});

// Handle Budget Update
const budgetForm = document.getElementById('budgetForm');
if(budgetForm) {
    budgetForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const newBudgetAmount = document.getElementById('newBudget').value;
        const newSavingsGoal = document.getElementById('newSavingsGoal').value;
        
        try {
            const response = await fetch('/api/budget', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ amount: newBudgetAmount, savings_goal: newSavingsGoal })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                document.getElementById('budgetForm').reset();
                alert("Budget updated successfully!");
                // Reload dashboard to reflect new budget globally
                loadDashboard();
            } else {
                alert("Error: " + result.message);
            }
        } catch (error) {
            console.error("Error setting budget:", error);
        }
    });
}

// Load dashboard on startup
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
    
    // Setup Navigation Listeners
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = item.getAttribute('data-target');
            if(targetId) {
                switchTab(targetId);
            }
        });
    });
});

// Reset All Expenses Logic
async function resetAllExpenses() {
    if (confirm("Are you sure you want to delete ALL expenses? This cannot be undone.")) {
        try {
            const response = await fetch('/api/expenses/reset', {
                method: 'POST'
            });
            const result = await response.json();
            
            if (result.status === 'success') {
                alert("All expenses have been reset.");
                loadDashboard();
            } else {
                alert("Error: " + result.message);
            }
        } catch (error) {
            console.error("Error resetting expenses:", error);
        }
    }
}

// Delete Single Expense Logic
async function deleteExpense(expenseId) {
    if (confirm("Are you sure you want to delete this specific expense?")) {
        try {
            const response = await fetch(`/api/expense/${expenseId}`, {
                method: 'DELETE'
            });
            const result = await response.json();
            
            if (result.status === 'success') {
                loadDashboard();
            } else {
                alert("Error: " + result.message);
            }
        } catch (error) {
            console.error("Error deleting specific expense:", error);
        }
    }
}

// Switch Tabs Logic
function switchTab(targetId) {
    // Hide all sections
    const sections = document.querySelectorAll('.view-section');
    sections.forEach(sec => sec.style.display = 'none');
    
    // Show target section
    const targetSec = document.getElementById(targetId);
    if(targetSec) targetSec.style.display = 'block';
    
    // Update active class on nav
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => item.classList.remove('active'));
    
    const activeNav = document.querySelector(`.nav-item[data-target="${targetId}"]`);
    if(activeNav) activeNav.classList.add('active');
}

// Generate AI Advice
async function generateAdvice() {
    const btn = document.getElementById('btn-generate-advice');
    const content = document.getElementById('advisor-content');
    
    // Show loading state
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing Data...';
    content.innerHTML = `
        <div class="text-center" style="margin-top: 50px;">
            <i class="fas fa-robot fa-spin" style="font-size: 3rem; color: #FF7675; margin-bottom: 15px;"></i>
            <h3>Analyzing your financial profile...</h3>
            <p class="text-muted">Calculating savings rate, checking budget limits, and generating mutual fund suggestions...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/api/advisor');
        const result = await response.json();
        
        if (result.status === 'success') {
            // Add a small delay for "AI thinking" effect
            setTimeout(() => {
                content.innerHTML = `
                    <div style="background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: left;">
                        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 15px;">
                            <i class="fas fa-robot" style="font-size: 2rem; color: #FF7675;"></i>
                            <h2 style="margin: 0; color: #2d3436;">AI Recommendation</h2>
                        </div>
                        <div style="line-height: 1.6; color: #2d3436; font-size: 1.05rem;" class="advice-html">
                            ${result.advice}
                        </div>
                    </div>
                `;
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-magic"></i> Generate Fresh Advice';
            }, 1500);
        } else {
            content.innerHTML = `<div style="color: red; padding: 20px; border: 1px solid red; border-radius: 8px; background: #fff0f0; margin-top: 50px;">Error: ${result.message}</div>`;
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-magic"></i> Try Again';
        }
    } catch (error) {
        console.error("Error generating advice:", error);
        content.innerHTML = `<div style="color: red; padding: 20px; border: 1px solid red; border-radius: 8px; background: #fff0f0; margin-top: 50px;">An unexpected error occurred. Please try again later.</div>`;
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-magic"></i> Try Again';
    }
}

// Update Spending Pie Chart
function updateReportChart(categoryData) {
    const ctx = document.getElementById('spendingChart')?.getContext('2d');
    if (!ctx) return;

    const labels = Object.keys(categoryData);
    const data = Object.values(categoryData);
    
    // Aesthetic colors matching our theme
    const colors = [
        '#6C5CE7', // Primary Purple
        '#FF7675', // Red
        '#00B894', // Green
        '#0984E3', // Blue
        '#E17055', // Orange
        '#FD79A8', // Pink
        '#FDCB6E', // Yellow
        '#A29BFE'  // Light Purple
    ];

    if (reportChart) {
        reportChart.data.labels = labels;
        reportChart.data.datasets[0].data = data;
        reportChart.update();
    } else {
        reportChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors.slice(0, labels.length),
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            font: { size: 12, family: "'Inter', sans-serif" }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                if (label) label += ': ';
                                if (context.parsed !== null) {
                                    label += formatCurrency(context.parsed);
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }
}

// Export Data to CSV
async function exportToCSV() {
    try {
        const response = await fetch('/api/dashboard');
        const data = await response.json();
        
        let csvContent = "data:text/csv;charset=utf-8,";
        
        // Header
        csvContent += "Financial Report Summary\n";
        csvContent += `Generated on,${new Date().toLocaleString()}\n\n`;
        
        // Totals Section
        csvContent += "METRIC,VALUE\n";
        csvContent += `Total Income,${data.totals.income}\n`;
        csvContent += `Total Expenses,${data.totals.expenses}\n`;
        csvContent += `Current Savings,${data.totals.savings}\n`;
        csvContent += `Total Investments,${data.totals.investments}\n\n`;
        
        // Transaction History
        csvContent += "TRANSACTION HISTORY\n";
        csvContent += "DATE,CATEGORY,AMOUNT\n";
        
        data.all_expenses.forEach(exp => {
            csvContent += `${exp.date},${exp.category},${exp.amount}\n`;
        });
        
        // Download Logic
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `finance_report_${new Date().toISOString().split('T')[0]}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
    } catch (error) {
        console.error("Error exporting CSV:", error);
        alert("Failed to export data. Please try again.");
    }
}

