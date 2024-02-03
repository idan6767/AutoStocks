import json


class StockDataManager:
    def __init__(self, path):
        self.file_path = path

    def remove_stock(self, stock):
        with open(self.file_path, 'r') as file:
            data = json.load(file)
            del data[stock]
        with open(self.file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def add_stock(self, stock, value):
        with open(self.file_path, 'r') as file:
            data = json.load(file)
            data[stock] = value
        with open(self.file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def get_specific_stock_info(self, stock):
        with open(self.file_path, 'r') as file:
            data = json.load(file)
            stock_info = data[stock]
        return stock_info

    def get_all_stocks_info(self):
        with open(self.file_path, 'r') as file:
            data = json.load(file)
            all_stocks_info = data.values()
        return all_stocks_info

    def get_all_stocks_symbols(self):
        with open(self.file_path, 'r') as file:
            data = json.load(file)
            all_stocks_symbols = data.keys()
        return all_stocks_symbols
