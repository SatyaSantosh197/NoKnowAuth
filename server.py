from flask import Flask, request, jsonify
from pymongo import MongoClient
import random
import hashlib
import os

flase_app = Flask(__name__)

n = 91  # use a large 

client = MongoClient("mongodb://localhost:27017/zkp_auth")
db = client["zkp_auth"]
users_collection = db["users"]

auth_sessions = {}

@flase_app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    v = data.get("v")
    if not username or v is None:
        return jsonify({"error": "Username and v are required"}), 400
    if users_collection.find_one({"username": username}):
        return jsonify({"error": "User already exists"}), 400
    users_collection.insert_one({"username": username, "v": int(v)})
    return jsonify({"message": "User registered successfully", "n": n})

@flase_app.route("/auth/start", methods=["POST"])
def auth_start():
    data = request.get_json()
    username = data.get("username")
    x = data.get("x")
    if not username or x is None:
        return jsonify({"error": "Username and x are required"}), 400
    if not users_collection.find_one({"username": username}):
        return jsonify({"error": "User not found"}), 404

    e = random.randint(0, 3)
    nonce = os.urandom(16).hex()
    commit_input = f"{e}{nonce}".encode()
    commit = hashlib.sha256(commit_input).hexdigest()
    auth_sessions[username] = {"x": int(x), "e": e, "nonce": nonce, "commit": commit}
    return jsonify({"commitment": commit})

@flase_app.route("/auth/reveal", methods=["POST"])
def auth_reveal():
    data = request.get_json()
    username = data.get("username")
    if not username:
        return jsonify({"error": "Username is required"}), 400
    session = auth_sessions.get(username)
    if not session:
        return jsonify({"error": "No active authentication session"}), 400
    return jsonify({"challenge": session["e"], "nonce": session["nonce"]})

@flase_app.route("/auth/verify", methods=["POST"])
def auth_verify():
    data = request.get_json()
    username = data.get("username")
    y = data.get("y")
    if not username or y is None:
        return jsonify({"error": "Username and y are required"}), 400
    session = auth_sessions.get(username)
    if not session:
        return jsonify({"error": "No active authentication session"}), 400
    x = session["x"]
    e = session["e"]
    user = users_collection.find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404
    v = user["v"]
    if (int(y) ** 2) % n == (x * (v ** e)) % n:
        del auth_sessions[username]
        return jsonify({"message": "Round passed"})
    else:
        del auth_sessions[username]
        return jsonify({"message": "Round failed"}), 401

if __name__ == "__main__":
    flase_app.run(debug=True)
