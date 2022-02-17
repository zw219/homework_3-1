import pandas as pd
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time

def fetch_managed_accounts():

    class ibkr_app(EWrapper, EClient):
        def __init__(self):
            EClient.__init__(self, self)
            self.error_messages = pd.DataFrame(columns = [
                'reqId', 'errorCode', 'errorString'
            ])
            self.managed_accounts = []

        def error(self, reqId, errorCode, errorString):
            print("Error: ", reqId, " ", errorCode, " ", errorString)

        def managedAccounts(self, accountsList):
            self.managed_accounts = [i for i in accountsList.split(",") if i]

    app = ibkr_app()

    app.connect('127.0.0.1', 7497, 10645)
    while not app.isConnected():
        time.sleep(0.5)

    print('connected')

    def run_loop():
        app.run()

    # Start the socket in a thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    while len(app.managed_accounts) == 0:
        time.sleep(0.5)

    app.disconnect()

    return app.managed_accounts


def req_historical_data(contract, endDateTime='', durationStr='30 D',
                        barSizeSetting='1 hour', whatToShow='MIDPOINT',
                        useRTH=True):

    class ibkr_app(EWrapper, EClient):
        def __init__(self):
            EClient.__init__(self, self)
            self.error_messages = pd.DataFrame(columns=[
                'reqId', 'errorCode', 'errorString'
            ])
            self.next_valid_id = None
            self.historical_data = ''  # pd.DataFrame()
            self.historical_data_end = ''  # pd.DataFrame()

        def error(self, reqId, errorCode, errorString):
            print("Error: ", reqId, " ", errorCode, " ", errorString)

        def nextValidId(self, orderId: int):
            self.next_valid_id = orderId

        def historicalData(self, reqId, bar):
            # YOUR CODE GOES HERE: Turn "bar" into a pandas dataframe, formatted
            #   so that it's accepted by the plotly candlestick function.
            # Take a look at candlestick_plot.ipynb for some help!
            # assign the dataframe to self.historical_data.
            print(reqId, bar)
            self.historical_data = bar

        def historicalDataEnd(self, reqId: int, start: str, end: str):
            # super().historicalDataEnd(reqId, start, end)
            print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
            self.historical_data_end = reqId

    app = ibkr_app()

    app.connect('127.0.0.1', 7497, 10645)
    while not app.isConnected():
        time.sleep(0.01)

    def run_loop():
        app.run()

    # Start the socket in a thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    while isinstance(app.next_valid_id, type(None)):
        time.sleep(0.01)

    tickerId = app.next_valid_id
    app.reqHistoricalData(
        tickerId, contract, endDateTime, durationStr, barSizeSetting,
        whatToShow,
        useRTH, formatDate=1, keepUpToDate=False, chartOptions=[])

    while app.historical_data_end != tickerId:
        time.sleep(0.01)

    app.disconnect()

    return app.historical_data
