# import variable that stores my API key located in a .py file 
from sandbox import SECRET_KEY

import numpy as np
import pandas as pd
import requests
import json

# Stock object, requires a symbol to be created
class Stock:

    def __init__(self, symbol):
        self.symbol = symbol
        self.acc_bal = 10000
        self.num_stock = 0
        self.num_buys = 0
        self.num_failed_buys = 0
        self.num_sells = 0
        self.num_nothing_to_sell = 0

    # method returns a dataframe of stock prices for that symbol 
    def get_df_prices(self, date_param='10d'):
        url_prefix = "https://sandbox.iexapis.com/stable/"

        # Gets the stock price at closing for some date parameter
        path = f'stock/{self.symbol}/chart/{date_param}?chartCloseOnly=True&&token={SECRET_KEY}'
        full_url = requests.compat.urljoin(url_prefix, path)

        # request 
        resp = requests.get(full_url)
        # create json object from response
        prices_obj = json.loads(resp.text)
        # turn json object into dataframe
        self.prices = pd.DataFrame(prices_obj)
        return self.prices

    # private buy method
    def __buy_stock(self, stockval):
        if(self.acc_bal >= stockval):
            self.acc_bal = self.acc_bal - stockval
            self.num_stock += 1
            self.num_buys += 1
        else:
            self.num_failed_buys += 1

    # private sell method
    def __sell_stock(self, stockval):
        if(self.num_stock > 0):
            self.acc_bal = self.acc_bal + stockval
            self.num_stock -= 1
            self.num_sells += 1
        else:
            self.num_nothing_to_sell += 1

    # total account value method
    def get_total_val(self, final_stockval):
        self.acc_total = self.num_stock * final_stockval + self.acc_bal
        print(self.acc_total)
        print(self.num_stock)

    def backtest1(self):
        num_rows = self.prices.shape[0]
        for i in range(0,num_rows):
            if(self.prices["changePercent"][i] > .01):
                self.__sell_stock(self.prices["close"][i])
            if(self.prices["changePercent"][i] < -.01):
                self.__buy_stock(self.prices["close"][i])
        self.get_total_val(self.prices["close"].iloc[-1])
        
        

def main():
    AAPL = Stock("AAPL")
    AAPL.get_df_prices("1y")
    print(AAPL.prices)
    AAPL.backtest1()

if __name__ == "__main__":
    main()