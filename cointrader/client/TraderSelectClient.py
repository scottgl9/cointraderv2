from cointrader.client.cbadv.CBADVTraderClient import CBADVTraderClient
from cointrader.config import CBADV_KEY, CBADV_SECRET
class TraderSelectClient:
    def __init__(self, client_name):
        self.client = self.select_client(client_name)

    def get_client(self):
        return self.client

    def select_client(self, client_name):
        clients = {
            "cbadv": (CBADVTraderClient, CBADV_KEY, CBADV_SECRET),
        }
        if client_name.lower() not in clients:
            raise ValueError(f"Unknown client: {client_name}")
        client, key, secret = clients[client_name.lower()]
        return client(key, secret)
