"""
Run this script to get the data and save it to sqlite database.
Subsequent runs do not need to gather data again, can simply read the data saved in
the sqlite database.
"""

from get_data import get_list_of_stocks, get_ratios_data, get_missing_ratios, format_ratios_df
from Smurfit.ValueInvesting.sqlite_handling import create_database, add_many, delete_negatives

# set global variables
DATABASE_NAME = "ratios_data.db"


def main():
    # get list of S&P500 tickers
    print("Getting list of tickers")
    SP500_tickers = get_list_of_stocks()
    print("Got list of tickers")

    print("Getting P/E and P/B ratios")
    # get P/E and P/B ratios for given tickers
    ratios_df = get_ratios_data(tickers=SP500_tickers)
    print("Got P/E and P/B ratios")

    # fill in missing P/E or P/B value if they exist
    if "N/A" in ratios_df.values:
        print("Some ratios were missing")
        print("Manually getting values")
        ratios_df = get_missing_ratios(ratios_df=ratios_df)
        print("Manually got the values")

    # format df
    print("Formatting ratios dataframe")
    ratios_df = format_ratios_df(ratios_df=ratios_df)
    print("Formatting done")

    # create the database to store the ratios data
    print("Creating sqlite database")
    create_database(database_name=DATABASE_NAME)
    print("sqlite database created")

    # Get each line of the dataframe into a list of list - for adding to database
    ratios_list = list(ratios_df.itertuples(index=True, name=None))

    # add data to sqlite database
    print("Adding data to sqlite database")
    add_many(database_name=DATABASE_NAME, tickers_list=ratios_list)
    print("Added to database")

    # --------- add in 'if statement' here check to see
    # delete records where P/E or P/B ratios <= 0
    print("Deleting unwanted records if any")
    delete_negatives(database_name=DATABASE_NAME)
    print("Deleted unwanted records")
    print("Script done")
    pass


if __name__ == "__main__":
    main()
