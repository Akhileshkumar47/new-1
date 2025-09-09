
from flask import Flask, request, jsonify, render_template
from dialogue_manager import DialogueManager
import auth

app = Flask(__name__)
dm = DialogueManager()

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/chat-ui")
def chat_ui():
    return render_template("chat.html")

@app.post("/register")
def register():
    data = request.get_json(force=True)
    result = auth.register(data.get("username",""), data.get("password",""))
    return jsonify(result)

@app.post("/login")
def login():
    data = request.get_json(force=True)
    result = auth.login(data.get("username",""), data.get("password",""))
    return jsonify(result)

@app.post("/chat")
def chat():
    data = request.get_json(force=True, silent=True) or {}
    msg = data.get("message", "")
    if not msg:
        return jsonify({"error": "message is required"}), 400
    reply = dm.handle(msg)
    return jsonify({"reply": reply["text"], "nlu": reply["nlu"]})

@app.post("/reset")
def reset():
    dm.reset()
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)
