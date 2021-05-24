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

# Properties of a single stock
class Stock:
    # Needs a stock symbol, and the timeframe for the backtest (data gathered from some n to the current date)
    def __init__(self, symbol, timeframe):
        # Stock symbol
        self.symbol = symbol
        # Length of time for the backtest of the stock
        self.timeframe = timeframe
        # number of shares held
        self.num_held = 0
        # Dataframe of historical stock prices
        self.get_df_prices()
        # Total number of rows of the df
        self.num_rows = self.prices.shape[0]
        # Variables for iterating
        self.starting_ind = 0
        self.current_ind = 0

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

# Account object, requires some amount of starting cash and a vector of Stock objects
class Account:
    def __init__(self, starting_cash, bundle):
        # Cash values of the account
        self.acc_cash_initial = starting_cash
        self.acc_cash = starting_cash
        # List of individual Stock objects
        self.bundle = bundle
        self.acc_total_val = 0
        # Index of longest df
        self.max_ind = self.__max_ind()

    # buy a single share of stock
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
    def __get_acc_total_val(self):
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

    # Find the largest index out off all of the stocks selected (needed if a selected stock in our bundle has less data points than the others)
    def __max_ind(self):
        x = []
        for i in range(0, len(self.bundle)):
            x.append(self.bundle[i].num_rows)
        return max(x)

    # Set the starting index for each stock in the bundle.
    # Historical data gathered from IEX starts with the least recent data from a specified date and end with the most recent.
    # Therefore, if we have different lengths in our dataframe for certain stocks, we will need to adjust the algorithm.
    def __set_start(self):
        for i in range(0, len(self.bundle)):
            self.bundle[i].starting_ind = self.max_ind - self.bundle[i].num_rows

    # First backtesting algorithm
    def bt1(self):
        self.__set_start()
        for i in range(0, self.max_ind):
            for j in range(0, len(self.bundle)):
                # Algorithm begins when data is available for a certain stock.
                # For example, if a stocks data is only available for the past 2yrs, while another
                # stocks data has been available for 5yrs, we have to account for that.
                if self.bundle[j].starting_ind > i:
                    print("Skip")
                else:
                    print(self.bundle[j].prices["close"][self.bundle[j].current_ind])
                    self.bundle[j].current_ind += 1

def main():
    # Create a list of stocks we want to use in the backtest, and how far back we want to backtest from the current date
    multi = bundle(['AAPL', 'PLTR', 'AMZN'], '2y')
    # Create a stock object for the market index we are comparing performance against
    mkt = Stock('SPY', '2y')
    # Create an account object with an initial starting dollar value, and the bundle of stocks we are backtesting with
    Acc = Account(10000, multi)

    mkt.get_finals()
    Acc.get_finals()
    Acc.bt1()
    

if __name__ == "__main__":
    main()