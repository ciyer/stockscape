#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
reader.py

Read data from data sources. Currently only support data from Shiller:

  http://www.econ.yale.edu/~shiller/data/ie_data.xls

Created by Chandrasekhar Ramakrishnan on 2016-09-22.
Copyright (c) 2016 Chandrasekhar Ramakrishnan. All rights reserved.
"""

import datetime

import pandas as pd

from .data_series import NominalData, RealStockData, StockscapeData


def _raw_read_shiller_data(path):
    """Internal function to read Shiller data into a frame"""
    df = pd.read_excel(path)
    # The real column headers are in the 6th row
    df.columns = df.iloc[5]
    df.columns.name = None
    # Strip the textual header and tail of the data
    df = df.iloc[6:-1, :]
    df.index = (df.index - 6)
    df['date_dt'] = pd.Series(df.index).apply(ie_index_to_datetime)
    df.set_index('date_dt', inplace=True)
    df = df.apply(lambda x: pd.to_numeric(x, errors='ignore'))
    return df


def read_ie_data(path):
    """Read data from the Irrational Exuberance Excel file published by Shiller.
    :param path: Path to an ie_data file
    :return: A data_series.StockscapeData object
    """
    df = _raw_read_shiller_data(path)
    nominal_data = NominalData(df[['P', 'D', 'E']], df['Rate GS10'])
    real_data = RealStockData(nominal_data, df['CPI'], df.iloc[-1]['CPI'])
    return StockscapeData(real_data, nominal_data)


def ie_index_to_datetime(index):
    """Convert indices in the ie_data file to datetime objects for the start of the period they represent.
    :param index: The index of a row.
    :return: The datetime for for that row
    """
    div, mod = divmod(index, 12)
    return datetime.datetime(1871 + div, mod + 1, 1)
