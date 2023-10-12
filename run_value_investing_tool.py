"""
Run the value investing analysis tool, using data that has already been gathered
"""
import os

import pandas as pd

from Smurfit.ValueInvesting.predictive_modelling import prophet_price_prediction
from Smurfit.ValueInvesting.twitter import twitter_analysis
from sqlite_handling import get_existing_data
from clean_data import calculate_figures, get_low_pe_pb_stocks, get_high_pe_pb_stocks, calculate_returns
from get_data import download_price_data

DB_FILE_PATH = os.path.join(r"C:Users\barry\Python\Smurfit\ValueInvesting", "ratios_data.db")
TIME_PERIOD = "5y"
INTERVAL = "1wk"


def main():
    # get the existing data from database
    ratios_df = get_existing_data(database_file_path=DB_FILE_PATH)

    num_remaining_stocks, ten_perc, ninety_perc = calculate_figures(ratios_df=ratios_df)

    # Get list of stocks that have the lowest 10% P/E and lowest 10% P/B
    low_pe_and_pb_stocks = get_low_pe_pb_stocks(ratios_df= ratios_df, ten_perc_value=ten_perc)
    # Get list of stocks that have the highest 10% P/E and lowest 10% P/B
    high_pe_and_pb_stocks = get_high_pe_pb_stocks(ratios_df=ratios_df, ninetieth_perc_value=ninety_perc)

    # download price data for last 5 years for value stocks
    value_stocks_price_data = download_price_data(stock_tickers=low_pe_and_pb_stocks, time_period=TIME_PERIOD,
                                                  interval=INTERVAL)
    # transform prices to returns
    value_stocks_returns_data = calculate_returns(price_data=value_stocks_price_data)

    # download price data for last 5 years for overvalued stocks
    overvalued_stocks_price_data = download_price_data(stock_tickers=high_pe_and_pb_stocks, time_period=TIME_PERIOD,
                                                       interval=INTERVAL)
    # transform prices to returns
    overvalued_stocks_returns_data = calculate_returns(price_data=overvalued_stocks_price_data)

    # perform sentiment analysis using TextBlob and data from Twitter API
    twitter_data = twitter_analysis(tickers=low_pe_and_pb_stocks,
                                    start_time=pd.Timestamp.now() - pd.Timedelta(INTERVAL),
                                    end_time=pd.Timestamp.now()
                                    )

    # plot the predictions of chosen stocks using prophet module
    prophet_price_prediction(sentiment_df=twitter_data, ratios_df=ratios_df)


if __name__ == "__main__":
    main()
