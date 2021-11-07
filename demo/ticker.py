import json
from websocket import create_connection


ws = create_connection("wss://ftx.com/ws/")

req_args = {
    "op": "subscribe",
    "channel": "trades",
    "market": "BTC-PERP"
}
ws.send(json.dumps(req_args))

while True:
    result = json.loads(ws.recv())
    print(result)