# Usage Guide

## CLI
practice-cli --id 1
practice-cli --id 1 --json
practice-cli --search Bret

## SDK with Error Handling
from stage2_sdk.client import APIError
from stage2_sdk import get_user

try:
    user = get_user(9999)
except APIError as e:
    print(f"Failed: {e}")
