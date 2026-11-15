import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.security import hash_password, verify_password, create_access_token, decode_token

def test_password_hashing():
    pwd = "secret_password_2026"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed)
    assert not verify_password("wrong_password", hashed)
    print("[PASS] Password hashing & verification verified.")

def test_jwt_token_flow():
    payload = {"sub": "user-123", "username": "admin", "role": "admin"}
    token = create_access_token(payload, expires_delta_seconds=3600)
    assert token is not None
    decoded = decode_token(token)
    assert decoded["username"] == "admin"
    assert decoded["role"] == "admin"
    print("[PASS] JWT generation and token decoding verified.")

if __name__ == "__main__":
    test_password_hashing()
    test_jwt_token_flow()
    print("All Auth & RBAC tests passed.")
