#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
dsr.py

Utilities for the DeLong-Shiller Redux (dsr).

Created by Chandrasekhar Ramakrishnan on 2017-10-02.
Copyright (c) 2017 Chandrasekhar Ramakrishnan. All rights reserved.
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

import statsmodels.formula.api as smf


def time_ticks(hop=10, start=1880, end=2020):
    """Standard tick points for DSR visualizations"""
    return [str(y) for y in np.arange(start, end, hop)]


def periods_from_df(time_df):
    """Take a frame and return a breakdown of the consecutive periods represented in the frame."""
    period = [time_df.index[0]]
    periods = [period]
    all_period_years = [time_df.index[0]]
    for i in range(1, len(time_df.index)):
        all_period_years.append(time_df.index[i])
        if time_df.index[i - 1] + 1 == time_df.index[i]:
            period.append(time_df.index[i])
        else:
            period = [time_df.index[i]]
            periods.append(period)
    period_labels = ["{}-{}".format(p[0], p[-1]) for p in periods]
    return all_period_years, [(p, pl) for p, pl in zip(periods, period_labels)]


def cite_source(ax):
    ax.annotate('Source: Robert Shiller', (1, 0), (-2, -30), fontsize=8,
                xycoords='axes fraction', textcoords='offset points', va='bottom', ha='right')


def split_to_and_since_delong(df):
    """Split the frame into time periods that DeLong analyzed and those since his article.
    :param df: The frame to split
    :return: Tuple with (to_delong, since_delong)
    """

    to_delong_index = [d for d in df.index if d.year <= 2004 and d.month < 6]
    since_delong_index = [d for d in df.index if d.year > 2004 or (d.year is 2004 and d.month >= 6)]
    return df.loc[to_delong_index], df.loc[since_delong_index]


def latest_index_label(ser_of_df):
    """Return a string for the latest date in the ser_of_df.
    :param ser_of_df: The series or frame to process
    :return: String (month(short) 'YY) for the date
    """

    return ser_of_df.dropna().index[-1].strftime("%b '%y").lower()


def split_cape_threshold_years(df, threshold=25, period_col='period'):
    """Split the df into those years above (or equal) and years below the CAPE threshold.
    In addition to splitting, add a columns labels the period.
    :param df: The data frame to apply the threshold to
    :param threshold: Defaults to 25
    :return: (above_threshold with period and year columns, below_threshold)
    """
    above_threshold = pd.DataFrame(df[df['cape'] >= threshold], copy=True)
    above_threshold['year'] = [i.year for i in above_threshold.index]
    above_threshold_years = above_threshold.groupby('year').count()
    above_threshold_years = above_threshold_years[above_threshold_years['price'] > 1]
    above_threshold_period_years, above_threshold_periods_and_labels = periods_from_df(above_threshold_years)
    for period, label in above_threshold_periods_and_labels:
        above_threshold.loc[above_threshold['year'].isin(period), period_col] = label
    all_high_cape_period_years_set = set(above_threshold_period_years)
    below_threshold = df.loc[[d for d in df.index if d.year not in all_high_cape_period_years_set]]
    return above_threshold, below_threshold


def loss_indices(*dfs):
    """Return the indices where any of the dfs experienced losses.
    :param dfs: The data frames to analyze
    :return: Unique indices in which some df had a loss
    """
    li = np.concatenate([np.array(df[df['returns'] < 0].index) for df in dfs])
    return np.unique(li)


def inversion_indices(df1, df2, column):
    """Return the indices in which df1[column] > df2[column]
    :param df1: A data frame
    :param df2: Another data frame
    :param column: A shared column
    :return: The indices where df1[column] > df2[column]
    """
    return df1[df1[column] > df2[column]].index


class DsrStylePrefs(object):
    """Utility class for styles/preferences/palettes"""

    def __init__(self):
        self.figure_full_size = (10.0, 7.5)
        self.figure_medium_size = (8.0, 5.5)
        self.figure_small_size = (8.0, 3.75)

        self.s_palette = sns.color_palette('Blues_r')[0:4]
        self.b_palette = sns.color_palette('Purples_r')[0:4]
        l_palette = sns.color_palette('Dark2')
        self.l_palette = [l_palette[i] for i in [1, 5, 3, 4, 0]]

    def use(self):
        """Applies styling to matplotlib """
        if 'ciyer' in mpl.style.available:
            plt.style.use(['seaborn-darkgrid', 'ciyer'])
        plt.rcParams["figure.figsize"] = self.figure_full_size


class LinearModel(object):
    """Bundle the relevant information from a linear regression."""

    def __init__(self, ind, dep, df, pred_range):
        """Build a linear model of data
        :param ind: Independent variable
        :param dep: Dependent variable
        :param df: The frame to fit the model against
        :param pred_range: The range to predict on.
        """
        self.ind = ind
        self.dep = dep
        self.df = df
        self.pred_range = pred_range
        self.lm = None
        self.predictions = None

    def fit_and_predict(self):
        self.lm = smf.ols(formula="{} ~ {}".format(self.dep, self.ind), data=self.df).fit()
        preds_input = pd.DataFrame({self.ind: self.pred_range})
        self.predictions = self.lm.predict(preds_input)
        return self

    @property
    def x_intercept(self):
        return (-1 * self.lm.params[0]) / self.lm.params[1]

    @property
    def rsquared(self):
        return self.lm.rsquared

    @property
    def rsquared_computed(self):
        """Compute rsquared from the data"""
        preds_input = pd.DataFrame({'cape': self.df[self.ind]})
        preds = self.lm.predict(preds_input)
        ss_res = np.sum(np.power((self.df[self.dep] - preds).dropna(), 2))
        dep_mean = self.df[self.dep].mean()
        ss_tot = np.sum(np.power((self.df[self.dep] - dep_mean).dropna(), 2))
        return 1 - (ss_res / ss_tot)
