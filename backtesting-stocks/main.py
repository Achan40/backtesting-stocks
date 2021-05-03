# import variable that stores my API key located in a .py file 
from sandbox import SECRET_KEY

import pandas as pd
import requests
import json

# Stock object, requires a symbol to be created
class Stock:

    def __init__(self, symbol):
        self.symbol = symbol
        self.acc_bal = 10000
        self.num_stock = 0

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
        else:
            print("Out of funds")
            return

    # private sell method
    def __sell_stock(self, stockval):
        if(self.num_stock > 0):
            self.acc_bal = self.acc_bal + stockval
            self.num_stock -= 1
        else:
            print("None to sell")
            return

    # total account value method
    def get_total_val(self, final_stockval):
        self.acc_total = self.num_stock * final_stockval + self.acc_bal
        print(self.acc_total)

    def backtest1(self):
        TEST = 'TEST'
        
        

def main():
    AAPL = Stock("AAPL")
    AAPL.get_df_prices("2y")
    print(AAPL.prices)

if __name__ == "__main__":
    main()