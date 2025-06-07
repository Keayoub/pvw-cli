"""
Authentication Service for managing JWT tokens and user authentication.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import jwt
import hashlib
import secrets
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

class AuthService:
    """Service for handling authentication and authorization operations."""
    
    def __init__(self, secret_key: str = "default-secret-key"):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.mock_users = self._generate_mock_users()
        self.active_sessions = {}
        self.refresh_tokens = {}
    
    def _generate_mock_users(self) -> Dict[str, Any]:
        """Generate mock user data for demonstration."""
        return {
            "admin@company.com": {
                "id": "user_001",
                "email": "admin@company.com",
                "name": "Admin User",
                "role": "admin",
                "department": "IT",
                "permissions": [
                    "read_all", "write_all", "delete_all", "admin_panel",
                    "user_management", "policy_management"
                ],
                "hashed_password": self.pwd_context.hash("admin123"),
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "last_login": "2024-01-15T16:30:00Z"
            },
            "alice.johnson@company.com": {
                "id": "user_002",
                "email": "alice.johnson@company.com",
                "name": "Alice Johnson",
                "role": "data_steward",
                "department": "Finance",
                "permissions": [
                    "read_all", "write_own", "classify_data", "steward_actions"
                ],
                "hashed_password": self.pwd_context.hash("alice123"),
                "is_active": True,
                "created_at": "2024-01-05T00:00:00Z",
                "last_login": "2024-01-15T14:20:00Z"
            },
            "bob.smith@company.com": {
                "id": "user_003",
                "email": "bob.smith@company.com",
                "name": "Bob Smith",
                "role": "analyst",
                "department": "Analytics",
                "permissions": [
                    "read_all", "create_reports", "view_lineage"
                ],
                "hashed_password": self.pwd_context.hash("bob123"),
                "is_active": True,
                "created_at": "2024-01-10T00:00:00Z",
                "last_login": "2024-01-15T15:45:00Z"
            }
        }
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return self.pwd_context.hash(password)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with email and password.
        
        Args:
            email: User email address
            password: User password
        
        Returns:
            User information if authentication successful, None otherwise
        """
        logger.info(f"Authenticating user: {email}")
        
        # Simulate authentication delay
        await asyncio.sleep(0.2)
        
        user = self.mock_users.get(email)
        if not user:
            logger.warning(f"User not found: {email}")
            return None
        
        if not user["is_active"]:
            logger.warning(f"User account disabled: {email}")
            return None
        
        if not self.verify_password(password, user["hashed_password"]):
            logger.warning(f"Invalid password for user: {email}")
            return None
        
        # Update last login
        user["last_login"] = datetime.utcnow().isoformat()
        
        logger.info(f"User authenticated successfully: {email}")
        return user
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Data to encode in the token
            expires_delta: Token expiration time
        
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, user_id: str) -> str:
        """
        Create a refresh token for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            Refresh token string
        """
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        self.refresh_tokens[token] = {
            "user_id": user_id,
            "expires_at": expires_at,
            "created_at": datetime.utcnow()
        }
        
        return token
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Perform user login and return tokens.
        
        Args:
            email: User email address
            password: User password
        
        Returns:
            Dictionary containing tokens and user information
        """
        user = await self.authenticate_user(email, password)
        if not user:
            raise ValueError("Invalid credentials")
        
        # Create tokens
        access_token_expires = timedelta(minutes=15)
        access_token = self.create_access_token(
            data={"sub": user["email"], "user_id": user["id"]},
            expires_delta=access_token_expires
        )
        
        refresh_token = self.create_refresh_token(user["id"])
        
        # Store session
        session_id = secrets.token_urlsafe(16)
        self.active_sessions[session_id] = {
            "user_id": user["id"],
            "email": user["email"],
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 900,  # 15 minutes
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"],
                "department": user["department"],
                "permissions": user["permissions"]
            },
            "session_id": session_id
        }
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            Dictionary containing new access token
        """
        logger.info("Refreshing access token")
        
        # Simulate refresh delay
        await asyncio.sleep(0.1)
        
        token_data = self.refresh_tokens.get(refresh_token)
        if not token_data:
            raise ValueError("Invalid refresh token")
        
        if datetime.utcnow() > token_data["expires_at"]:
            # Clean up expired token
            del self.refresh_tokens[refresh_token]
            raise ValueError("Refresh token expired")
        
        # Get user
        user_id = token_data["user_id"]
        user = next(
            (u for u in self.mock_users.values() if u["id"] == user_id),
            None
        )
        
        if not user or not user["is_active"]:
            raise ValueError("User not found or inactive")
        
        # Create new access token
        access_token_expires = timedelta(minutes=15)
        access_token = self.create_access_token(
            data={"sub": user["email"], "user_id": user["id"]},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 900
        }
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate a JWT token.
        
        Args:
            token: JWT token to decode
        
        Returns:
            Dictionary containing token payload
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.JWTError:
            raise ValueError("Invalid token")
    
    async def get_current_user(self, token: str) -> Dict[str, Any]:
        """
        Get current user from JWT token.
        
        Args:
            token: JWT access token
        
        Returns:
            Dictionary containing user information
        """
        payload = self.decode_token(token)
        email = payload.get("sub")
        
        if not email:
            raise ValueError("Invalid token payload")
        
        user = self.mock_users.get(email)
        if not user or not user["is_active"]:
            raise ValueError("User not found or inactive")
        
        return user
    
    async def logout(self, session_id: str) -> Dict[str, Any]:
        """
        Logout a user and invalidate session.
        
        Args:
            session_id: User session ID
        
        Returns:
            Dictionary containing logout result
        """
        logger.info(f"Logging out session: {session_id}")
        
        # Remove session
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        return {
            "message": "Logged out successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get user profile information.
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary containing user profile
        """
        logger.info(f"Getting user profile: {user_id}")
        
        user = next(
            (u for u in self.mock_users.values() if u["id"] == user_id),
            None
        )
        
        if not user:
            raise ValueError("User not found")
        
        # Return profile without sensitive data
        profile = {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "department": user["department"],
            "permissions": user["permissions"],
            "is_active": user["is_active"],
            "created_at": user["created_at"],
            "last_login": user["last_login"],
            "session_info": {
                "active_sessions": len([
                    s for s in self.active_sessions.values()
                    if s["user_id"] == user_id
                ])
            }
        }
        
        return profile
    
    async def update_user_profile(
        self,
        user_id: str,
        profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user profile information.
        
        Args:
            user_id: User ID
            profile_data: Updated profile data
        
        Returns:
            Dictionary containing updated profile
        """
        logger.info(f"Updating user profile: {user_id}")
        
        user = next(
            (u for u in self.mock_users.values() if u["id"] == user_id),
            None
        )
        
        if not user:
            raise ValueError("User not found")
        
        # Update allowed fields
        allowed_fields = ["name", "department"]
        for field in allowed_fields:
            if field in profile_data:
                user[field] = profile_data[field]
        
        user["updated_at"] = datetime.utcnow().isoformat()
        
        return await self.get_user_profile(user_id)
    
    async def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str
    ) -> Dict[str, Any]:
        """
        Change user password.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
        
        Returns:
            Dictionary containing result
        """
        logger.info(f"Changing password for user: {user_id}")
        
        user = next(
            (u for u in self.mock_users.values() if u["id"] == user_id),
            None
        )
        
        if not user:
            raise ValueError("User not found")
        
        if not self.verify_password(current_password, user["hashed_password"]):
            raise ValueError("Current password is incorrect")
        
        # Update password
        user["hashed_password"] = self.get_password_hash(new_password)
        user["password_changed_at"] = datetime.utcnow().isoformat()
        
        return {
            "message": "Password changed successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_active_sessions(self) -> Dict[str, Any]:
        """
        Get information about active user sessions.
        
        Returns:
            Dictionary containing session information
        """
        logger.info("Getting active sessions")
        
        sessions = []
        for session_id, session_data in self.active_sessions.items():
            # Get user info
            user = next(
                (u for u in self.mock_users.values() 
                 if u["id"] == session_data["user_id"]),
                None
            )
            
            if user:
                sessions.append({
                    "session_id": session_id,
                    "user_id": session_data["user_id"],
                    "email": session_data["email"],
                    "user_name": user["name"],
                    "created_at": session_data["created_at"].isoformat(),
                    "last_activity": session_data["last_activity"].isoformat(),
                    "duration_minutes": (
                        datetime.utcnow() - session_data["created_at"]
                    ).total_seconds() / 60
                })
        
        return {
            "sessions": sessions,
            "total_sessions": len(sessions),
            "generated_at": datetime.utcnow().isoformat()
        }
