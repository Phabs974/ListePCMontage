import logging

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)


def create_default_admin_if_missing() -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        existing_user = db.query(User).first()
        existing_admin = db.query(User).filter(User.username == settings.admin_username).first()
        if existing_user or existing_admin:
            logger.info("Admin ensured")
            return

        try:
            role = UserRole(settings.admin_role)
        except ValueError:
            role = UserRole.ADMIN

        user = User(
            username=settings.admin_username,
            password_hash=hash_password(settings.admin_password),
            role=role,
        )
        db.add(user)
        db.commit()
        logger.info("Admin ensured")
    finally:
        db.close()
