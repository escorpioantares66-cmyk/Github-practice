import requests

def fetch_status(url: str) -> int:
    r = requests.get(url, timeout=5)
    return r.status_code

def main() -> None:
    url: str = "https://httpbin.org/get"
    code: int = fetch_status(url)
    print(f"Success! Day 1 done. Status = {code} from {url}")

if __name__ == "__main__":
    main()
