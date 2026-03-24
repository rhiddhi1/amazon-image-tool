import os
import httpx
from jose import jwt, JWTError
from fastapi import HTTPException

# Cache the JWKS so we don't fetch it on every request
_jwks_cache = None

def _get_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        # Clerk JWKS endpoint — uses your publishable key prefix
        clerk_domain = os.getenv("CLERK_DOMAIN")  # e.g. sound-treefrog-7.clerk.accounts.dev
        url = f"https://{clerk_domain}/.well-known/jwks.json"
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        _jwks_cache = response.json()
    return _jwks_cache

def get_current_user(request):
    """
    Returns user_id (sub) if logged in.
    Returns None if no token present (anonymous user).
    Raises 401 if token is present but invalid.
    """
    auth_header = request.headers.get("Authorization")

    # No token → anonymous user, let them through
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]

    try:
        jwks = _get_jwks()

        # Decode without verification first to get the key id
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        # Find the matching key in JWKS
        rsa_key = {}
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n":   key["n"],
                    "e":   key["e"],
                }
                break

        if not rsa_key:
            raise HTTPException(status_code=401, detail="Invalid token key")

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            options={"verify_aud": False},  # Clerk doesn't use aud by default
        )

        return payload.get("sub")  # Clerk user ID

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
