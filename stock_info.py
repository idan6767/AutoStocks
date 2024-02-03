import os

import yfinance as yf


class StocksData:
    def __init__(self, stocks):
        self.change_list = []
        self.stocks = stocks
        self.stock_info_cards = []
        self.stocks_info_data = []
        self.stock_list = list(self.stocks)

    def get_change_list(self):
        print("Receiving Stocks Data...  [1 / 5]")
        for stock in self.stocks:
            stock_name = yf.Ticker(stock)
            old_price = stock_name.fast_info['regularMarketPreviousClose']
            new_price = stock_name.fast_info['last_price']

            self.percentage_change = round((new_price - old_price) / old_price * 100, 2)
            self.change_list.append(f"{self.percentage_change}%")

            print("|", end="", flush=True)

        return self.change_list

    def get_stock_info(self):
        for stock in self.stocks:
            stock_info = yf.Ticker(stock).info
            self.stock_info_cards.append(stock_info)
        return self.stock_info_cards

    def full_stock_info(self, stock):
        full_stock_info = yf.Ticker(stock).info
        return full_stock_info

    # returns stock symbol by for any stock name
    def get_stock_symbol(self, stock):
        stock_symbol = yf.Ticker(stock).ticker
        return stock_symbol
