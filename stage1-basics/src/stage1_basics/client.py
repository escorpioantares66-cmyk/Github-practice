from .config import AppConfig

class APIClient:
    """Stores base URL and API key, formats endpoints + headers."""

    def __init__(self, config: AppConfig):
        # __init__ is the constructor - runs when you create APIClient()
        self._base_url = config.base_url.rstrip("/")
        self._api_key = config.api_key
        self.config = config

    @property
    def is_configured(self) -> bool:
        # property lets you call it like client.is_configured (no brackets)
        return bool(self._base_url and self._api_key)

    def _format_endpoint(self, path: str) -> str:
        # internal method - _ means "private, don't call from outside"
        return f"{self._base_url}/{path.lstrip('/')}"

    def _get_headers(self) -> dict[str, str]:
        # internal method to build headers
        return {**self.config.headers, "Authorization": f"Bearer {self._api_key}"}

    def get(self, path: str) -> dict:
        # public method - this is what you call from outside
        url = self._format_endpoint(path)
        headers = self._get_headers()
        print(f"GET {url}")
        print(f"Headers: {headers}")
        return {"url": url, "headers": headers}
