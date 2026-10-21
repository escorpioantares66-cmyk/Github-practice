# github-practice

[![ci](https://github.com/escorpioantares66-cmyk/Github-practice/actions/workflows/ci.yml/badge.svg)](https://github.com/escorpioantares66-cmyk/Github-practice/actions/workflows/ci.yml)

A production-ready Python SDK + CLI for JSONPlaceholder Users API. Built mobile-first on Termux.

## Install
pip install github-practice

## CLI Usage
practice-cli --id 1
practice-cli --id 1 --json
practice-cli --search Leanne

## SDK Usage
from stage2_sdk import get_user, get_users, search_users
user = get_user(1)
print(user.name)

## Dev
pip install -e .
pytest -v
ruff check .
