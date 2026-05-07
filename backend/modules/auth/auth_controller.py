from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.modules.auth.auth_schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
)
from backend.modules.auth.auth_service import AuthService
from backend.database import get_db
from backend.core.dependencies import get_current_user_id


class AuthController:
    """Controller for authentication endpoints."""

    def __init__(self):
        self.router = APIRouter()
        self._register_routes()

    def _register_routes(self):
        """Register all auth routes."""
        self.router.post(
            "/register",
            response_model=TokenResponse,
            status_code=status.HTTP_201_CREATED,
        )(self.register)
        self.router.post("/login", response_model=TokenResponse)(self.login)
        self.router.get("/me", response_model=UserResponse)(self.get_current_user)

    async def register(
        self, user_data: UserCreate, db: Session = Depends(get_db)
    ) -> TokenResponse:
        """Register a new user."""
        service = AuthService(db)
        return service.register(user_data)

    async def login(
        self, login_data: UserLogin, db: Session = Depends(get_db)
    ) -> TokenResponse:
        """Authenticate user."""
        service = AuthService(db)
        return service.login(login_data)

    async def get_current_user(
        self, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)
    ) -> UserResponse:
        """Get current user info."""
        service = AuthService(db)
        return service.get_current_user(user_id)


auth_controller = AuthController()
router = auth_controller.router
