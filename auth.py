import json, os, hashlib

AUTH_FILE = "users.json"

def _load_users():
    if not os.path.exists(AUTH_FILE):
        return {}
    with open(AUTH_FILE, "r") as f:
        return json.load(f)

def _save_users(users):
    with open(AUTH_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def register(username: str, password: str) -> dict:
    users = _load_users()
    if username in users:
        return {"ok": False, "error": "Username already exists"}
    users[username] = {"password": hash_pw(password)}
    _save_users(users)
    return {"ok": True}

def login(username: str, password: str) -> dict:
    users = _load_users()
    if username not in users:
        return {"ok": False, "error": "User not found"}
    if users[username]["password"] != hash_pw(password):
        return {"ok": False, "error": "Invalid password"}
    return {"ok": True}
