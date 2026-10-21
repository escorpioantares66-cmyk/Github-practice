import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stage2_sdk import get_user, get_users, search_users


def main():
    parser = argparse.ArgumentParser(description="User SDK CLI - Week3")
    parser.add_argument("--name", help="Search users by name")
    parser.add_argument("--id", type=int, help="Get user by id")
    parser.add_argument("--all", action="store_true", help="List all users")
    args = parser.parse_args()

    if args.id:
        print(get_user(args.id))
    elif args.name:
        results = search_users(args.name)
        print(f"Found {len(results)}")
        for u in results:
            print(u)
    elif args.all:
        users = get_users()
        print(f"Total {len(users)} users")
        for u in users:
            print(u)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
