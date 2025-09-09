
from dataclasses import dataclass, field

@dataclass
class Account:
    id: str
    kind: str   # savings/checking/credit
    balance: float

@dataclass
class Customer:
    user_id: str
    name: str
    accounts: dict = field(default_factory=dict)  # kind -> Account

class MockBankDB:
    """Tiny in-memory mock DB with one demo customer."""
    def __init__(self):
        self.customer = Customer(
            user_id="user001",
            name="Akhilesh",
            accounts={
                "savings": Account(id="1234", kind="savings", balance=2000.0),
                "checking": Account(id="4532", kind="checking", balance=2000.0),
            },
        )

    # helpers
    def mask(self, acc: Account) -> str:
        return f"{acc.kind}(****{acc.id})"

    def get_account(self, kind_or_id: str) -> Account | None:
        kind_or_id = str(kind_or_id).lower()
        # by kind
        if kind_or_id in self.customer.accounts:
            return self.customer.accounts[kind_or_id]
        # by id
        for acc in self.customer.accounts.values():
            if acc.id == kind_or_id or acc.id.endswith(kind_or_id):
                return acc
        return None

    # banking ops
    def balance(self, kind_or_id: str) -> float | None:
        acc = self.get_account(kind_or_id)
        return acc.balance if acc else None

    def transfer(self, from_acc: str, to_acc: str, amount: float) -> dict:
        src = self.get_account(from_acc)
        dst = self.get_account(to_acc)
        if not src or not dst:
            return {"ok": False, "error": "Invalid account(s)."}
        if amount <= 0:
            return {"ok": False, "error": "Amount must be positive."}
        if src.balance < amount:
            return {"ok": False, "error": "Insufficient funds."}
        src.balance -= amount
        dst.balance += amount
        return {
            "ok": True,
            "from": self.mask(src),
            "to": self.mask(dst),
            "amount": amount,
            "from_balance": src.balance,
            "to_balance": dst.balance,
        }

    def account_info(self, kind_or_id: str) -> dict | None:
        acc = self.get_account(kind_or_id)
        if not acc:
            return None
        return {
            "id": acc.id,
            "kind": acc.kind,
            "balance": acc.balance,
        }
    
    def deposit(self, to_acc: str, amount: float) -> dict:
        acc = self.get_account(to_acc)
        if not acc:
            return {"ok": False, "error": "Invalid account."}
        if amount <= 0:
            return {"ok": False, "error": "Amount must be positive."}
        acc.balance += amount
        return {
            "ok": True,
            "to": self.mask(acc),
            "amount": amount,
            "new_balance": acc.balance,
        }

