import requests
from config.settings import API_BASE_URL, TIMEOUT, API_KEY

class BaseAPIClient(requests.Session):
    def __init__(self, api_key=None):
        super().__init__()
        self.base_url = API_BASE_URL
        self.headers.update({
            'Content-Type': 'application/json',
            "Notion-Version": "2022-06-28"
        })
        if api_key:
            self.headers.update({'Authorization': f'Bearer {api_key}'})
        else:
            self.headers.update({'Authorization': f'Bearer {API_KEY}'})
    
    def get(self, endpoint, params=None, **kwargs):
        url = f'{self.base_url}/{endpoint}'
        response = super().get(url, params=params, **kwargs)
        return self._handle_response(response)
    
    def post(self, endpoint, data=None, **kwargs):
        url = f'{self.base_url}/{endpoint}'
        response = super().post(url, json=data, **kwargs)
        return self._handle_response(response)
    
    def _handle_response(self, response):
        if response.status_code == 200:
            return {
                "code":200,
                "body": response.json()
            }
        else:
            raise Exception(response.json())
