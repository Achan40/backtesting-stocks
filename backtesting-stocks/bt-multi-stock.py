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
            return ((final - initial) / initial) * 100.0
        except ZeroDivisionError:
            return 0

# helper function to create an array of Stock objects
def bundle(list_of_symbols, timeframe):
    multi = []
    for i in list_of_symbols:
        multi.append(Stock(i, timeframe))
    return multi

# Account object, requires some amount of starting cash, the timeframe for the backtest, and a vector of Stock objects
class Account:
    def __init__(self, starting_cash, bundle):
        self.acc_cash_initial = starting_cash
        self.acc_cash = starting_cash
        self.bundle = bundle
        self.acc_total_val = 0

    # buy a single share of stock. Takes in a Stock object
    def __buy_stock(self, stock_obj, stock_val):
        if(self.acc_cash > stock_val):
            self.acc_cash = self.acc_cash - stock_val
            stock_obj.num_held += 1
        else:
            print('Out of Cash')

    # sell a single share of stock
    def __sell_stock(self, stock_obj, stock_val):
        if(stock_obj.num_held > 0):
            stock_obj.num_held -= 1
            self.acc_cash = self.acc_cash + stock_val
        else:
            print('No availble shares to sell')

    # calculate final account value
    def get_acc_total_val(self):
        for i in range(0,len(self.bundle)):
            # the total value of the account is the current total value of the account plus remaining cash plus the number of shares held of a stock times the last price of the stock
            self.acc_total_val = self.acc_total_val + self.acc_cash + self.bundle[i].num_held * self.bundle[i].prices['close'].iloc[-1]

    
    # Get the rate of return any other final values for an account
    def get_finals(self):
        delta = get_change(self.acc_total_val, self.acc_cash_initial)
        print("Account")
        print("Change: " + str(delta) + "%")
        # Use timeframe from first stock object in the bundle of stocks (the timeframe is the same for all items in the bundle)
        print("Timeframe: " + self.bundle[0].timeframe + "\n")
    

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

    # Get the rate of return any other final values for a given stock
    def get_finals(self):
        stock_initial_value = self.prices["close"].iloc[0]
        stock_final_value = self.prices["close"].iloc[-1]
        delta = get_change(stock_final_value, stock_initial_value)
        print(self.symbol)
        print("Change: " + str(delta) + "%")
        print("Timeframe: " + self.timeframe + "\n")
        

def main():
    # Create a list of stocks we want to use in the backtest, and how far back we want to backtest from the current date
    multi = bundle(['AAPL', 'PLTR', 'AMZN'], '2y')
    # Create a stock object for the market index we are comparing performance against
    mkt = Stock('SPY', '2y')
    # Create an account object with an initial starting dollar value, and the bundle of stocks we are backtesting with
    Acc = Account(10000, multi)

    mkt.get_finals()
    Acc.get_finals()
    print(Acc.bundle[1].prices['close'][1])

if __name__ == "__main__":
    main()