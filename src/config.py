import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    azure_key_vault_url: str = ""
    azure_storage_connection_string: str = ""
    azure_application_insights_connection_string: str = ""
    azure_sql_connection_string: str = ""
    azure_datalake_account_name: str = ""
    openai_api_key: str = ""
    environment: str = "production"
    log_level: str = "INFO"
    trading_pairs: List[str] = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT"]
    arbitrage_threshold_percent: float = 0.5
    max_position_size_usd: float = 10000.0
    data_collection_interval_seconds: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
