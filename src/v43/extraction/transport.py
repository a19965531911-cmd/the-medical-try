import json
from urllib.request import Request, urlopen


class SemanticTransport:
    def __init__(self, endpoint: str = "http://127.0.0.1:1213/v1/chat/completions"):
        self.endpoint = endpoint

    def post(self, payload: dict, timeout: float) -> dict:
        request = Request(self.endpoint, json.dumps(payload).encode("utf-8"), {"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
