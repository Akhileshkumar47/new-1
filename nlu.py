
import re
from collections import defaultdict

INTENTS = {
    "transfer_money": {
        "keywords": ["transfer", "send", "move", "pay", "to", "from"],
        "required_entities": ["amount", "from_account", "to_account"],
    },
    "check_balance": {
        "keywords": ["balance", "how much", "left", "available"],
        "required_entities": ["account"],
    },
    "account_info": {
        "keywords": ["account", "details", "info", "number", "id"],
        "required_entities": ["account"],
    },
    "deposit_money": {
        "keywords": ["deposit", "add", "credit", "put", "into"],
        "required_entities": ["amount", "account"],
    },
    "greet": {"keywords": ["hello", "hi", "hey"], "required_entities": []},
    "goodbye": {"keywords": ["bye", "goodbye", "see you"], "required_entities": []},
}

ACCOUNT_WORDS = ["savings", "checking", "current", "credit", "loan"]
AMOUNT_RE = re.compile(r"(?:\$\s*)?(\d+(?:\.\d{1,2})?)")
ACCOUNT_ID_RE = re.compile(r"\b(?:acct|account)\s*(\d{3,12})\b|\b(\d{4,12})\b")

def _score_keywords(text: str, keywords: list[str]) -> float:
    text = text.lower()
    hits = sum(1 for k in keywords if k in text)
    return hits / max(1, len(keywords))

def extract_entities(text: str) -> dict:
    text_low = text.lower()
    ents = {}

    # amount
    m = AMOUNT_RE.search(text_low)
    if m:
        ents["amount"] = float(m.group(1))

    # accounts by kind
    # from ... to ...
    # heuristics to map from/to
    # find account kinds first
    kinds_found = []
    for w in ACCOUNT_WORDS:
        if w in text_low:
            kinds_found.append(w)

    # account ids
    ids_found = []
    for m in ACCOUNT_ID_RE.finditer(text_low):
        val = next((g for g in m.groups() if g), None)
        if val:
            ids_found.append(val)

    # preposition heuristics
    # from <A> to <B>
    from_match = re.search(r"from\s+([a-z]+\s*\d*)", text_low)
    to_match = re.search(r"to\s+([a-z]+\s*\d*)", text_low)

    def normalize_account_token(tok: str) -> dict:
        tok = tok.strip()
        # split kind + id (e.g., "checking 4532")
        parts = tok.split()
        kind = None
        acc_id = None
        for p in parts:
            if p in ACCOUNT_WORDS:
                kind = p
            elif p.isdigit():
                acc_id = p
        return {"kind": kind, "id": acc_id}

    if from_match:
        f = normalize_account_token(from_match.group(1))
        ents["from_account"] = f["kind"] or f["id"]
    if to_match:
        t = normalize_account_token(to_match.group(1))
        ents["to_account"] = t["kind"] or t["id"]

    # fallback mapping if not captured via prepositions
    if "from_account" not in ents and kinds_found:
        ents["from_account"] = kinds_found[0]
    if "to_account" not in ents and len(kinds_found) > 1:
        ents["to_account"] = kinds_found[1]
    if "to_account" not in ents and ids_found:
        ents["to_account"] = ids_found[-1]

    # general account (for balance/info)
    if "account" not in ents:
        if kinds_found:
            ents["account"] = kinds_found[0]
        elif ids_found:
            ents["account"] = ids_found[0]

    return ents

def classify_intent(text: str) -> tuple[str, float]:
    text = text.lower().strip()
    best_intent = "fallback"
    best_score = 0.0
    for name, spec in INTENTS.items():
        score = _score_keywords(text, spec["keywords"])
        if score > best_score:
            best_intent, best_score = name, score
    # tiny boost if we have entities that suit the intent
    ents = extract_entities(text)
    if best_intent == "transfer_money":
        if {"amount", "from_account", "to_account"} <= set(ents):
            best_score = min(1.0, best_score + 0.3)
    return best_intent, round(best_score, 2)

def parse(text: str) -> dict:
    intent, confidence = classify_intent(text)
    entities = extract_entities(text)
    return {
        "intent": intent,
        "confidence": confidence,
        "entities": entities,
    }
