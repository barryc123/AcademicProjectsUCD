import sqlite3 as lite
from typing import List

import pandas as pd


def create_database(database_name: str):
    """
    Create sqlite database
    :param: database_name: Name of database to be created
    :return: None
    """
    # create sqlite database
    con = lite.connect(database_name)
    curs = con.cursor()

    curs.execute(""" DROP TABLE IF EXISTS ratio
        """)

    curs.execute(""" CREATE TABLE ratio ( 
            Tickers text,
            PE real,
            PB real
        )""")
    con.commit()
    con.close()
    pass


def add_many(database_name: str, tickers_list: List):
    """
    Add data to existing sqlite database
    :param: database_name: Name of database to connect and add data to
    :param: tickers_list: List of list, with each list a row in the ratios dataframe
    :return: None
    """
    con = lite.connect(database_name)
    curs = con.cursor()
    curs.executemany("INSERT INTO ratio VALUES (?, ?, ?)", tickers_list)
    con.commit()
    con.close()
    pass


def delete_negatives(database_name: str):
    """
    Delete records in the sqlite database where P/E or P/B ratios <=0
    :param database_name: Name of database where data is stored
    :return: None
    """
    con = lite.connect(database_name)
    curs = con.cursor()
    # Delete Records
    curs.execute("DELETE from ratio WHERE PE <= 0 OR PB <= 0")
    con.commit()
    con.close()
    pass


def get_existing_data(database_file_path: str):
    """
    Get the existing ratio data that is saved in sqlite database
    :param database_file_path: File path of sqlite database (incl. file name)
    :return: Dataframe of ratios data
    """
    con = lite.connect(database_file_path)
    ratios_df = pd.read_sql_query("SELECT * FROM ratio", con)
    con.close()

    ratios_df = ratios_df.set_index("Tickers")

    return ratios_df
