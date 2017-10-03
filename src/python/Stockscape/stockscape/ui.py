#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ui.py.

Convert the data to data for the interactive UI

Created by Chandrasekhar Ramakrishnan on 2017-07-20.
Copyright (c) 2017 Chandrasekhar Ramakrishnan. All rights reserved.
"""

import json

import pandas as pd

from .analysis import Cape, WarrantedReturns
from .returns import StockReturns, BondHoldToMaturityReturns, Inflation


class UiData(object):
    """Convert the data to data for the UI."""

    def __init__(self, stockscape_data):
        self.stockscape_data = stockscape_data
        self.df = self.compute_df(self.stockscape_data)
        self.wr = self.compute_wr(self.stockscape_data)

    def write(self, path):
        df_array = json.loads(self.df.to_json(orient='records'))
        with open(path, 'w') as f:
            json.dump({'data_table': df_array, 'wr_curve': self.wr}, f)

    @staticmethod
    def compute_df(stockscape_data):
        """Return a data frame that can be used by the UI

        :param stockscape_data: The data used to create the frame
        :return: A data frame
        """
        columns = {}
        columns['cape'] = Cape(stockscape_data).df['cape']
        for horizon in range(10, 21):
            augment_horizon_data(columns, stockscape_data, horizon)
        df = pd.DataFrame(columns)
        df['date'] = ["{}-{:02d}".format(d.year, d.month) for d in df.index]
        df = df.reset_index(drop=True)
        return df

    @staticmethod
    def compute_wr(stockscape_data):
        """Return the warranted returns curve for use by the UI.

        :param stockscape_data: The data used to create the frame
        :return: A data frame
        """
        wr_10y = WarrantedReturns(Cape(stockscape_data), StockReturns(stockscape_data))
        return [{'cape': c, 'wr': wr} for c, wr in zip(*wr_10y.warranted_returns_curve())]


def augment_horizon_data(columns, ie_data, horizon):
    stocks = StockReturns(ie_data, horizon)
    bond = BondHoldToMaturityReturns(ie_data, horizon)
    inflation = Inflation(ie_data, horizon)

    columns['stock_{}y'.format(horizon)] = stocks.df['returns']
    columns['stockgross_{}y'.format(horizon)] = stocks.df['gross_returns']
    columns['bond_{}y'.format(horizon)] = bond.df['gs10_returns']
    columns['bondgross_{}y'.format(horizon)] = bond.df['gross_gs10_returns']
    columns['inflation_{}y'.format(horizon)] = inflation.df['forward_inflation']
