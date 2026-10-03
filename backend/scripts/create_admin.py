"""Create the first ADMIN user.

Run from the backend/ folder with:
    python -m scripts.create_admin
"""
import sys

from app import create_app
from app.extensions import db
from app.models.user import User


def main():
    app = create_app()
    with app.app_context():
        username = input("Admin username: ").strip()
        if not username:
            print("Username cannot be empty.")
            sys.exit(1)

        existing = User.query.filter_by(username=username).first()
        if existing:
            print(f"User '{username}' already exists.")
            sys.exit(1)

        email = input("Admin email (optional): ").strip() or None

        # NOTE: plain input() so you can SEE what you type.
        # Fine for a college project. Use getpass in production.
        password = input("Admin password: ")
        confirm = input("Confirm password: ")

        if password != confirm:
            print("Passwords do not match.")
            sys.exit(1)
        if len(password) < 6:
            print("Password must be at least 6 characters.")
            sys.exit(1)

        user = User(
            username=username,
            email=email,
            role="ADMIN",
            is_active=True,
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        print(f"[OK] Admin '{username}' created with user_id={user.user_id}")


if __name__ == "__main__":
    main()