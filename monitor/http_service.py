import requests


class HttpService:

    def get(self, url, params=None, headers=None):
        response = requests.get(url, params=params, headers=headers)
        return self._handle_response(response)

    def post(self, url, data=None, json=None, headers=None):
        response = requests.post(url, data=data, json=json, headers=headers)
        return self._handle_response(response)

    def _handle_response(self, response):
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            return {"error": str(e), "status": response.status_code}
        except ValueError:
            return response.text