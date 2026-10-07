import asyncio
import time
from pathlib import Path
from stage1_basics.client import APIClient
from stage1_basics.config import AppConfig

async def main() -> None:
    config = AppConfig.from_env()
    sample_data = {"app": "stage1-basics", "version": 1}
    config_path = Path("data/config.json")
    config.save_json_config(config_path, sample_data)
    loaded = config.load_json_config(config_path)
    print(f"Saved & loaded JSON from {config_path}: {loaded}")

    client = APIClient(config)
    print("Starting 3 concurrent fetches (secure)...")
    start = time.perf_counter()
    results = await asyncio.gather(
        client.get("/status"),
        client.get("/users"),
        client.get("/posts"),
    )
    elapsed = time.perf_counter() - start
    print(f"Done in {elapsed:.2f}s")
    for r in results:
        print(r)
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
