from clerk_backend_api import Clerk
from clerk_backend_api.jwks_helpers import authenticate_request, AuthenticateRequestOptions
import os

clerk = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))

def get_current_user(request):
    """
    Verifies the Clerk JWT from the Authorization header.
    Returns the user_id string if valid, raises HTTPException if not.
    """
    from fastapi import HTTPException

    result = authenticate_request(
        clerk,
        request,
        AuthenticateRequestOptions(
            authorized_parties=os.getenv("CLERK_AUTHORIZED_PARTY", "").split(",")
        )
    )

    if not result.is_signed_in:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return result.payload.get("sub")  # sub = Clerk user ID