import json
import pandas as pd
import calendar
import csv
from stock_data_manager import StockDataManager
from datetime import datetime, timedelta

STOCK_DATA = StockDataManager('C:/Users/idan6/PycharmProjects/Day19-part1/AutoStocks-Website/DATA.json')
CRISIS_DATA = StockDataManager('C:/Users/idan6/PycharmProjects/Day19-part1/AutoStocks-Website/CRISIS_DATA.json')
stocksdata_csv_path = 'C:/Users/idan6/PycharmProjects/Day19-part1/AutoStocks-Website/stocks-data.csv'


def get_csv_stocks():
    try:
        with open(stocksdata_csv_path, mode='r', newline='', encoding='UTF8') as f:
            data = list(csv.reader(f, delimiter=","))
            return data[0]
    except IndexError:
        return []


class DataOrganizer:
    def __init__(self):
        self.today_date = datetime.now().date()
        self.crisis_dict = {}
        self.df = pd.read_csv(stocksdata_csv_path)
        self.df['Date'] = pd.to_datetime(self.df['Date'], dayfirst=True, yearfirst=False, format="%d/%m/%y")
        self.df.insert(1, 'Listing Date', self.df['Date'].dt.strftime('%d.%m.%Y'))

        self.months = self.df['Date'].dt.month.drop_duplicates().sort_values()
        self.years = self.df['Date'].dt.year.drop_duplicates().sort_values()

    def crisis_manager(self):
        symbols = STOCK_DATA.get_all_stocks_symbols()

        # New date format
        df_hidden = self.df.drop('Date', axis=1)

        # Reformat data type from string to float
        df_hidden.iloc[:, 1:] = df_hidden.iloc[:, 1:].map(lambda x: str(x).replace('%', '')).astype('float')

        # Reset Json file old values
        file_path = 'C:/Users/idan6/PycharmProjects/Day19-part1/AutoStocks-Website/CRISIS_DATA.json'
        new_sum_value = 999
        # Read the JSON file and update the "sum" element for all symbols
        with open(file_path, 'r+') as file:
            data = json.load(file)
            for symbol in data:
                data[symbol]['sum'] = new_sum_value
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()

        for symbol in symbols:
            print("|", end="", flush=True)
            for row_number in range(len(self.df)):
                stock_row = df_hidden.iloc[:, 1:][symbol][row_number:]
                listing_date = df_hidden.iloc[row_number]['Listing Date']
                stock_sum = round(stock_row.sum(), 2)
                old_sum = CRISIS_DATA.get_specific_stock_info(symbol)['sum']
                current_symbol = CRISIS_DATA.get_specific_stock_info(symbol)

                if symbol == current_symbol["symbol"] and old_sum > stock_sum:

                    data = {
                        "symbol": f'{symbol}',
                        "date": f'{listing_date}',
                        "sum": stock_sum,
                        "row number": row_number,
                    }
                    CRISIS_DATA.add_stock(symbol, data)

    def get_total_year_sum(self, year):

        # Define date range for the entire year
        start_date = pd.to_datetime(f'{year}-01-01').date()
        end_date = pd.to_datetime(f'{year}-12-31').date()

        # Filter by date range
        filtered_df = self.df[(self.df['Date'].dt.date >= start_date) & (self.df['Date'].dt.date <= end_date)]
        df_hidden = filtered_df.drop('Date', axis=1)

        df_hidden.iloc[:, 1:] = df_hidden.iloc[:, 1:].map(lambda x: str(x).replace('%', '')).astype('float')
        sum_row = round(df_hidden.iloc[:, 1:].fillna(0).sum(), 2)
        df_hidden = filtered_df._append(sum_row, ignore_index=True)
        df_hidden = df_hidden.fillna('Total')

        total_list = df_hidden.iloc[-1].tolist()
        return total_list[2:]

    def selected_months(self, stock):
        today_date = self.today_date.strftime('%Y-%m-%d')
        crisis_date = CRISIS_DATA.get_specific_stock_info(stock)['date']

        # Convert string to datetime object
        formatted_crisis_date = datetime.strptime(crisis_date, "%d.%m.%Y").strftime('%Y-%m-%d')

        # Define date range for the entire year
        start_date = pd.to_datetime(f'{formatted_crisis_date}-01-01').date()
        end_date = pd.to_datetime(today_date).date()

        # Filter by date range
        filtered_df = self.df[(self.df['Date'].dt.date >= start_date) & (self.df['Date'].dt.date <= end_date)]
        df_hidden = filtered_df.drop('Date', axis=1)
        stock_selected_data = df_hidden[['Listing Date', stock]]

        return stock_selected_data

    def selected_year(self, year):
        organized_data = []
        month_sum_list = []

        for month in self.months:

            # define the date in the end of the month
            date_range = pd.date_range(start=f'{year}-{month}-1', periods=1, freq='M')
            last_day_of_the_month = date_range[0].day

            # Define date range
            start_date = pd.to_datetime(f'{year}-{month}-01').date()
            end_date = pd.to_datetime(f'{year}-{month}-{last_day_of_the_month}').date()

            # Filter by date range
            filtered_df = self.df[(self.df['Date'].dt.date >= start_date) & (self.df['Date'].dt.date <= end_date)]

            if not filtered_df.empty:

                # New date format
                df_hidden = filtered_df.drop('Date', axis=1)

                # Calculate month results
                df_hidden.iloc[:, 1:] = df_hidden.iloc[:, 1:].map(lambda x: str(x).replace('%', '')).astype(
                    'float')

                sum_row = round(df_hidden.iloc[:, 1:].fillna(0).sum(), 2)
                df_hidden = df_hidden._append(sum_row, ignore_index=True)
                df_hidden.iloc[:, 1:] = df_hidden.iloc[:, 1:].map(lambda x: f'{x}%')
                df_hidden = df_hidden.fillna('Total')

                df_html = df_hidden.to_html(classes='table table-Default table-hover ', index=False)
                temp = df_html.replace("\n", "").replace(",", "").replace('<tr style="text-align: right;">',
                                                                          "<tr style='text-align: center;'>")[
                       :-1].replace("<thead>", "<thead class='table-dark'>").replace('<tr>      <td>Total</td>',
                                                                                     '<tr class="table-active" style="font-weight:bold">      <td>Total</td>').replace(
                    '<td>-', '<td class="table-danger">-')

                if len(temp) > 500:
                    organized_data.append(f"{temp}<thead class='table-dark'><th>{calendar.month_name[month]}</th>")
                    organized_data.append("<center><br>")

            convert_string = [str(item) for item in organized_data]
            result = "".join(convert_string)

        return result


#orgenizer = DataOrganizer()
#orgenizer.crisis_manager()
