from dataclasses import dataclass, field

@dataclass
class AppConfig:
    """This holds our settings in one clean box."""

    # These two you MUST give when you create it
    base_url: str
    api_key: str

    # These have defaults - practice for list, dict, tuple
    endpoints: list[str] = field(
        default_factory=lambda: ["/status", "/users"]
    )
    headers: dict[str, str] = field(
        default_factory=lambda: {"Content-Type": "application/json"}
    )
    retry_policy: tuple[int, int] = (3, 5)
