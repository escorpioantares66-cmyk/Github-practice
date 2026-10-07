import asyncio
import json
from pathlib import Path
from typing import Any


async def parse_line(line: str) -> dict[str, Any] | None:
    await asyncio.sleep(0.1)  # simulate IO
    if "ERROR" in line:
        parts = line.split(" ", 3)
        if len(parts) == 4:
            return {
                "date": parts[0],
                "time": parts[1],
                "level": parts[2],
                "message": parts[3],
            }
        return {"raw": line}
    return None


async def parse_log_file(input_path: Path, output_path: Path) -> list[dict[str, Any]]:
    text = input_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    results = await asyncio.gather(*[parse_line(item) for item in lines])
    errors = [r for r in results if r is not None]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(errors, indent=2), encoding="utf-8")
    return errors


async def main() -> None:
    inp = Path("logs/app.log")
    out = Path("data/errors.json")
    errors = await parse_log_file(inp, out)
    for e in errors:
        print(e)


if __name__ == "__main__":
    asyncio.run(main())
