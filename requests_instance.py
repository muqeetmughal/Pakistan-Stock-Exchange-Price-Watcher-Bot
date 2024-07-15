import requests

class HttpClient:
    def __init__(self, base_url, headers=None, timeout=120):
        self.base_url = base_url
        self.headers = headers or {}
        self.timeout = timeout
        self.session = requests.Session()

    def _get_full_url(self, path):
        return f"{self.base_url}{path}"

    def get(self, path, params=None, **kwargs):
        url = self._get_full_url(path)
        response = self.session.get(url, headers=self.headers, params=params, timeout=self.timeout, **kwargs)
        return response

    def post(self, path, data=None, json=None, **kwargs):
        url = self._get_full_url(path)
        response = self.session.post(url, headers=self.headers, data=data, json=json, timeout=self.timeout, **kwargs)
        return response

    def put(self, path, data=None, **kwargs):
        url = self._get_full_url(path)
        response = self.session.put(url, headers=self.headers, data=data, timeout=self.timeout, **kwargs)
        return response

    def delete(self, path, **kwargs):
        url = self._get_full_url(path)
        response = self.session.delete(url, headers=self.headers, timeout=self.timeout, **kwargs)
        return response
if __name__ == "__main__":
    
    # Usage
    client = HttpClient(base_url="https://api.example.com", headers={"Authorization": "Bearer YOUR_TOKEN"})

    # Making requests
    response_get = client.get("/endpoint", params={"key": "value"})
    response_post = client.post("/endpoint", json={"key": "value"})

    print(response_get.json())
    print(response_post.json())
