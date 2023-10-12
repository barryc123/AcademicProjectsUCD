"""
Functions used to clean gathered data and select 'value stocks'
"""
import math
import re
from typing import List, Tuple

import numpy as np
import pandas as pd
from textblob import TextBlob


def calculate_figures(ratios_df: pd.DataFrame) -> Tuple:
    """
    Calculate values for number of remaining stocks, tenth and ninetieth percentiles
    :param: ratios_df: Dataframe of tickers and their P/E and P/B ratios
    :return: Tuple of num stocks remaining, tenth and ninetieth percentiles
    """
    num_remaining_stocks = len(ratios_df.index)
    ten_perc = math.ceil(num_remaining_stocks * 0.1)
    ninety_perc = math.ceil(num_remaining_stocks * 0.9)

    return num_remaining_stocks, ten_perc, ninety_perc


def get_low_pe_pb_stocks(ratios_df: pd.DataFrame, ten_perc_value: float | int) -> List:
    """
    Get list of stocks with low P/E and P/B ratios
    :param: ratios_df: Dataframe of tickers and their P/E and P/B ratios
    :param: ten_perc_value: Value of tenth percentile
    :return: List of tickers with low P/E and P/B ratios
    """
    # Lowest 10% P/E ratios
    ratios_df = ratios_df.sort_values("PE")
    low_pe_stocks = []
    for stock in ratios_df.index[:ten_perc_value]:
        low_pe_stocks.append(stock)

    # Lowest 10% p/b stocks
    ratios_df = ratios_df.sort_values("PB")
    low_pb_stocks = []
    for stock in ratios_df.index[:ten_perc_value]:
        low_pb_stocks.append(stock)

    low_pe_and_pb_stocks = list(set(low_pe_stocks).intersection(low_pb_stocks))

    return low_pe_and_pb_stocks


def get_high_pe_pb_stocks(ratios_df: pd.DataFrame, ninetieth_perc_value: float | int) -> List:
    """
    Get list of stocks with high P/E and P/B ratios
    :param: ratios_df: Dataframe of tickers and their P/E and P/B ratios
    :param: ninetieth_perc_value: Value of ninetieth percentile
    :return: List of tickers with high P/E and P/B ratios
    """
    # Highest 10% P/E ratios
    ratios_df = ratios_df.sort_values("PE")
    high_pe_stocks = []
    for stock in ratios_df.index[ninetieth_perc_value:]:
        high_pe_stocks.append(stock)

    # Highest 10% P/E stocks
    ratios_df = ratios_df.sort_values("PB")
    high_pb_stocks = []
    for stock in ratios_df.index[ninetieth_perc_value:]:
        high_pb_stocks.append(stock)

    high_pe_and_pb_stocks = list(set(high_pe_stocks).intersection(high_pb_stocks))

    return high_pe_and_pb_stocks


def calculate_returns(price_data: pd.DataFrame) -> pd.DataFrame:
    """
    Turn dataframe of prices into a dataframe of returns
    :param price_data: Dataframe of prices
    :return: Dataframe of returns data
    """
    returns = np.log(price_data / price_data.shift(1))
    returns = returns.dropna()

    return returns


def clean_tweet(tweet):
    """Function to clean a tweet"""
    twt = re.sub('\\n', '', tweet)  # removes the '\n' string
    twt = re.sub('https?:\/\/\S+', '', twt)  # removes any hyperlinks
    return twt


def get_subjectivity(tweet):
    """Function to get subjectivity"""
    return TextBlob(tweet).sentiment.subjectivity


def get_polarity(tweet):
    return TextBlob(tweet).sentiment.polarity


def get_sentiment(score):
    """Function to easily see sentiment text"""
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'

