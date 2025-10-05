import requests


class DataController:
    def __init__(self, server_url: str):
        self.url = server_url

    def get_assets(self):
        try:
            response = requests.get(self.url + "/assets")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(e)