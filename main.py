import pandas.errors
import requests.exceptions
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators
import csv
import pandas as pd
import os
from stock_info import StocksData
from stock_data_manager import StockDataManager
import matplotlib
import matplotlib.pyplot as plt
import yfinance as yf
from io import BytesIO
import base64
from data_organizer import DataOrganizer
import json
from datetime import datetime as dt, timedelta, date
import matplotlib.dates as mdates
import numpy as np

today_date = date.today()
today_datetime = dt.combine(today_date, dt.min.time())

STOCK_DATA = StockDataManager('DATA.json')
TEMP_STOCK_DATA = StockDataManager('TEMP_DATA.json')
NEWS_DATA = StockDataManager('NEWS_DATA.json')
CRISIS_DATA = StockDataManager('C:/Users/idan6/PycharmProjects/Day19-part1/AutoStocks-Website/CRISIS_DATA.json')
stocksdata_csv_path = 'C:/Users/idan6/PycharmProjects/Day19-part1/AutoStocks-Website/stocks-data.csv'

full_info = StocksData("")
matplotlib.use('Agg')


def get_csv_stocks():
    try:
        with open(stocksdata_csv_path, mode='r', newline='', encoding='UTF8') as f:
            data = list(csv.reader(f, delimiter=","))
            return data[0]
    except IndexError:
        return []


app = Flask(__name__)
Bootstrap(app)
app.app_context().push()
app.config['SECRET_KEY'] = os.urandom(32)


class AddSymbleForm(FlaskForm):
    symble = StringField('Enter Symbol', [validators.Length(min=4, max=4), validators.DataRequired(),
                                          validators.Regexp(r'^[a-zA-Z]+$', message='only characters are allowed')])
    add = SubmitField(label='Search')


# Check if a symbol exists or not
def is_symbol_exist(symbol):
    try:
        full_info.full_stock_info(symbol)
        return True
    except requests.exceptions.HTTPError:
        return False


def generate_stock_chart(symbol, title, start_date, end_date):
    # Fetch the stock data
    data = yf.download(symbol, start=start_date, end=end_date)
    plt.switch_backend('agg')
    # Plot the closing prices over the years
    plt.plot(data['Close'])
    plt.xlabel('Date', labelpad=20)
    plt.ylabel('Closing Price', labelpad=20)
    plt.title(title)
    plt.xticks(rotation=30, fontsize=8)

    # Automatically format and rotate x-axis date labels
    plt.gcf().autofmt_xdate()

    # Add dollar sign to every y-axis label
    plt.gca().yaxis.set_major_formatter('{x:,.0f}$')

    # Add tight layout to prevent overlapping labels
    plt.tight_layout()

    chart = plt

    # Save the chart image to a BytesIO buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the chart image as base64
    chart_image = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()
    # Close the plot to release memory
    plt.close()

    return chart_image


def generate_year_bar_chart(stocks_sum_list, year):
    organizer = DataOrganizer()

    # Your data
    x_values = STOCK_DATA.get_all_stocks_symbols()
    y_values = organizer.get_total_year_sum(year)

    bar_sizes = [0.35 for n in range(len(x_values))]

    # Creating the bar chart
    fig, ax = plt.subplots(figsize=(8.2, 3))
    bars = ax.bar(x_values, y_values, width=bar_sizes,
                  color='#FF8B71')

    # Adding labels above or below the bars based on the y-values
    for bar, yval in zip(bars, y_values):
        va = 'bottom' if yval < 0 else 'top'
        label = f'{round(yval, 2)}%'
        plt.text(bar.get_x() + bar.get_width() / 2, yval - 13 if va == 'bottom' else yval + 12, label, ha='center',
                 va=va, fontsize=9)  # Adjust fontsize as needed

    # Adding padding inside the chart
    x_padding_percentage = 0.4  # Adjust as needed
    y_padding_percentage = 20  # Adjust as needed
    ax.set_xlim([min(ax.get_xlim()) - x_padding_percentage, max(ax.get_xlim()) + x_padding_percentage])
    ax.set_ylim([min(ax.get_ylim()) - y_padding_percentage, max(ax.get_ylim()) + y_padding_percentage])

    # Adding labels with '%' sign
    # ax.set_xlabel('X-axis Label')
    # ax.set_ylabel('Y-axis Label (%)', fontsize=6)  # Adjust fontsize as needed
    ax.set_title(f'{year} Stocks Progress', fontsize=10)  # Adjust fontsize as needed

    # Save the chart image to a BytesIO buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the chart image as base64
    chart_image = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()  # Close the buffer to release memory

    # Close the plot to release memory
    plt.close()

    return chart_image


def generate_year_pie_chart(stocks_percentage, year):
    # Your data
    labels_list = []
    labels_data = STOCK_DATA.get_all_stocks_symbols()
    for key in labels_data:
        labels_list.append(key)
    labels = labels_list
    sizes = stocks_percentage
    colors = ['#FF8B71', '#FFB74D', '#FFD700', '#9CCC65', '#81C784', '#64B5F6', '#7986CB', '#BA68C8', '#FFAB91']

    # Look for stock values less than 0 and remove them
    negative_numbers = list(filter(lambda x: (x < 1), sizes))
    for num in negative_numbers:
        loc = sizes.index(num)
        sizes.pop(loc)
        labels.pop(loc)

    # Creating the pie chart
    fig, ax = plt.subplots(figsize=(4, 4))
    wedges, texts, autotexts = ax.pie(sizes, labels=labels,
                                      autopct=lambda p: '{:.1f}%'.format(p * sum(sizes) / 100) if p > 0 else '',
                                      startangle=90, colors=colors, wedgeprops=dict(width=0.4), pctdistance=0.80)

    # Adjusting text properties
    plt.setp(autotexts, size=8, weight="bold")
    plt.setp(texts, size=8)

    # Adding title
    ax.set_title(f'{year} Stocks Distribution', fontsize=10)

    # Save the chart image to a BytesIO buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the chart image as base64
    chart_image = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()  # Close the buffer to release memory

    # Close the plot to release memory
    plt.close()

    return chart_image


def is_csv_empty():
    with open(stocksdata_csv_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        try:
            first_row = next(csv_reader)
        except StopIteration:  # Empty file, no rows
            return True
        return False


@app.route('/', methods=['POST', 'GET'])
def stocks():
    try:
        df = pd.read_csv(stocksdata_csv_path)
        df_values = df.columns.values

        if len(df_values) == 1:
            os.remove(stocksdata_csv_path)

        with open(stocksdata_csv_path, newline='', encoding="utf8") as csv_file:
            csv_data = csv.reader(csv_file, delimiter=',')
            list_of_rows = []
            for row in csv_data:
                list_of_rows.append(row)

        organizer = DataOrganizer()
        year_list = organizer.years

        if request.method == 'POST':
            user_choice = int(request.form['year_select'])

            return render_template('index.html', stocks_headlines=get_csv_stocks(),
                                   df=organizer.selected_year(user_choice), years=year_list,
                                   user_choice=user_choice, stocks_data=reversed(list_of_rows[-5:]),
                                   chart=generate_year_bar_chart(organizer.get_total_year_sum(user_choice),
                                                                 user_choice),
                                   pie_chart=generate_year_pie_chart(organizer.get_total_year_sum(user_choice),
                                                                     user_choice))

    except pandas.errors.EmptyDataError:
        os.remove(stocksdata_csv_path)
        with open(stocksdata_csv_path, mode='a', newline='', encoding='UTF8') as f:
            writer = csv.writer(f, delimiter=',')
        return render_template('index.html')

    except FileNotFoundError:
        with open(stocksdata_csv_path, mode='a', newline='', encoding='UTF8') as f:
            writer = csv.writer(f, delimiter=',')
            return render_template('index.html')

    return render_template('index.html', stocks_headlines=get_csv_stocks(),
                           stocks_data=reversed(list_of_rows[-5:]), years=year_list)


@app.route('/delete_last_row')
def delete_last_row():
    df = pd.read_csv(stocksdata_csv_path)
    df = df.drop(df.index[-1])
    df.to_csv(stocksdata_csv_path, index=False)
    return redirect(url_for('stocks'))


@app.route('/choose_stocks', methods=['POST', 'GET'])
def choose_stocks():
    form = AddSymbleForm()

    if form.validate_on_submit():
        user_input = form.symble.data.upper()

        if is_symbol_exist(form.symble.data):

            if (user_input not in TEMP_STOCK_DATA.get_all_stocks_info() and user_input not in get_csv_stocks()
                    and user_input not in STOCK_DATA.get_all_stocks_symbols()):

                flash(f"'{user_input}' ✔️")
                TEMP_STOCK_DATA.add_stock(user_input, full_info.full_stock_info(user_input))

                return render_template('choose_stocks.html', form=form,
                                       user_stocks=reversed(TEMP_STOCK_DATA.get_all_stocks_info()),
                                       current_stocks=get_csv_stocks(), stocks_data=STOCK_DATA.get_all_stocks_symbols())

            else:
                flash(f"'{form.symble.data.upper()}' Already In Your List.")
                return render_template('choose_stocks.html', form=form,
                                       user_stocks=reversed(TEMP_STOCK_DATA.get_all_stocks_info()),
                                       current_stocks=get_csv_stocks(), stocks_data=STOCK_DATA.get_all_stocks_symbols())
        else:
            flash(f"'{form.symble.data.upper()}' Is not A Valid Symbol")
            return render_template('choose_stocks.html', form=form,
                                   user_stocks=reversed(TEMP_STOCK_DATA.get_all_stocks_info()),
                                   current_stocks=get_csv_stocks(), stocks_data=STOCK_DATA.get_all_stocks_symbols())
    return render_template('choose_stocks.html', form=form, user_stocks=reversed(TEMP_STOCK_DATA.get_all_stocks_info()),
                           current_stocks=get_csv_stocks(), stocks_data=STOCK_DATA.get_all_stocks_symbols())


@app.route('/add/')
def add_stocks_list():
    if is_csv_empty():
        empty_csv_template = []
        empty_csv_template.insert(0, "Date")
        with open(stocksdata_csv_path, mode='a', encoding='UTF8') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(empty_csv_template)

    user_request = str(request.args.get("single"))

    try:

        data = {
            "symbol": f'{user_request}',
            "date": '-',
            "sum": 0,
            "row number": '-',
        }

        # if user add only one stock instead all the list
        if user_request != "None":
            TEMP_STOCK_DATA.remove_stock(user_request)
            STOCK_DATA.add_stock(user_request, full_info.full_stock_info(user_request))
            CRISIS_DATA.add_stock(user_request, data)

            df = pd.read_csv("stocks-data.csv")
            df[user_request] = 0
            df.head()
            df.to_csv(stocksdata_csv_path, index=False)

            return redirect(url_for('choose_stocks'))

        # if user add all the stock list
        if user_request == "None":

            for stock in TEMP_STOCK_DATA.get_all_stocks_symbols():
                TEMP_STOCK_DATA.remove_stock(stock)
                STOCK_DATA.add_stock(stock, full_info.full_stock_info(stock))
                CRISIS_DATA.add_stock(stock, data)

                df = pd.read_csv("stocks-data.csv")
                df[stock] = 0
                df.head()
                df.to_csv(stocksdata_csv_path, index=False)

            return redirect(url_for('stocks'))

    except pandas.errors.EmptyDataError:
        pass


@app.route('/info_cards')
def info_cards():
    try:
        df = pd.read_csv(stocksdata_csv_path)
        df_values = df.columns.values
        if len(df_values) > 1:
            return render_template('info_cards.html', stocks=STOCK_DATA.get_all_stocks_info())

    except pandas.errors.EmptyDataError:
        return render_template('info_cards.html')


@app.route('/stock_card/<symbol>')
def card(symbol):
    seven_years_before = (dt.today() - timedelta(days=2555)).strftime("%Y-%m-%d")
    title = f"{symbol} Stock Price Over the Years"

    stock_data = STOCK_DATA.get_specific_stock_info(symbol)
    stock_chart = generate_stock_chart(symbol, title, seven_years_before, today_date)
    return render_template('stock_card.html', stock=stock_data, chart=stock_chart)


@app.route('/crisis_manager', methods=['POST', 'GET'])
def crisis_manager():
    charts_list = []
    crisis_list = [-5, -10, -20, -25, -30]
    f = open('CRISIS_DATA.json', "r")
    crisis_data = json.loads(f.read())

    def filter_crisis_data(crisis_level):
        # Filter Crisis Data by the level of crisis
        filtered_crisis_data = {stock: data for stock, data in crisis_data.items() if data["sum"] < crisis_level and
                                crisis_data[stock]["date"] != "-"}
        return filtered_crisis_data

    def generate_data(crisis_level):
        for stock in crisis_data:
            if crisis_data[stock]["sum"] < crisis_level and crisis_data[stock]["date"] != "-":

                crisis_date_object = dt.strptime(crisis_data[stock]['date'], "%d.%m.%Y").date()
                five_months_ago = (dt.today() - timedelta(days=150)).strftime("%Y-%m-%d")

                data = {
                    "symbol": f'{stock}',
                    "news": yf.Ticker(stock).news,
                }
                NEWS_DATA.add_stock(stock, data)

                # check if the crisis is lower than (-5) or higher
                if crisis_data[stock]["sum"] > -5:
                    title = f"{stock} Last 5 Months Status"
                    charts_list.append(generate_stock_chart(stock, title, five_months_ago, today_date))

                else:
                    # defines a date for review a stock lower than (-5)
                    stock_review_date = crisis_date_object - timedelta(weeks=3)

                    title = f"{stock} Crisis ({crisis_date_object}) Review Since {stock_review_date}"
                    charts_list.append(generate_stock_chart(stock, title, stock_review_date, today_date))

                    # OPTION - define if the crisis began less than two weeks ago or before then that # OPTION
                    #two_weeks_before_today = today_date - timedelta(weeks=2)
                    #str_crisis_date = crisis_date_object.strftime("%d.%m.%Y")
                    #if crisis_date_object >= two_weeks_before_today:
                    #    title = f"{stock} Crisis ({crisis_date_object}) Review Since {two_weeks_before_today}"
                    #    charts_list.append(generate_stock_chart(stock, title, crisis_date_object - timedelta(weeks=3),
                    #                                            today_date))
                    #else:
                    #    print(stock)
                    #    print("me!")
                    #    title = f"{stock} Crisis Review Since {str_crisis_date}"
                    #    charts_list.append(generate_stock_chart(stock, title, crisis_date_object - timedelta(weeks=2),
                    #                                            today_date))

        return crisis_data

    n = open('NEWS_DATA.json', "r")
    news_data = json.loads(n.read())

    if request.method == 'POST':
        user_choice = int(request.form['crisis_level'])
        generate_data(user_choice)

        return render_template('crisis_manager.html', crisis_data=filter_crisis_data(user_choice),
                               news_data=news_data, chart_list=charts_list, user_choice=user_choice,
                               crisis_list=crisis_list, total_items_length=len(STOCK_DATA.get_all_stocks_symbols()))

    generate_data(999)
    return render_template('crisis_manager.html', crisis_data=filter_crisis_data(999),
                           news_data=news_data, chart_list=charts_list, crisis_list=crisis_list,
                           user_choice="-", total_items_length=len(STOCK_DATA.get_all_stocks_symbols()))


@app.route('/delete_stock')
def delete_stock_from_data():
    symbol = request.args.get('symbol')
    STOCK_DATA.remove_stock(symbol)
    CRISIS_DATA.remove_stock(symbol)
    df = pd.read_csv(stocksdata_csv_path)
    df = df.drop(symbol, axis=1)
    df.to_csv(stocksdata_csv_path, index=False)

    if request.args.get('choose_stocks') == "True":
        return redirect(url_for('choose_stocks'))
    return redirect(url_for('stocks'))


@app.route('/delete_temp_stock')
def delete_stock_from_temp_data():
    symbol = request.args.get('symbol')
    TEMP_STOCK_DATA.remove_stock(symbol)
    flash(f"'{symbol}' Removed")

    return redirect(url_for('choose_stocks'))


@app.route('/popup')
def popup():
    return redirect(url_for('stocks'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
