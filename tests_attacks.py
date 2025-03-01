import random
import hashlib
import secrets
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/your_db_name")
db = client["your_db_name"]
users_collection = db["users"]

def generate_challenge():
    return random.randint(1, 10)

def calculate_proof(challenge, secret, nonce):
    hashed_secret = hashlib.sha256(secret.encode()).hexdigest()
    return hashlib.sha256(f"{challenge}{hashed_secret}{nonce}".encode()).hexdigest()

def verify_proof(challenge, proof, hashed_secret, nonce):
    expected_proof = hashlib.sha256(f"{challenge}{hashed_secret}{nonce}".encode()).hexdigest()
    return proof == expected_proof

def authenticate_user(username, password):
    user = users_collection.find_one({"username": username})
    if user:
        hashed_secret = user["password_hash"]
        nonce = secrets.token_hex(16)
        challenge = generate_challenge()
        proof = calculate_proof(challenge, password, nonce)
        if verify_proof(challenge, proof, hashed_secret, nonce):
            print("User authenticated successfully!")
        else:
            print("Authentication failed. Incorrect password.")
    else:
        print("User not found.")

# Simulated Attacks:

def sql_injection():
    print("\nCarrying out SQL Injection Attack Simulation")
    username = "abc3"
    password = "' OR '1'='1"
    authenticate_user(username, password)

def brute_force():
    print("\nCarrying out Brute-Force Attack Simulation")
    for i in range(1, 5):
        print(f"\nAttempt with password: {i}")
        authenticate_user("abc3", str(i))

def dictionary_attacks():
    print("\nCarrying out Dictionary Attacks Simulation")
    try:
        with open('dictionary_passwords.txt', 'r') as file:
            entries = [line.strip() for line in file]
        for pwd in entries:
            print(f"\nTrying password: {pwd}")
            authenticate_user("abc3", pwd)
    except FileNotFoundError:
        print("Password dictionary file not found.")

def replay_attack():
    print("\nSimulating Replay Attack")
    username = "abc3"
    password = "password123"
    nonce = secrets.token_hex(16)
    challenge = generate_challenge()
    proof = calculate_proof(challenge, password, nonce)

    user = users_collection.find_one({"username": username})
    if user:
        hashed_secret = user["password_hash"]
        # Simulate a failed replay attack by regenerating the nonce
        nonce = secrets.token_hex(16)
        if verify_proof(challenge, proof, hashed_secret, nonce):
            print("Replay Attack: User authenticated successfully!")
        else:
            print("Replay Attack: Authentication failed. Incorrect proof.")
    else:
        print("Replay Attack: User not found in database.")
    

def test_attack_menu():
    while True:
        print("\nSelect an attack simulation:")
        print("1. SQL Injection")
        print("2. Brute-Force Attack")
        print("3. Dictionary Attacks")
        print("4. Replay Attack")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ").strip()
        if choice == "1":
            sql_injection()
        elif choice == "2":
            brute_force()
        elif choice == "3":
            dictionary_attacks()
        elif choice == "4":
            replay_attack()
        elif choice == "5":
            print("Exiting attack tests.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    test_attack_menu()
    client.close()
