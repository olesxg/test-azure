from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from typing import Dict


class KeyVaultManager:
    def __init__(self, vault_url: str):
        self.vault_url = vault_url
        self.credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=vault_url, credential=self.credential)

    async def get_exchange_credentials(self, exchange_name: str) -> Dict[str, str]:
        try:
            api_key = self.client.get_secret(f"{exchange_name}-api-key").value
            api_secret = self.client.get_secret(f"{exchange_name}-api-secret").value
            return {"api_key": api_key, "api_secret": api_secret}
        except Exception:
            return {"api_key": "", "api_secret": ""}

    async def get_openai_key(self) -> str:
        try:
            return self.client.get_secret("openai-api-key").value
        except Exception:
            return ""

    async def set_secret(self, name: str, value: str) -> bool:
        try:
            self.client.set_secret(name, value)
            return True
        except Exception:
            return False
