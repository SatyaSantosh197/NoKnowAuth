import requests
import random
import hashlib

URL = "http://127.0.0.1:5000"
n = 55  # For demo; use a larger modulus in production

def get_secret(prompt):
    secret_str = input(prompt)
    hash_str = hashlib.sha256(secret_str.encode()).hexdigest()
    secret = int(hash_str, 16) % n
    return secret if secret != 0 else 1

def register_user():
    print("\n--- User Registration ---")
    username = input("Enter username for registration: ")
    secret = get_secret("Enter your secret (password): ")
    v = (secret ** 2) % n
    payload = {"username": username, "v": v}
    response = requests.post(f"{URL}/register", json=payload)
    print("Response:", response.json())

def authenticate_user():
    print("\n--- User Authentication ---")
    username = input("Enter username for authentication: ")
    secret = get_secret("Enter your secret (password): ")
    
    rounds = 5
    passed_all = True
    for i in range(rounds):
        print(f"\n--- Round {i+1} ---")
        r = random.randint(1, n - 1)
        x = (r ** 2) % n
        
        payload = {"username": username, "x": x}
        response = requests.post(f"{URL}/auth/start", json=payload)
        data = response.json()
        if "commitment" not in data:
            print("Error:", data)
            return
        commitment = data["commitment"]
        print("Received commitment:", commitment)
        
        payload = {"username": username}
        response = requests.post(f"{URL}/auth/reveal", json=payload)
        reveal_data = response.json()
        if "challenge" not in reveal_data or "nonce" not in reveal_data:
            print("Error in challenge reveal:", reveal_data)
            return
        e = reveal_data["challenge"]
        nonce = reveal_data["nonce"]
        print(f"Challenge: {e}, Nonce: {nonce}")
        
        commit_input = f"{e}{nonce}".encode()
        computed_commit = hashlib.sha256(commit_input).hexdigest()
        if computed_commit != commitment:
            print("Commitment verification failed!")
            return
        
        y = (r * (secret ** e)) % n
        payload = {"username": username, "y": y}
        response = requests.post(f"{URL}/auth/verify", json=payload)
        result = response.json()
        print("Round result:", result)
        if response.status_code != 200:
            passed_all = False
            break
            
    if passed_all:
        print("\n*** User authenticated successfully! ***\n")
    else:
        print("\n*** Authentication failed. ***\n")

def main():
    while True:
        print("\n----------------------------")
        print("   ZKP Authentication CLI")
        print("----------------------------")
        print("1. Register")
        print("2. Authenticate")
        print("3. Exit")
        choice = input("Enter your choice (1, 2, or 3): ")
        if choice == "1":
            register_user()
        elif choice == "2":
            authenticate_user()
        elif choice == "3":
            print("Exiting..")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
