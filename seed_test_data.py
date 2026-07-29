"""Seed the database with repeatable, non-production test data.

Run with:
    .venv/bin/python seed_test_data.py
"""

from auth import password_hash
from crypter import encrypt
from database import ApiKey, User_data, session


USER_COUNT = 100
TEST_PASSWORD = "TestPass!2026"


def key_count_for_user(number: int) -> int:
    """Give every tenth user three keys, every fifth user two, and others one."""
    if number % 10 == 0:
        return 3
    if number % 5 == 0:
        return 2
    return 1


def seed() -> None:
    created_users = 0
    created_keys = 0

    try:
        for number in range(1, USER_COUNT + 1):
            username = f"test_user_{number:03d}"
            user = session.query(User_data).filter_by(username=username).first()

            if user is None:
                user = User_data(
                    username=username,
                    password=password_hash(TEST_PASSWORD),
                    email=f"{username}@example.test",
                )
                session.add(user)
                session.flush()
                created_users += 1

            for key_number in range(1, key_count_for_user(number) + 1):
                fake_key = f"test-api-key-{number:03d}-{key_number:02d}"
                exists = session.query(ApiKey).filter_by(
                    userid=user.userid, model=f"test-model-{key_number}"
                ).first()
                if exists is None:
                    session.add(ApiKey(
                        userid=user.userid,
                        api_key=encrypt(fake_key),
                        model=f"test-model-{key_number}",
                        expiry="2099-12-31",
                        usability="test",
                    ))
                    created_keys += 1

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    print(f"Created {created_users} users and {created_keys} API keys.")
    print("\nFive test logins:")
    for number in range(1, 6):
        print(f"  test_user_{number:03d} / {TEST_PASSWORD}")
    print("\nUsers 005, 010, 015, etc. have multiple fake API keys.")


if __name__ == "__main__":
    seed()
