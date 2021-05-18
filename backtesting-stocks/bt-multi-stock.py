# import variable that stores my API key located in a .py file 
from sandbox import SECRET_KEY

import numpy as np
import pandas as pd
import requests
import json

# percent change helper function
def get_change(final, initial):
        if final == initial:
            return 100.0
        try:
            return (abs(final - initial) / initial) * 100.0
        except ZeroDivisionError:
            return 0

# Account object, requires some amount of starting cash, the timeframe for the backtest, and a vector of Stock objects
class Account:
    def __init__(self, starting_cash, bundle):
        self.acc_cash_initial = starting_cash
        self.acc_cash = starting_cash
        self.bundle = bundle

    # buy a single share of stock
    def __buy_stock(self, stockval):
        if(self.acc_cash >= stockval):
            self.acc_cash = self.acc_cash - stockval
            self.num_stock += 1
            self.num_buys += 1
        else:
            self.num_failed_buys += 1

    # sell a single share of stock
    def __sell_stock(self, stockval):
        if(self.num_stock > 0):
            self.acc_cash = self.acc_cash + stockval
            self.num_stock -= 1
            self.num_sells += 1
        else:
            self.num_nothing_to_sell += 1
    

# Properties of a single stock
class Stock:
    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe
        self.num_held = 0
        self.get_df_prices()

    # method returns a dataframe of stock prices for that symbol 
    def get_df_prices(self):
        url_prefix = "https://sandbox.iexapis.com/stable/"

        # Gets the stock price at closing for some date parameter
        path = f'stock/{self.symbol}/chart/{self.timeframe}?chartCloseOnly=True&&token={SECRET_KEY}'
        full_url = requests.compat.urljoin(url_prefix, path)

        # request 
        resp = requests.get(full_url)
        # create json object from response
        prices_obj = json.loads(resp.text)
        # turn json object into dataframe
        self.prices = pd.DataFrame(prices_obj)
        return self.prices

    def get_finals(self):
        stock_initial_value = self.prices["close"].iloc[0]
        stock_final_value = self.prices["close"].iloc[-1]
        delta = get_change(stock_final_value, stock_initial_value)
        print("Change: " + str(delta) + "%")
        print("Timeframe: " + self.timeframe)
        


# helper function to create an array of Stock objects
def bundle(list_of_symbols, timeframe):
    multi = []
    for i in list_of_symbols:
        multi.append(Stock(i, timeframe))
    return multi

def main():
    multi = bundle(['AAPL', 'PLTR', 'AMZN'], '2y')
    mkt = Stock('SPY', '2y')
    Acc = Account(10000, multi)
    print(Acc.bundle[1].prices["close"][1])
    mkt.get_finals()


if __name__ == "__main__":
    main()