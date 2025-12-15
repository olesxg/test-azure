import json
from datetime import datetime
from typing import List
from azure.storage.filedatalake import DataLakeServiceClient
from azure.identity import DefaultAzureCredential


class DataLakeManager:
    def __init__(self, account_name: str):
        self.account_url = f"https://{account_name}.dfs.core.windows.net"
        self.credential = DefaultAzureCredential()
        self.service_client = DataLakeServiceClient(
            account_url=self.account_url, credential=self.credential
        )
        self.filesystem_name = "arbitrage"

    async def init_filesystem(self):
        try:
            self.service_client.create_file_system(self.filesystem_name)
        except Exception:
            pass

    async def upload_market_data(self, symbol: str, data: List[dict]):
        filesystem_client = self.service_client.get_file_system_client(
            self.filesystem_name
        )

        timestamp = datetime.now()
        file_path = f"market_data/{symbol}/{timestamp.strftime('%Y/%m/%d')}/{timestamp.strftime('%H%M%S')}.json"

        directory_client = filesystem_client.get_directory_client(
            f"market_data/{symbol}/{timestamp.strftime('%Y/%m/%d')}"
        )
        try:
            directory_client.create_directory()
        except Exception:
            pass

        file_client = filesystem_client.get_file_client(file_path)
        file_data = json.dumps(data, default=str, indent=2)
        file_client.upload_data(file_data, overwrite=True)

    async def upload_arbitrage_results(self, results: dict):
        filesystem_client = self.service_client.get_file_system_client(
            self.filesystem_name
        )

        timestamp = datetime.now()
        file_path = f"arbitrage_results/{timestamp.strftime('%Y/%m/%d/%H%M%S')}.json"

        directory_client = filesystem_client.get_directory_client(
            f"arbitrage_results/{timestamp.strftime('%Y/%m/%d')}"
        )
        try:
            directory_client.create_directory()
        except Exception:
            pass

        file_client = filesystem_client.get_file_client(file_path)
        file_data = json.dumps(results, default=str, indent=2)
        file_client.upload_data(file_data, overwrite=True)
