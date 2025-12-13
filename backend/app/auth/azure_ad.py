"""Azure AD authentication using MSAL"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
import httpx
from ..config import settings

security = HTTPBearer()


class AzureADAuth:
    """Azure AD authentication handler"""

    def __init__(self):
        self.tenant_id = settings.AZURE_AD_TENANT_ID
        self.client_id = settings.AZURE_AD_CLIENT_ID
        self.jwks_uri = f"https://login.microsoftonline.com/{self.tenant_id}/discovery/v2.0/keys"
        self.issuer = f"https://login.microsoftonline.com/{self.tenant_id}/v2.0"
        self._signing_keys = None

    async def get_signing_keys(self):
        """Fetch signing keys from Azure AD"""
        if self._signing_keys:
            return self._signing_keys

        async with httpx.AsyncClient() as client:
            response = await client.get(self.jwks_uri)
            response.raise_for_status()
            jwks = response.json()
            self._signing_keys = jwks["keys"]
            return self._signing_keys

    async def verify_token(self, token: str) -> dict:
        """
        Verify Azure AD JWT token

        Returns:
            dict: Decoded token payload with user information
        """
        try:
            # Get signing keys
            signing_keys = await self.get_signing_keys()

            # Decode token header to get key ID
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")

            # Find matching signing key
            signing_key = None
            for key in signing_keys:
                if key["kid"] == kid:
                    signing_key = key
                    break

            if not signing_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: signing key not found"
                )

            # Verify and decode token
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=self.issuer
            )

            return payload

        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )


# Create global instance
azure_ad = AzureADAuth()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency to get current authenticated user

    Usage in FastAPI endpoint:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"user": user}
    """
    token = credentials.credentials
    user = await azure_ad.verify_token(token)
    return user


# Optional: Extract specific user info
def get_user_email(user: dict = Depends(get_current_user)) -> str:
    """Get user email from Azure AD token"""
    return user.get("preferred_username") or user.get("email") or user.get("upn")


def get_user_name(user: dict = Depends(get_current_user)) -> str:
    """Get user name from Azure AD token"""
    return user.get("name", "Unknown User")
