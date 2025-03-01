# ZKP Authentication

## Table of Contents
1. [Introduction](#introduction)
2. [Project Overview](#project-overview)
3. [Protocol Details](#protocol-details)
   - [Registration Phase](#registration-phase)
   - [Authentication Phase](#authentication-phase)
     - [Commitment](#commitment)
     - [Verifiable Challenge Commitment and Reveal](#verifiable-challenge-commitment-and-reveal)
     - [Response and Verification](#response-and-verification)
4. [Code Structure](#code-structure)
   - [Server (server.py)](#server-serverpy)
   - [Client (client.py)](#client-clientpy)
5. [Installation and Setup](#installation-and-setup)
6. [Usage Instructions](#usage-instructions)
7. [Security Considerations](#security-considerations)
8. [Future Enhancements](#future-enhancements)
9. [Conclusion](#conclusion)

---

## Introduction

This project implements a unique variant of the Fiat–Shamir zero-knowledge proof (ZKP) authentication protocol. It is designed to allow a client to prove knowledge of a secret (derived from a password) without revealing the secret to the server. Enhancements include:
- **SHA‑256** used for converting passwords into numeric secrets.
- **Extended challenge space** (challenge values ranging from 0 to 3).
- **Verifiable challenge commitment**, where the server commits to its challenge using SHA‑256.
- **Ephemeral session parameters** for each authentication round.
- **Multi-round authentication** to reduce the likelihood of successful forgery.

---

## Project Overview

The system consists of two main components:
- **Server:** A Flask application using MongoDB to store user data and handle authentication endpoints.
- **Client:** A command-line interface (CLI) that registers and authenticates users by interacting with the server.

**Key Features:**
- **Registration:** The client computes a public value \( v = s^2 \mod n \) (using a numeric secret derived from the password) and sends it to the server.
- **Authentication:** The client and server perform multiple rounds of a ZKP protocol. In each round, the server commits to a challenge using SHA‑256, which the client verifies before responding.

---

## Protocol Details

### Registration Phase

1. **Secret Derivation:**  
   The client converts a user-provided password into a numeric secret \( s \) using SHA‑256.  
   \[
   s = \text{num}( \text{SHA-256}( \text{password} ) ) \mod n
   \]
2. **Public Value Computation:**  
   The client computes the public value:
   \[
   v = s^2 \mod n
   \]
3. **Submission:**  
   The client sends the username and \( v \) to the server. The server stores this information for later authentication.

### Authentication Phase

Authentication is performed over multiple rounds (e.g., 5 rounds) to minimize the success probability of an impostor.

#### Commitment

1. **Random Selection:**  
   The client picks a random \( r \) such that \( 1 \leq r < n \).
2. **Commitment Computation:**  
   The client computes:
   \[
   x = r^2 \mod n
   \]
3. **Submission:**  
   The client sends \( x \) and the username to the server via the `/auth/start` endpoint.

#### Verifiable Challenge Commitment and Reveal

1. **Challenge Generation:**  
   The server generates an extended challenge \( e \) (e.g., an integer in the range [0, 3]).
2. **Commitment Calculation:**  
   The server generates a random nonce and computes a commitment:
   \[
   C = \text{SHA-256}(e \parallel \text{nonce})
   \]
3. **Commitment Transmission:**  
   The server sends \( C \) (the challenge commitment) to the client.
4. **Challenge Reveal:**  
   After receiving \( C \), the client requests the actual challenge \( e \) and nonce via the `/auth/reveal` endpoint. The client then verifies:
   \[
   \text{SHA-256}(e \parallel \text{nonce}) \stackrel{?}{=} C
   \]
   If the verification fails, the session is terminated.

#### Response and Verification

1. **Response Computation:**  
   The client computes:
   \[
   y = r \times s^e \mod n
   \]
2. **Submission:**  
   The client sends \( y \) to the server via the `/auth/verify` endpoint.
3. **Verification:**  
   The server verifies the proof by checking:
   \[
   y^2 \mod n \stackrel{?}{=} x \times v^e \mod n
   \]
   If the verification holds for all rounds, the client is authenticated.

---

## Code Structure

### Server (server.py)

- **Framework:** Flask  
- **Database:** MongoDB (stores username and \( v \))
- **Endpoints:**
  - `/register`: Registers a user.
  - `/auth/start`: Accepts \( x \) and sends a challenge commitment.
  - `/auth/reveal`: Reveals the challenge \( e \) and nonce.
  - `/auth/verify`: Accepts \( y \) and verifies the response.
- **Cryptographic Primitives:** SHA‑256 is used to generate and verify challenge commitments.

### Client (client.py)

- **Interface:** CLI for user input.
- **Secret Handling:** Converts a password to a numeric secret using SHA‑256.
- **Authentication Rounds:** Repeats the commitment/challenge/response cycle over multiple rounds.
- **Interaction:** Communicates with the server through REST endpoints.

---

## Installation and Setup

1. **Install Dependencies:**
   - For the server:
     ```bash
     pip install flask pymongo
     ```
   - For the client:
     ```bash
     pip install requests
     ```
2. **Database Setup:**
   - Ensure MongoDB is installed and running.
   - Update the MongoDB connection URI in `server.py` as needed.
3. **Running the Server:**
   ```bash
   python server.py
   ```
4. **Running the Client:**
   ```bash
   python client.py
   ```

---

## Usage Instructions

1. **Registration:**
   - Run the client.
   - Choose option **1** for registration.
   - Enter the username and a password. The password is hashed using SHA‑256 to derive the secret.
   - The client computes \( v = s^2 \mod n \) and sends it to the server.

2. **Authentication:**
   - Run the client.
   - Choose option **2** for authentication.
   - Enter the username and the same password.
   - The client performs multiple rounds:
     - Computes a random \( r \) and \( x = r^2 \mod n \).
     - Receives a challenge commitment from the server.
     - Retrieves the challenge and nonce, verifies the commitment.
     - Computes the response \( y = r \times s^e \mod n \) and sends it.
     - If all rounds pass, authentication is successful.

3. **Exit:**
   - Choose option **3** to exit the CLI.

---

## Security Considerations

- **SHA‑256 Usage:**  
  SHA‑256 is used to convert the password into a numeric secret and to generate verifiable challenge commitments.
- **Extended Challenge Space:**  
  Using an extended range for \( e \) (0 to 3) increases security over a binary challenge.
- **Multiple Rounds:**  
  Repeating the authentication process over multiple rounds minimizes the risk of impostor success.
- **Ephemeral Session Data:**  
  Each authentication round uses fresh session parameters to prevent replay attacks.