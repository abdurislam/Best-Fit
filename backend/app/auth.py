"""
Firebase Admin SDK initialization and authentication utilities
"""

import os
from functools import lru_cache
from typing import Optional

import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Header, Depends
from dotenv import load_dotenv

load_dotenv()


@lru_cache()
def get_firebase_app():
    """Initialize Firebase Admin SDK (cached)"""
    cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
    
    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        return firebase_admin.initialize_app(cred)
    else:
        # For development without credentials, return None
        # In production, this should raise an error
        print("Warning: Firebase credentials not found. Auth will be disabled.")
        return None


def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """
    Verify Firebase ID token and return user ID.
    Returns None if auth is disabled (development mode).
    """
    app = get_firebase_app()
    
    # Development mode - no auth
    if app is None:
        return "dev-user"
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization.split("Bearer ")[1]
    
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


# Dependency for protected routes
async def require_auth(user_id: str = Depends(get_current_user)) -> str:
    """Dependency that requires authentication"""
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_id
