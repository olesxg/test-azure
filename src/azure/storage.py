import json
from datetime import datetime
from typing import List
from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableServiceClient, TableEntity


class StorageManager:
    def __init__(self, connection_string: str):
        self.blob_service = BlobServiceClient.from_connection_string(connection_string)
        self.table_service = TableServiceClient.from_connection_string(
            connection_string
        )
        self.container_name = "arbitrage-data"
        self.table_name = "opportunities"

    async def init_storage(self):
        try:
            self.blob_service.create_container(self.container_name)
        except Exception:
            pass

        try:
            self.table_service.create_table(self.table_name)
        except Exception:
            pass

    async def save_opportunities_to_blob(
        self, opportunities: List[dict], timestamp: datetime
    ):
        blob_name = f"opportunities/{timestamp.strftime('%Y/%m/%d/%H%M%S')}.json"
        blob_client = self.blob_service.get_blob_client(
            container=self.container_name, blob=blob_name
        )

        data = json.dumps(opportunities, default=str, indent=2)
        blob_client.upload_blob(data, overwrite=True)

    async def save_opportunity_to_table(self, opportunity: dict):
        table_client = self.table_service.get_table_client(self.table_name)

        entity = TableEntity()
        entity["PartitionKey"] = opportunity.get("symbol", "UNKNOWN")
        entity["RowKey"] = (
            f"{datetime.now().isoformat()}_{opportunity.get('buy_exchange', '')}_{opportunity.get('sell_exchange', '')}"
        )
        entity.update(
            {
                k: v
                for k, v in opportunity.items()
                if isinstance(v, (str, int, float, bool))
            }
        )

        try:
            table_client.create_entity(entity)
        except Exception:
            pass

    async def get_recent_opportunities(self, limit: int = 100) -> List[dict]:
        table_client = self.table_service.get_table_client(self.table_name)

        try:
            entities = table_client.list_entities(results_per_page=limit)
            return [dict(e) for e in entities][:limit]
        except Exception:
            return []
