from stock_data_manager import StockDataManager
import datetime
import csv
from stock_info import StocksData
from mail_sender import Mail
import pandas as pd
from data_organizer import DataOrganizer

mail = Mail()
STOCK_DATA = StockDataManager('C:/Users/idan6/PycharmProjects/Day19-part1/AutoStocks-Website/DATA.json')
stocksdata_csv_path = 'C:/Users/idan6/PycharmProjects/Day19-part1/AutoStocks-Website/stocks-data.csv'

total_tasks = 5


# Returns current date
def get_time():
    time = datetime.datetime.now()
    return time


def get_csv_stocks():
    try:
        with open(stocksdata_csv_path, mode='r', newline='', encoding='UTF8') as f:
            data = list(csv.reader(f, delimiter=","))
            return data[0]
    except IndexError:
        return []


def get_stocks_prices():
    try:
        stocks_db = StocksData(stocks=STOCK_DATA.get_all_stocks_symbols())
        return stocks_db
    except AttributeError:
        return []
    except IndexError:
        return []


def refresh_stocks_list():

    # GeneratePriceChange class gets updated with the latest stock symbles
    # from CSV file and gets back stock dict with prices

    if len(get_csv_stocks()) > 1:
        stocks_name = STOCK_DATA.get_all_stocks_symbols()
        stocks_price = get_stocks_prices().get_change_list()
        stocks_dict = dict(zip(stocks_name, stocks_price))

        time_dict = {"date": get_time().strftime('%d/%m/%y')}
        time_dict.update(stocks_dict)
        print(f"\nUpdate Changes [2 / {total_tasks}]")

        # CSV file gets updated with latest changes
        with open(stocksdata_csv_path, mode='a', newline='', encoding='UTF8') as f:
            df = pd.DataFrame.from_dict(stocks_dict, orient='index')
            writer = csv.writer(f, delimiter=',')

            if len(pd.read_csv(stocksdata_csv_path)) < 2:
                writer.writerow({})
            writer.writerow(time_dict.values())
        print(f"Stocks Update Completed! [3 / {total_tasks}]")

        # Update Crisis Manager Data
        print(f"Scanning Crisis Manager Data [4 / {total_tasks}]")
        data_manager = DataOrganizer().crisis_manager()

        # Send update mail to user
        #mail.send_mail(f"Subject:🕒️ AutoStocks(Bot) Success\r\n\r\nStocks has been updated right now "
        #               f"({get_time().strftime('%d/%m/%y')}, {get_time().strftime('%H:%M')})\n\n"
        #               f"{df}")

        print(f"\nUpdate Mail Sent. [5 / {total_tasks}]")


# updates stocks data
if get_time().hour == 23:
    refresh_stocks_list()
