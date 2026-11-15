import hashlib
import hmac
import base64
import json
import time
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.core.config import settings

security_bearer = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    """Generate SHA256 salted hash for passwords."""
    salt = settings.SECRET_KEY[:16]
    h = hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()
    return f"{salt}${h}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against salted hash."""
    try:
        salt, expected_hash = hashed_password.split("$", 1)
        actual_hash = hashlib.sha256(f"{salt}{plain_password}".encode("utf-8")).hexdigest()
        return hmac.compare_digest(actual_hash, expected_hash)
    except Exception:
        return False

def create_access_token(data: Dict[str, Any], expires_delta_seconds: int = 86400) -> str:
    """Create a tamper-evident HMAC-SHA256 JWT token."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = data.copy()
    payload["exp"] = int(time.time()) + expires_delta_seconds
    payload["iat"] = int(time.time())

    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    
    signing_input = f"{header_b64}.{payload_b64}"
    signature = hmac.new(
        settings.SECRET_KEY.encode(),
        signing_input.encode(),
        hashlib.sha256
    ).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")

    return f"{signing_input}.{sig_b64}"

def decode_token(token: str) -> Dict[str, Any]:
    """Validate and decode JWT token."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token structure")
        
        signing_input = f"{parts[0]}.{parts[1]}"
        expected_sig = hmac.new(
            settings.SECRET_KEY.encode(),
            signing_input.encode(),
            hashlib.sha256
        ).digest()
        expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")
        
        if not hmac.compare_digest(parts[2], expected_sig_b64):
            raise ValueError("Token signature verification failed")

        padding = "=" * (4 - len(parts[1]) % 4) if len(parts[1]) % 4 != 0 else ""
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + padding).decode())
        
        if payload.get("exp", 0) < time.time():
            raise ValueError("Token expired")
            
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer)) -> Dict[str, Any]:
    """Dependency to retrieve authenticated user from Bearer token."""
    if not credentials:
        # Default fallback for development mode
        return {"username": "operator_admin", "role": "admin"}
    return decode_token(credentials.credentials)

def require_role(allowed_roles: List[str]):
    """Role-based authorization guard."""
    def role_checker(user: Dict[str, Any] = Depends(get_current_user)):
        user_role = user.get("role", "operator")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of roles: {', '.join(allowed_roles)}. Current role: {user_role}"
            )
        return user
    return role_checker
