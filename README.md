# Bank Chatbot (Python, Minimal NLU)

A lightweight banking chatbot that demonstrates **intent & entity recognition**, **confidence scoring**, **slot filling**, and a **mock core banking layer**. No external ML models are required.

It supports:
- Intents: `transfer_money`, `check_balance`, `account_info`, `greet`, `goodbye`, `fallback`
- Entities: `amount`, `from_account`, `to_account`, `account_id`
- Confidence scoring based on keyword coverage
- Slot filling for transfers (needs `amount`, `from_account`, `to_account`)
- A simple CLI, plus an optional Flask API

## Quick Start (CLI)

```bash
python3 -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Example:
```
> I want to transfer $500 from my savings to checking 4532
Chatbot: Transferred $500.00 from savings(****1234) to checking(****4532). New balances — savings: $1500.00, checking: $2500.00.
```

## Run the API (optional)

```bash
pip install -r requirements.txt
python server.py
# Then POST JSON to http://127.0.0.1:5000/chat with {"message":"check balance on savings"}
```

## Project Structure
- `nlu.py` — rule-based intent & entity extraction with confidence scoring
- `dialogue_manager.py` — slot filling & response generation
- `bank_core.py` — mock data & core banking operations
- `main.py` — CLI runner
- `server.py` — Flask API
- `requirements.txt` — lightweight deps

---

This project is designed for education and demos. **Do NOT** connect to real banking systems.
