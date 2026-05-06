from sqlalchemy.orm import Session
from typing import Optional
from datetime import timedelta
from backend.modules.auth.auth_repository import UserRepository
from backend.modules.auth.auth_schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from backend.modules.auth.auth_models import User
from core.security import verify_password, create_access_token
from config.settings import settings
from fastapi import HTTPException, status
from backend.core.logger import logger


class AuthService:
    """Service for authentication business logic."""
    
    def __init__(self, db: Session):
        self.repository = UserRepository(db)
    
    def register(self, user_data: UserCreate) -> TokenResponse:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
        
        Returns:
            Token response with access token
        
        Raises:
            HTTPException: If email already exists
        """
        # Check if user already exists
        if self.repository.exists_by_email(user_data.email):
            logger.warning(f"Registration attempt with existing email: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = self.repository.create(user_data)
        logger.info(f"User registered successfully: {user.email}")
        
        # Generate token
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return TokenResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )
    
    def login(self, login_data: UserLogin) -> TokenResponse:
        """
        Authenticate user and return token.
        
        Args:
            login_data: User login credentials
        
        Returns:
            Token response with access token
        
        Raises:
            HTTPException: If credentials are invalid
        """
        # Get user by email
        user = self.repository.get_by_email(login_data.email)
        
        # Verify user exists and password is correct
        if not user or not verify_password(login_data.password, user.password_hash):
            logger.warning(f"Failed login attempt for email: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Generate token
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return TokenResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )
    
    def get_current_user(self, user_id: str) -> UserResponse:
        """
        Get current user by ID.
        
        Args:
            user_id: User ID from JWT token
        
        Returns:
            User response
        
        Raises:
            HTTPException: If user not found
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserResponse.model_validate(user)
