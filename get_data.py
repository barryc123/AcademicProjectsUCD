"""
Functions used in value investing script
"""
from typing import List

import pandas as pd
import requests
from bs4 import BeautifulSoup
import yfinance as yf


def get_list_of_stocks():
    """
    Function to get the list of stocks in S&P500 from Wikipedia
    :return: List of stocks in S&P500
    """
    wiki_table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    # take the first table
    wiki_table = wiki_table[0]
    tickers = wiki_table["Symbol"].to_list()

    return tickers


def get_ratios_data(tickers: List):
    """
    Function that gets the P/E & P/B ratios from Yahoo Finance
    :param: tickers: List of tickers to get ratios data for
    :return: Dataframe of P/B and P/E ratios
    """

    # set empty dataframe
    ratios_df = pd.DataFrame(columns=["Ticker", "Trailing P/E", "P/B"])
    url = "https://finance.yahoo.com/quote/{}/key-statistics?p={}"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
    }
    # loop through each ticker and scrape ratios
    for ticker in tickers:
        soup = BeautifulSoup(requests.get(url.format(ticker, ticker), headers=headers).content, "html.parser")
        for t in soup.select("table"):
            for tr in t.select("tr:has(td)"):
                for sup in tr.select("sup"):
                    sup.extract()
                tds = [td.get_text(strip=True) for td in tr.select("td")]
                if tds[0] == "Trailing P/E":
                    tr_pe_ratio = tds[1]
                elif tds[0] == "Price/Book(mrq)":
                    pb_ratio = tds[1]
                else:
                    pass
            # create list to add to df
            new_row = [ticker, tr_pe_ratio, pb_ratio]
        # add to df
        ratios_df.loc[len(ratios_df)] = new_row

    # Set the tickers column as the index
    ratios_df.set_index('Ticker', inplace=True)

    return ratios_df


def get_missing_ratios(ratios_df):
    """
    Manually calculate P/E or P/B ratios using data from yahoo finance if they are missing
    :param ratios_df: Dataframe P/E and P/B ratios with some missing values
    :return: Dataframe of P/E and P/B ratios
    """
    # Fix the P/E Column
    for stock in ratios_df.loc[ratios_df['Trailing P/E'] == 'N/A'].index:
        # Loop through each ticker
        ticker = yf.Ticker(stock)
        try:
            # get current price
            price = ticker.info['currentPrice']

            # get EPS
            eps = ticker.info['trailingEps']

            # P/E Ratio = Share Price / EPS
            pe_ratio = price / eps

            # Put the value calculated into the table
            ratios_df.loc[stock]['Trailing P/E'] = pe_ratio

        except:
            # If not available, use -1
            ratios_df.loc[stock]['Trailing P/E'] = -1

    # Now fix the P/B column ----
    for stock in ratios_df.loc[ratios_df['P/B'] == 'N/A'].index:
        ticker = yf.Ticker(stock)
        try:
            # get current price
            price = ticker.info['currentPrice']

            # get book value per share
            book_value = ticker.info['bookValue']

            # P/B Ratio = Share Price / Book Value per share
            pb_ratio = price / book_value

            # Put the value calculated into the table
            ratios_df.loc[stock]['P/B'] = pb_ratio
        # if not available, use -1
        except:
            ratios_df.loc[stock]['P/B'] = -1

    # Have to change the type of the values from str to float
    for stock in ratios_df.index:
        try:
            # Changing p/e and p/b ratios to floats
            ratios_df.loc[stock]['Trailing P/E'] = float(ratios_df.loc[stock]['Trailing P/E'])
            ratios_df.loc[stock]['P/B'] = float(ratios_df.loc[stock]['P/B'])

        except:
            # If there is an error it is because the number has k in it, for a thousand
            # as it's a very large number we can change it to -1 as we will disregard it
            ratios_df.loc[stock]['Trailing P/E'] = -1
            ratios_df.loc[stock]['P/B'] = -1

    return ratios_df


def format_ratios_df(ratios_df: pd.DataFrame):
    """
    Format dataframe to change string values to float
    :param ratios_df:
    :return:
    """
    # change the type of the values from str to float
    for stock in ratios_df.index:
        try:
            # Changing p/e and p/b ratios to floats
            ratios_df.loc[stock]['Trailing P/E'] = float(ratios_df.loc[stock]['Trailing P/E'])
            ratios_df.loc[stock]['P/B'] = float(ratios_df.loc[stock]['P/B'])

        except:
            # If there is an error it is because the number has k in it, for a thousand
            # as it's a very large number we can change it to -1 as we will disregard it
            ratios_df.loc[stock]['Trailing P/E'] = -1
            ratios_df.loc[stock]['P/B'] = -1

    return ratios_df


def download_price_data(stock_tickers: List, time_period: str, interval: str):
    """
    Download price data from yahoo finance
    :param stock_tickers: List of tickers to get price data for
    :param time_period: Time period to go back and get data for, e.g. 1d, 2y
    :param interval: Interval period for the data, e.g. 1wk
    :return:
    """
    # need to join the tickers for downloading data
    tickers_joined = " ".join(stock_tickers)

    price_data = yf.download(tickers=tickers_joined, period=time_period, interval=interval)
    price_data = price_data["Adj Close"]
    price_data = price_data.dropna()

    return price_data
