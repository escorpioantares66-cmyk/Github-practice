from src.stage1_basics.config import AppConfig
from src.stage1_basics.client import APIClient

config = AppConfig(base_url="https://api.example.com", api_key="test123")
client = APIClient(config)
print(client.get("/status"))
