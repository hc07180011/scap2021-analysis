import time
import hmac

from requests import Request, Session


req_args = dict({
    "market": "BTC-PERP",
    "side": "buy",
    "price": 10000,
    "type": "limit",
    "size": 0.0001,
    "reduceOnly": False,
    "ioc": False,
    "postOnly": False,
    "clientId": None
})

request = Request("POST", "https://ftx.com/api/orders", json=req_args)
prepared = request.prepare()

ts = int(time.time() * 1000)
signature_payload = f"{ts}{prepared.method}{prepared.path_url}".encode()
if prepared.body:
    signature_payload += prepared.body

API_KEY = "ZEM121gMc2G-TH1WHuAXYSMZX_yY3bJQ3RdJInSu" // You have to replace this
API_SECRET = "PqpL-ysuDEI4QDNjA-aThqtf62L5qKBHJ4B4kkxe" // You have to replace this

signature = hmac.new(
    API_SECRET.encode(),
    signature_payload,
    "sha256"
).hexdigest()

prepared.headers["FTX-KEY"] = API_KEY
prepared.headers["FTX-SIGN"] = signature
prepared.headers["FTX-TS"] = str(ts)

session = Session()
resp = session.send(prepared)

print(resp.text)
