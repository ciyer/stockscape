#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
analysis.py

Classes for analyzing stock and bond returns.

Created by Chandrasekhar Ramakrishnan on 2017-06-30.
Copyright (c) 2017 Chandrasekhar Ramakrishnan. All rights reserved.
"""

import numpy as np
import pandas as pd
from scipy import stats as st


class Cape(object):
    """Compute the CAPE (Cyclically-Adjusted Price/Earnings ratio)"""

    def __init__(self, stockscape_data, years=10, summary='mean'):
        """Initialize the Cape object.
        :param stockscape_data: A data_series.StockscapeData object.
        :param years: The period to look at when computing CAPE, specified in years. Defaults to 10 years.
        :param summary: The summary statistic to use: 'mean' or 'median'. Default is 'mean'.
        """
        self.data = stockscape_data
        self.years = years
        self.summary = summary
        self.df = self.compute_df(self.data.real_stock_data, self.years, self.summary)

    @staticmethod
    def compute_df(real_stock_data, years=10, summary='mean'):
        """Return a data frame, indexed by date, with columns for analysis.

        Columns in the returned frame are cape.

        CAPE is computed using the mean P/E ratio over the period years.
        :param real_stock_data: The real-dollars-denominated stock data used as the basis for this calculation.
        :param years: The period to look at, specified in years.
        :param summary: The summary statistic to use: 'mean' or 'median'. Default is 'mean'.
        :return:
        """
        df = real_stock_data.df
        months = years * 12
        # Use the past months of earnings but do not include the current month in the CAPE calculation.
        if summary == 'mean':
            earnings = df.rolling(months, 1).mean()['earnings'].shift(1)
        else:
            earnings = df.rolling(months, 1).median()['earnings'].shift(1)
        earnings = earnings.drop(earnings.index[0:months])

        df = df.assign(cape=df['price'] / earnings)
        return df


class WarrantedReturns(object):
    """Compute warranted returns assuming the efficient-market hypothesis."""

    def __init__(self, cape, stock_returns):
        """
        :param cape: A Cape object used for computing warranted returns.
        :param stock_returns: A stock_returns object used for computing error against warranted returns.
        """
        self.cape = cape
        self.stock_returns = stock_returns
        self.df = self.compute_df(cape, stock_returns, self.period_utils)

    @staticmethod
    def compute_df(cape, stock_returns, period_utils):
        """Compute a frame with EMH-warranted returns (annualized and gross) and error between warranted returns and actual returns.

        Columns in the returned frame are gross_warranted_returns, warranted_returns (annualized)
                              gross_wr_error, wr_error (annualized)

        :param cape: A Cape object with the CAPE calculation
        :param stock_returns: A returns.StockReturns object with the returns
        :param period_utils: A period utils object.
        :return:
        """
        gwr = period_utils.warranted_returns(cape.df['cape'])
        wr = period_utils.annualized_returns(gwr)
        gross_wr_error = stock_returns.df['gross_returns'] - gwr
        wr_error = stock_returns.df['returns'] - wr

        return pd.DataFrame({'gross_warranted_returns': gwr, 'warranted_returns': wr,
                             'gross_wr_error': gross_wr_error, 'wr_error': wr_error})

    @property
    def period_utils(self):
        return self.stock_returns.period_utils

    def gross_warranted_returns_curve(self):
        """Return a tuple of range and values for the gross warranted returns."""
        cape_range = np.linspace(self.cape.df['cape'].min(), self.cape.df['cape'].max())
        gwr = self.period_utils.warranted_returns(cape_range)
        return cape_range, gwr

    def warranted_returns_curve(self):
        """Return a tuple of range and values for the warranted returns."""
        cape_range, gwr = self.gross_warranted_returns_curve()
        return cape_range, self.period_utils.annualized_returns(gwr)


class CapeNeighborsEstimator(object):
    """Factory for building CapeNeighborsPredictor objects"""

    def __init__(self, cape):
        """
        :param cape: A Cape object used for determining neighbors.
        """
        self.cape = cape
        self.df = self.compute_difference_matrix(cape)

    def fit(self, df, column, max_neighbors=20):
        """Return a predictor that can be used to predict values.
        :param df: The frame (indexed by date) that we use for prediction -- values to predict are those that are nan.
        :param column: The column we want to predict
        :param max_neighbors: The maxiumum number of neighbors that will be used
        :return: A CapeNeighborsPredictor
        """

        return CapeNeighborsPredictor(self, df, column, max_neighbors)

    @staticmethod
    def compute_difference_matrix(cape):
        """Compute a frame differences of CAPE values.

        :param cape: A Cape object with the CAPE calculation
        :return:
        """
        cape_ser = cape.df['cape'].dropna()
        # Alternative implementation
        # diff_mtx = pd.DataFrame(cape_ser.values - cape_ser.values[:, np.newaxis]).head()
        diff_mtx = pd.DataFrame(np.subtract.outer(*[cape_ser.values] * 2))

        # Fix the row and column names
        diff_mtx.index = cape_ser.index
        diff_mtx.columns = cape_ser.index
        return diff_mtx


class CapeNeighborsPredictor(object):
    """Predict values from CAPE-neighbors."""

    def __init__(self, estimator, df, column, max_neighbors=20):
        """
        :param estimator: A CapeNeighborsEstimator object used for determining neighbors.
        :param df: The frame (indexed by date) that we use for prediction -- values to predict are those that are nan.
        :param column: The column we want to predict
        :param max_neighbors: The maxiumum number of neighbors that will be used
        """
        self.estimator = estimator
        self.source_df = df
        self.column = column
        self.max_neighbors = max_neighbors
        self.template_df = df[np.isnan(df[column])]
        self.neighbors_dict = self.compute_neighbors_dict(estimator.df, self.template_df, max_neighbors)

    @staticmethod
    def compute_neighbors_dict(cape_diff_df, template_df, max_neighbors):
        """Compute a frame with predictions for future stock returns.

        Return a frame with the same index and the following columns: For each group:
            min, ci_95_min, returns, ci_95_max, max.

        :param cape_diff_df: A cape difference matrix
        :param template_df: The frame to predict
        :param column: The column to predict
        :param max_neighbors: The maximum number of neighbors
        :return:
        """

        nearest_dates_dict = {}

        # Drop columns I need to predict from the data used to predict
        diff_mtx = cape_diff_df.drop(template_df.index, axis=1)

        for d in template_df.index:
            nearest = np.abs(diff_mtx.loc[d]).sort_values()[0:max_neighbors]
            nearest_dates_dict[d.to_datetime64()] = nearest

        return nearest_dates_dict

    def predict(self, number_of_neighbors=None, transform=None, result_col_name=None):
        """Compute a frame with predictions for future stock returns.

        Columns are grouped by number of neighbors used. For each group:
            min, ci_95_min, returns, ci_95_max, max.

        :param number_of_neighbors: An array with the number of neighbors, defaults to just [self.max_neighbors]
        :param transform: An optional transform applied to the result values
        :param result_col_name: The name of the results column, defaults to self.column
        :return: A data frame with the predicted values
        """

        if not number_of_neighbors:
            number_of_neighbors = [self.max_neighbors]
        if not hasattr(number_of_neighbors, "__iter__"):
            number_of_neighbors = [number_of_neighbors]
        if not result_col_name:
            result_col_name = self.column
        estimates = []
        apply_multiindex = len(number_of_neighbors) > 1
        for nc in number_of_neighbors:
            predict = self.predictor_func(nc, transform, result_col_name)
            estimate = self.template_df.apply(predict, axis=1)
            if apply_multiindex:
                estimate.columns = pd.MultiIndex.from_product([[nc], estimate.columns], names=['neighbors', 'stat'])
            estimates.append(estimate)

        return pd.concat(estimates, axis=1).sort_index(axis=1)

    def predictor_func(self, neighor_count, transform, result_col_name):
        """Return a function that predicts a value from the nearest neighbors"""

        def predict(x):
            neighbors = self.source_df.loc[self.neighbors_dict[x.name.to_datetime64()].index, self.column][
                        0:neighor_count]
            gross = neighbors.mean()
            ci = st.t.interval(0.95, len(neighbors) - 1, loc=gross, scale=st.sem(neighbors))
            results = [neighbors.min(), ci[0], gross, ci[1], neighbors.max()]
            if transform:
                results = transform(results)
            return pd.Series(results, ['min', 'ci_min', result_col_name, 'ci_max', 'max'], np.float64)

        return predict
