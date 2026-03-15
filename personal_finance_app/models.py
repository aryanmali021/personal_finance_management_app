from dataclasses import dataclass

@dataclass
class Transaction:
    """Represents a financial transaction (income or expense)."""
    id: int
    trans_type: str  # 'income' or 'expense'
    amount: float
    category: str
    date: str

@dataclass
class Budget:
    """Represents the monthly budget limit."""
    amount: float
    savings_goal: float = 0.0

@dataclass
class Goal:
    """Represents a financial goal."""
    id: int
    name: str
    target_amount: float
    current_amount: float

@dataclass
class Investment:
    """Represents an investment."""
    id: int
    name: str
    amount: float
