import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database.session import SessionLocal
from backend.modules.auth.auth_models import User
from core.security import get_password_hash

def reset_password(email, password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.password_hash = get_password_hash(password)
            db.commit()
            print(f"Password reset successful for {email}")
        else:
            print(f"User {email} not found")
    finally:
        db.close()

if __name__ == "__main__":
    reset_password("bobby@gmail.com", "Bobby@123")
