import requests
from .config import Config

class APIClient:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {Config.get_api_key()}",
            "Content-Type": "application/json"
        }

    def post(self, endpoint, payload, stream=False, timeout=None):
        url = Config.get_api_url(endpoint)
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=timeout if timeout is not None else Config.API_TIMEOUT,
                stream=stream
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None