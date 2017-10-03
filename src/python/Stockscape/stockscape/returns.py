#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
returns.py

Objects for calculating returns.

Created by Chandrasekhar Ramakrishnan on 2017-06-30.
Copyright (c) 2017 Chandrasekhar Ramakrishnan. All rights reserved.
"""

import numpy as np
import pandas as pd


class PeriodUtils(object):
    """Utilities for performing calculations over a period (in years)."""

    def __init__(self, years):
        self.years = years
        self.months = years * 12

    @property
    def annualized_returns(self):
        """Return a function that takes gross returns over years and returns annualized returns."""
        years = self.years
        return np.vectorize(lambda gross_returns: np.power(1 + gross_returns, 1 / years) - 1)

    @property
    def gross_returns(self):
        """Return a function that takes rates returns over years and returns annualized returns."""
        years = self.years
        return np.vectorize(lambda rate: np.power(1 + rate, years) - 1)

    @property
    def warranted_returns(self):
        """Return a function that takes a cape as an estimate and returns the warranted returns."""
        years = self.years
        return np.vectorize(lambda cape: np.power(1 + (1 / cape), years) - 1)


class StockReturns(object):
    """Compute the returns on stocks, both gross and annualized.

    See http://faculty.washington.edu/ezivot/econ424/returnCalculations.pdf
    """

    def __init__(self, stockscape_data, years=10):
        """Initialize the Returns object.
        :param stockscape_data: A data_series.StockscapeData object.
        :param years: The period over which returns are calculated, specified in years. Defaults to 10 years.
        """
        self.data = stockscape_data
        self.years = years
        self.period_utils = PeriodUtils(self.years)
        self.df = self.compute_df(self.data.real_stock_data, self.period_utils)

    @staticmethod
    def compute_df(real_stock_data, period_utils):
        """Compute a frame with real stock returns (annualized and gross).

        Columns in the computed frame are returns (annualized), gross_returns
        :param real_stock_data: The frame with the cape used as a source for data.
        :param period_utils: A period_utils object.
        :return: A frame containing returns and gross_returns.
        """
        df = real_stock_data.df

        months = period_utils.months
        gross_returns = (1 + df['m_return']).rolling(months, 1).apply(np.prod) - 1
        gross_returns = gross_returns.shift(-months)

        returns = period_utils.annualized_returns(gross_returns)

        return pd.DataFrame({'gross_returns': gross_returns, 'returns': returns}, index=df.index)


class Inflation(object):
    """Compute inflation over the period."""

    def __init__(self, stockscape_data, years=10):
        """Initialize the Inflation object.

        :param stockscape_data: A data_series.StockscapeData object.
        :param years: The period over which inflation is calculated, specified in years. Defaults to 10 years.
        """
        self.data = stockscape_data
        self.years = years
        self.period_utils = PeriodUtils(self.years)
        self.df = self.compute_df(self.data.real_stock_data.cpi_s, self.period_utils)

    @staticmethod
    def compute_df(cpi_s, period_utils):
        """Compute a frame with inflation.

        Columns in the computed frame are forward_inflation (that's it for now).
        :param cpi_s: The series with the consumer price index data
        :param period_utils: A period_utils object
        :return: A frame containing forward_inflation
        """
        months = period_utils.months
        forward_inflation = period_utils.annualized_returns(cpi_s.diff(-months) * -1 / cpi_s)
        return pd.DataFrame({'forward_inflation': forward_inflation}, index=cpi_s.index)


class BondHoldToMaturityReturns(object):
    """Compute the returns on bonds if held to maturity.

    For alternatives, see http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html
    """

    def __init__(self, stockscape_data, years=10):
        """Initialize the BondHoldToMaturityReturns object.
        :param stockscape_data: A data_series.StockscapeData object.
        :param years: The period over which returns are calculated, specified in years. Defaults to 10 years.
        """
        self.data = stockscape_data
        self.years = years
        self.period_utils = PeriodUtils(self.years)
        self.df = self.compute_df(self.data.nominal_data.gs10_s, self.data.real_stock_data.cpi_s, self.period_utils)

    @staticmethod
    def compute_df(gs10_s, cpi_s, period_utils):
        """Compute a frame with real bond returns (annualized and gross).

        Columns added to cape_df are gs10_returns (annualized), gross_gs10_returns
        :param gs10_s: The series with the 10-year T-Bond yield data
        :param cpi_s: The series with the consumer price index data
        :param period_utils: A period utils object.
        :return: A frame containing gs10_returns and gross_gs10_returns
        """
        months = period_utils.months
        gs10_gross_nominal = period_utils.gross_returns(gs10_s)
        forward_price_correction = cpi_s.shift(-months) / cpi_s
        gs10_gross = ((gs10_gross_nominal + 1) / forward_price_correction) - 1
        gs10_returns = period_utils.annualized_returns(gs10_gross)

        return pd.DataFrame({'gross_gs10_returns': gs10_gross, 'gs10_returns': gs10_returns}, index=gs10_s.index)


class WaitingReturns(object):
    def __init__(self, ie_data, horizons=[10, 15, 20], waits=range(1, 4)):
        """Compute returns over horizons years from waiting waits years."""
        self.ie_data = ie_data
        self.horizons = horizons
        self.waits = waits
        self.horizon_df = None
        self.inflation_df = None
        self.wait_dfs = None
        self.initialize_horizon_df()
        self.initialize_inflation_df()
        self.initialize_wait_dfs()

    def initialize_horizon_df(self):
        min_horizon = min(self.horizons) - max(self.waits)
        max_horizon = max(self.horizons) + 1
        horizons = {h: StockReturns(self.ie_data, h).df['gross_returns'] for h in
                    range(min_horizon, max_horizon)}
        self.horizon_df = pd.DataFrame(horizons)

    def initialize_inflation_df(self):
        inflation = {w: Inflation(self.ie_data, w).df['forward_inflation'] for w in self.waits}
        self.inflation_df = pd.DataFrame(inflation)

    def horizon_wait_returns(self, horizon, wait):
        return ((1 - self.inflation_df[wait]) *
                self.horizon_df[horizon - wait].shift(-12 * wait)) - self.horizon_df[horizon]

    def initialize_wait_dfs(self):
        def wait_n_df(horizon):
            return pd.DataFrame({wait: self.horizon_wait_returns(horizon, wait) for wait in self.waits})

        self.wait_dfs = [wait_n_df(horizon) for horizon in self.horizons]

    @property
    def diff_limits(self):
        return [min([df.min().min() for df in self.wait_dfs]), max([df.max().max() for df in self.wait_dfs])]
