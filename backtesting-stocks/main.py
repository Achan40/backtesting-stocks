# import variable that stores my API key located in a .py file 
from sandbox import SECRET_KEY

import logging
import numpy
import pandas as pd
import requests
import json

# Stock object, requires a symbol to be created
class Stock:

    def __init__(self, symbol):
        self.symbol = symbol

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


def main():
    AAPL = Stock("AAPL")
    AAPL.get_df_prices("2y")
    print(AAPL.prices.head())

if __name__ == "__main__":
    main()