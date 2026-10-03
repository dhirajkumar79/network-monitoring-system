from typing import Optional

from app.extensions import db
from app.models.user import User


def authenticate(username: str, password: str) -> Optional[User]:
    """Return the User if credentials are valid AND account is active.
    Otherwise return None.
    """
    if not username or not password:
        return None

    user = User.query.filter_by(username=username).first()
    if user is None:
        return None
    if not user.is_active:
        return None
    if not user.check_password(password):
        return None
    return user


def get_user_by_id(user_id: int) -> Optional[User]:
    return db.session.get(User, user_id)