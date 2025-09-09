
from dataclasses import dataclass, field
from typing import Optional
from bank_core import MockBankDB
from nlu import parse, INTENTS

@dataclass
class DialogueState:
    current_intent: Optional[str] = None
    slots: dict = field(default_factory=dict)

class DialogueManager:
    def __init__(self, db: MockBankDB | None = None):
        self.db = db or MockBankDB()
        self.state = DialogueState()

    def reset(self):
        self.state = DialogueState()

    def handle(self, user_text: str) -> dict:
        nlu = parse(user_text)

        # If the new intent has decent confidence, switch
        if nlu["confidence"] >= 0.25 and nlu["intent"] != "fallback":
            self.state.current_intent = nlu["intent"]

        # merge slots
        self.state.slots.update(nlu["entities"])

        if self.state.current_intent == "transfer_money":
            return self._handle_transfer(nlu)
        elif self.state.current_intent == "check_balance":
            return self._handle_balance(nlu)
        elif self.state.current_intent == "account_info":
            return self._handle_info(nlu)
        elif self.state.current_intent == "deposit_money":
            return self._handle_deposit(nlu)
        elif self.state.current_intent == "get_branch_details":
            return self._handle_branch_details(nlu)
        elif self.state.current_intent == "get_interest_rate":
            return self._handle_interest_rate(nlu)
        elif self.state.current_intent == "create_account":
            return self._handle_create_account(nlu)
        elif self.state.current_intent == "lost_card":
            return self._handle_lost_card(nlu)
        elif self.state.current_intent == "apply_loan":
            return self._handle_apply_loan(nlu)
        elif self.state.current_intent == "check_history":
            return self._handle_check_history(nlu)
        elif self.state.current_intent == "apply_card":
            return self._handle_apply_card(nlu)
        elif self.state.current_intent == "close_account":
            return self._handle_close_account(nlu)
        elif nlu["intent"] == "greet":
            return {"text": "Hello! I can help with transfers and balances. What would you like to do?", "nlu": nlu}
        elif nlu["intent"] == "goodbye":
            self.reset()
            return {"text": "Goodbye! 👋", "nlu": nlu}        
        else:
            return {"text": "Sorry, I didn't catch that. You can say: 'transfer $100 from savings to checking' or 'check balance on savings'.", "nlu": nlu}

    # --- Handlers
    def _need(self, *keys):
        missing = [k for k in keys if k not in self.state.slots]
        return missing

    def _handle_transfer(self, nlu) -> dict:
        missing = self._need("amount", "from_account", "to_account")
        if missing:
            prompts = {
                "amount": "How much would you like to transfer?",
                "from_account": "Which account are you sending **from** (savings/checking)?",
                "to_account": "Which account are you sending **to** (kind or last 4 digits)?",
            }
            ask = prompts[missing[0]]
            return {"text": ask, "nlu": nlu, "need": missing}

        result = self.db.transfer(
            self.state.slots["from_account"],
            self.state.slots["to_account"],
            float(self.state.slots["amount"]),
        )
        if not result["ok"]:
            return {"text": f"Transfer failed: {result['error']}", "nlu": nlu}

        # Clear transfer slots to end the task
        for k in ["amount", "from_account", "to_account"]:
            self.state.slots.pop(k, None)
        self.state.current_intent = None

        return {
            "text": (
                f"Transferred ${result['amount']:.2f} from {result['from']} to {result['to']}."
                f" New balances — {result['from'].split('(')[0]}: ${result['from_balance']:.2f},"
                f" {result['to'].split('(')[0]}: ${result['to_balance']:.2f}."
            ),
            "nlu": nlu,
        }

    def _handle_balance(self, nlu) -> dict:
        acc = self.state.slots.get("account")
        if not acc:
            return {"text": "Which account? (savings/checking or last 4 digits)", "nlu": nlu}
        bal = self.db.balance(acc)
        if bal is None:
            return {"text": "I couldn't find that account. Try 'savings' or 'checking 4532'.", "nlu": nlu}
        self.state.current_intent = None
        self.state.slots.pop("account", None)
        return {"text": f"The current balance for {acc} is ${bal:.2f}.", "nlu": nlu}

    def _handle_info(self, nlu) -> dict:
        acc = self.state.slots.get("account")
        if not acc:
            return {"text": "Which account do you want info on? (savings/checking or last 4 digits)", "nlu": nlu}
        info = self.db.account_info(acc)
        if not info:
            return {"text": "I couldn't find that account. Try 'savings' or 'checking 4532'.", "nlu": nlu}
        self.state.current_intent = None
        self.state.slots.pop("account", None)
        return {
            "text": f"Account {info['kind']} (****{info['id']}) — Balance: ${info['balance']:.2f}.",
            "nlu": nlu
        }
    
    def _handle_deposit(self, nlu) -> dict:
        missing = self._need("amount", "account")
        if missing:
            prompts = {
                "amount": "How much would you like to deposit?",
                "account": "Which account should I deposit into? (savings/checking)",
            }
            return {"text": prompts[missing[0]], "nlu": nlu, "need": missing}

        result = self.db.deposit(
            self.state.slots["account"],
            float(self.state.slots["amount"])
        )
        if not result["ok"]:
            return {"text": f"Deposit failed: {result['error']}", "nlu": nlu}

        # clear slots after success
        for k in ["amount", "account"]:
            self.state.slots.pop(k, None)
        self.state.current_intent = None

        return {
            "text": f"Deposited ${result['amount']:.2f} into {result['to']}. New balance: ${result['new_balance']:.2f}.",
            "nlu": nlu,
        }
    
    def _handle_branch_details(self, nlu) -> dict:
        # Example: Just echo branch info, you can connect to DB if needed
        return {"text": "You can find branch details on our website or tell me your city for more info.", "nlu": nlu}

    def _handle_interest_rate(self, nlu) -> dict:
        loan_type = self.state.slots.get("loan_type")
        account_type = self.state.slots.get("account_type")
        if loan_type:
            return {"text": f"The current interest rate for {loan_type} is 7.5% per annum.", "nlu": nlu}
        elif account_type:
            return {"text": f"The current interest rate for {account_type} is 4% per annum.", "nlu": nlu}
        else:
            return {"text": "Which loan or account type do you want the interest rate for?", "nlu": nlu}

    def _handle_create_account(self, nlu) -> dict:
        account_type = self.state.slots.get("account_type")
        if not account_type:
            return {"text": "What type of account would you like to open? (savings, current, joint, etc.)", "nlu": nlu}
        self.state.current_intent = None
        self.state.slots.pop("account_type", None)
        return {"text": f"To open a {account_type}, please visit your nearest branch with ID proof.", "nlu": nlu}

    def _handle_lost_card(self, nlu) -> dict:
        card_type = self.state.slots.get("card_type")
        if not card_type:
            return {"text": "Which card did you lose? (debit, credit, ATM, etc.)", "nlu": nlu}
        self.state.current_intent = None
        self.state.slots.pop("card_type", None)
        return {"text": f"Your {card_type} has been blocked. Please visit the branch for a replacement.", "nlu": nlu}

    def _handle_apply_loan(self, nlu) -> dict:
        loan_type = self.state.slots.get("loan_type")
        if not loan_type:
            return {"text": "Which type of loan do you want to apply for? (home, personal, car, etc.)", "nlu": nlu}
        self.state.current_intent = None
        self.state.slots.pop("loan_type", None)
        return {"text": f"To apply for a {loan_type}, please provide income proof and visit your nearest branch.", "nlu": nlu}

    def _handle_check_history(self, nlu) -> dict:
        date = self.state.slots.get("date")
        day = self.state.slots.get("day")
        if date:
            return {"text": f"Showing transactions for {date}.", "nlu": nlu}
        elif day:
            return {"text": f"Showing transactions for {day}.", "nlu": nlu}
        else:
            return {"text": "For which date or period do you want your transaction history?", "nlu": nlu}

    def _handle_apply_card(self, nlu) -> dict:
        card_type = self.state.slots.get("card_type")
        if not card_type:
            return {"text": "Which card would you like to apply for? (debit, credit, visa, etc.)", "nlu": nlu}
        self.state.current_intent = None
        self.state.slots.pop("card_type", None)
        return {"text": f"To apply for a {card_type}, please visit your nearest branch.", "nlu": nlu}

    def _handle_close_account(self, nlu) -> dict:
        account_type = self.state.slots.get("account_type")
        if not account_type:
            return {"text": "Which account do you want to close? (savings, current, etc.)", "nlu": nlu}
        self.state.current_intent = None
        self.state.slots.pop("account_type", None)
        return {"text": f"Your {account_type} will be closed after verification at the branch.", "nlu": nlu}

