import argparse

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User, UserRole


def create_admin(username: str, password: str, role: str) -> None:
    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == username).first():
            raise SystemExit("User already exists")
        user = User(username=username, password_hash=hash_password(password), role=UserRole(role))
        db.add(user)
        db.commit()
        print(f"Created {role} user {username}")
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create-user")
    create_parser.add_argument("--username", required=True)
    create_parser.add_argument("--password", required=True)
    create_parser.add_argument("--role", default="ADMIN")

    args = parser.parse_args()
    if args.command == "create-user":
        create_admin(args.username, args.password, args.role)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
