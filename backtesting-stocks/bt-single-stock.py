# import variable that stores my API key located in a .py file 
from sandbox import SECRET_KEY

import numpy as np
import pandas as pd
import requests
import json

# percentage change function
def get_change(final, initial):
        if final == initial:
            return 100.0
        try:
            return (abs(final - initial) / initial) * 100.0
        except ZeroDivisionError:
            return 0

# Account object, requires some amount of starting cash, the timeframe for the backtest, and a single symbol
class Account:
    def __init__(self, starting_cash, timeframe, symbol):
        self.acc_cash_initial = starting_cash
        self.acc_cash = starting_cash
        self.timeframe = timeframe
        self.symbol = symbol

        self.num_stock = 0
        self.num_buys = 0
        self.num_failed_buys = 0
        self.num_sells = 0
        self.num_nothing_to_sell = 0

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

    # final values and percentage calculations
    def get_finals(self):
        stock_initial_value = self.prices["close"].iloc[0]
        stock_final_value = self.prices["close"].iloc[-1]

        self.acc_total = self.num_stock * stock_final_value + self.acc_cash
        self.stock_gain_per = get_change(stock_final_value, stock_initial_value)
        self.acc_gain_per = get_change(self.acc_total, self.acc_cash_initial)


    # print totals
    def get_totals(self):
        print("Ending cash: ", self.acc_cash)
        print("Total number of stock held: ", self.num_stock)
        print("Total number of purchases: ", self.num_buys)
        print("Total number of sells: ", self.num_sells)
        print("Total number of failed buys (out of funds): ", self.num_failed_buys)
        print("Total number of failed sells (out of stock): ", self.num_nothing_to_sell)
        print("Total ending account value: ", self.acc_total)
        print("Stock percentage gain: ", self.stock_gain_per)
        print("Portfolio percentage gain: ", self.acc_gain_per)

    # backtesting algorithm
    def backtest1(self):
        num_rows = self.prices.shape[0]
        for i in range(0,num_rows):
            pdelta = self.prices["changePercent"][i]
            if(pdelta > .05):
                nsells = int(pdelta/.05)
                for k in range(0,nsells):
                    self.__sell_stock(self.prices["close"][i])
            if(pdelta < -.01):
                nbuys = int(pdelta/-.01)
                for k in range(0, nbuys):
                    self.__buy_stock(self.prices["close"][i])
        self.get_finals()
        self.get_totals()

def main():
    AAPL = Account(10000,"5y","AAPL")
    AAPL.backtest1()

if __name__ == "__main__":
    main()