#!/usr/bin/env python3
"""
Create a user for the LocalFeather web interface
"""

import sys
from getpass import getpass
from werkzeug.security import generate_password_hash
from app import create_app
from app.models import User
from sqlalchemy import select


def create_user(username, email, password, role='admin'):
    """Create a new user"""
    app = create_app()

    with app.db.session() as session:
        # Check if user already exists
        stmt = select(User).where(User.username == username)
        existing_user = session.execute(stmt).scalar_one_or_none()

        if existing_user:
            print(f"Error: User '{username}' already exists")
            return False

        # Check if email already exists
        stmt = select(User).where(User.email == email)
        existing_email = session.execute(stmt).scalar_one_or_none()

        if existing_email:
            print(f"Error: Email '{email}' is already registered")
            return False

        # Create new user
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            active=True
        )

        session.add(new_user)
        session.commit()

        print(f"\nUser created successfully:")
        print(f"  Username: {username}")
        print(f"  Email: {email}")
        print(f"  Role: {role}")

        return True


def main():
    print("=" * 60)
    print("LocalFeather - Create User")
    print("=" * 60)
    print()

    # Get user details
    username = input("Username: ").strip()
    if not username:
        print("Error: Username cannot be empty")
        sys.exit(1)

    email = input("Email: ").strip()
    if not email:
        print("Error: Email cannot be empty")
        sys.exit(1)

    password = getpass("Password: ")
    if not password:
        print("Error: Password cannot be empty")
        sys.exit(1)

    password_confirm = getpass("Confirm password: ")
    if password != password_confirm:
        print("Error: Passwords do not match")
        sys.exit(1)

    role = input("Role (admin/viewer) [admin]: ").strip().lower() or 'admin'
    if role not in ['admin', 'viewer']:
        print("Error: Role must be 'admin' or 'viewer'")
        sys.exit(1)

    print()

    # Create user
    success = create_user(username, email, password, role)

    if success:
        print("\nYou can now log in at http://yourserver:5000/login")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
