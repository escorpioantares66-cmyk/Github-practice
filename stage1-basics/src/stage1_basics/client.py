import asyncio
from typing import Any
import httpx

from stage1_basics.config import load_config

async def fetch(
    client: httpx.AsyncClient, path: str
) -> dict[str, Any]:
    cfg = load_config()
    url = f"{cfg['BASE_URL'].rstrip('/')}{path}"
    headers = {
        "Authorization": f"Bearer {cfg['API_KEY']}",
        "Content-Type": "application/json",
    }
    resp = await client.get(url, headers=headers, timeout=10.0)
    resp.raise_for_status()
    return {
        "url": url,
        "status": resp.status_code,
        "data": resp.json(),
    }

async def main() -> None:
    cfg = load_config()
    print(f"Using BASE_URL: {cfg['BASE_URL']}")
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            fetch(client, "/get?test=1"),
            fetch(client, "/get?test=2"),
            fetch(client, "/get?test=3"),
        )
    for r in results:
        print(r["status"], r["url"])

if __name__ == "__main__":
    asyncio.run(main())
