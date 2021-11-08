import time
import hmac

from requests import Request, Session


ts = int(time.time() * 1000)

req_args = {
    "market": "BTC-PERP",
    "side": "buy",
    "price": 10000,
    "type": "limit",
    "size": 0.0001,
    "reduceOnly": False,
    "ioc": False,
    "postOnly": False,
    "clientId": None
}

request = Request("POST", "https://ftx.com/api/orders", json=req_args)
prepared = request.prepare()

signature_payload = f"{ts}{prepared.method}{prepared.path_url}".encode()
if prepared.body:
    signature_payload += prepared.body

signature_payload = signature_payload
signature = hmac.new(
    "nTOyFdN14ycUleT5aJXOe7miQww7NXZulcpCSMIe".encode(),
    signature_payload,
    "sha256"
).hexdigest()

prepared.headers["FTX-KEY"] = "3eCAuRqOyTSEg2tvfIw-CT0rS-MOtPkc7ajQdAZn"
prepared.headers["FTX-SIGN"] = signature
prepared.headers["FTX-TS"] = str(ts)

session = Session()
resp = session.send(prepared)

print(resp.text)
