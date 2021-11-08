import json
from websocket import create_connection


ws = create_connection("wss://ftx.com/ws/")

req_args = dict({
    "op": "subscribe",
    "channel": "trades",
    "market": "BTC-PERP"
})
ws.send(json.dumps(req_args))

while True:
    print(json.loads(ws.recv()))
