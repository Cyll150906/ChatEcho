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
    
    def post_files(self, endpoint, files, data=None, timeout=None):
        """Post request with file upload support"""
        url = Config.get_api_url(endpoint)
        try:
            response = requests.post(
                url,
                files=files,
                data=data,
                headers={"Authorization": self.headers["Authorization"]},  # Remove Content-Type for file upload
                timeout=timeout if timeout is not None else Config.API_TIMEOUT
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"API file upload failed: {e}")
            return None
    
    def post_stream(self, endpoint, payload, timeout=None):
        """Post request with streaming response support"""
        url = Config.get_api_url(endpoint)
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=timeout if timeout is not None else Config.API_TIMEOUT,
                stream=True
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"API streaming request failed: {e}")
            return None