#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
data_series.py

Classes for manipulating the data series.

Created by Chandrasekhar Ramakrishnan on 2016-09-22.
Copyright (c) 2016 Chandrasekhar Ramakrishnan. All rights reserved.
"""

import pandas as pd


class NominalData(object):
    """Holds onto series and frames containing data in nominal units."""

    def __init__(self, stocks_df, gs10_s):
        """Initialize the NominalPriceData object.
        All frames and series should be indexed by a timestamp representing the start of the period for the row.
        :param stocks_df: A frame of nominal stock price, dividend, and earnings data.
        :param gs10_s: A series with the nominal yield in percent for 10-year treasury bonds.
        """
        self.stocks_df = stocks_df
        self.gs10_s = gs10_s / 100


class RealStockData(object):
    """Convert stock data in nominal units to real data.

    The resulting frame contains:
    - price (real)
    - dividend (real)
    - earnings (real)
    - m_return (real) (monthly return)
    """

    def __init__(self, nominal_data, cpi_s, base_price_level):
        """
        :param nominal_data: A nominal data object.
        :param cpi_s: A series with CPI data, (pandas-)indexed the same as the nominal data.
        :param base_price_level: The base price level representing 1.
        """
        self.nominal_data = nominal_data
        self.cpi_s = cpi_s
        self.base_price_level = base_price_level
        self.df = None
        self._compute_df()

    def _compute_df(self):
        df = self._real_dollar_df()
        df = self._enrich_with_real_monthly_return(df)
        # Remove the nominal-unit columns
        del df['P']
        del df['D']
        del df['E']
        self.df = df

    def _real_dollar_df(self):
        """Return a frame with real values for stock data in the fields price, dividend, and earnings.

        Take the nominal-units data and use CPI data to convert to real units.
        Return the original frame augmented with the real values.
        """
        stocks_df = self.nominal_data.stocks_df
        bpl = self.base_price_level
        cpi = self.cpi_s
        inflation_scale = bpl / cpi
        price = pd.to_numeric(stocks_df['P']) * inflation_scale
        dividend = pd.to_numeric(stocks_df['D']) * inflation_scale
        earnings = pd.to_numeric(stocks_df['E']) * inflation_scale
        return stocks_df.assign(price=price, dividend=dividend, earnings=earnings)

    @staticmethod
    def _enrich_with_real_monthly_return(df):
        """Take a frame with real price, dividend, and earnings and augment with monthly (real) returns."""
        m_return = (df['price'].diff() + (df['dividend'] / 12)) / df['price'].shift(1)
        return df.assign(m_return=m_return)


# noinspection SpellCheckingInspection
class StockscapeData(object):
    """An object for collecting together data for the analysis."""

    def __init__(self, real_stock_data, nominal_data):
        self.real_stock_data = real_stock_data
        self.nominal_data = nominal_data
