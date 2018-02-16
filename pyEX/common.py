import requests
import pandas as pd
import websocket
import http.client as httplib


_URL_PREFIX = 'https://api.iextrading.com/1.0/'
_SIO_URL_PREFIX = 'https://ws-api.iextrading.com/1.0/'
_TIMEFRAME_CHART = ['5y', '2y', '1y', 'ytd', '6m', '3m', '1m', '1d']
_TIMEFRAME_DIVSPLIT = ['5y', '2y', '1y', 'ytd', '6m', '3m', '1m']
_LIST_OPTIONS = ['mostactive', 'gainers', 'losers', 'iexvolume', 'iexpercent']


def _getJson(url):
    url = _URL_PREFIX + url
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    raise Exception('Response %d - ' % resp.status_code, resp.text)


def _wsURL(url):
        return _SIO_URL_PREFIX + url


def _df(resp):
    df = {k: [v] for k, v in resp.items()}
    return pd.DataFrame(df)


def _strToList(st):
    if isinstance(st, str):
        return [st]
    return st


def _raiseIfNotStr(s):
    if s is not None and not isinstance(s, str):
        raise Exception('Cannot use type %s' % str(type(s)))


class WSClient(object):
    def __init__(self, addr, sendinit=None, on_data=None, on_open=None, on_close=None, on_error=None):
        self.on_data = on_data or print

        print(addr)
        conn = httplib.HTTPConnection(addr)
        conn.request('POST', '/socket.io/1/')
        resp = conn.getresponse()
        hskey = resp.read().split(':')[0]

        def on_message(ws, message):
            print(message)
            self.on_data(message)

        def null(ws, *args):
            print(args)

        def on_open_default(ws):
            if sendinit:
                ws.send(sendinit)

        self.ws = websocket.WebSocketApp(_WS_URL_PREFIX+hskey,
                                         on_message=on_message,
                                         on_error=on_error if on_error else null,
                                         on_close=on_close if on_close else null)
        self.ws.on_open = on_open if on_open else on_open_default

    def run(self):

        self.ws.run_forever()


def _stream(url, sendinit=None, on_data=print):
    cl = WSClient(url, sendinit=sendinit, on_data=on_data)
    return cl
