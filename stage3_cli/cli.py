#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stage2_sdk import get_user, get_users, search_users


def user_to_dict(u):
    return {
        "id": u.id,
        "name": u.name,
        "username": u.username,
        "email": u.email,
        "phone": u.phone,
        "website": u.website,
    }

def main():
    parser = argparse.ArgumentParser(description="User SDK CLI - Week3")
    parser.add_argument("--name", help="Search users by name")
    parser.add_argument("--id", type=int, help="Get user by id")
    parser.add_argument("--all", action="store_true", help="List all users")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.id:
        u = get_user(args.id)
        print(json.dumps(user_to_dict(u), indent=2) if args.json else u)
    elif args.name:
        results = search_users(args.name)
        if args.json:
            print(json.dumps([user_to_dict(r) for r in results], indent=2))
        else:
            print(f"Found {len(results)}")
            for u in results:
                print(u)
    elif args.all:
        users = get_users()
        if args.json:
            print(json.dumps([user_to_dict(u) for u in users], indent=2))
        else:
            print(f"Total {len(users)} users")
            for u in users:
                print(u)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
