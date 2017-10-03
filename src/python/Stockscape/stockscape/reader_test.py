#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
reader_test.py


Created by Chandrasekhar Ramakrishnan on 2016-09-22.
Copyright (c) 2016 Chandrasekhar Ramakrishnan. All rights reserved.
"""

from . import reader
from . import analysis, returns, ui
import numpy as np


# noinspection PyProtectedMember,SpellCheckingInspection
def test_price_calculation(shiller_excel_data_path):
    """Compare the calculated price to the one provided by Shiller"""

    shiller_df = reader._raw_read_shiller_data(shiller_excel_data_path)
    assert shiller_df is not None
    data = reader.read_ie_data(shiller_excel_data_path)
    df = data.real_stock_data.df
    assert df['earnings'].dtype == np.float64
    # If this test fails here it's probably because the structure
    # of the Shiller Excel file has changed. You may need to fix the reading code in
    # _raw_read_shiller_data
    assert (shiller_df['Price'] - df['price'] < 0.00001).all()
    assert (shiller_df['Dividend'].dropna() - df['dividend'].dropna() < 0.00001).all()
    assert (shiller_df['Earnings'].dropna() - df['earnings'].dropna() < 0.00001).all()

    cape = analysis.Cape(data)
    assert len(shiller_df['CAPE'].dropna()) == len(cape.df['cape'].dropna())
    assert (shiller_df['CAPE'].dropna() - cape.df['cape'].dropna() < 0.00001).all()
    cape.df.iloc[0].name.strftime("%Y-%m-%d") == '1871-01-01'

    stock_returns = returns.StockReturns(data)
    assert stock_returns.df.loc['2005-05', 'returns'][0] - 0.060458 < 0.00001

    wr = analysis.WarrantedReturns(cape, stock_returns)
    curve = wr.warranted_returns_curve()
    assert curve[0] is not None
    assert curve[1] is not None
    assert wr.df.loc['2005-05', 'warranted_returns'][0] - 0.038986 < 0.00001

    gs10 = returns.BondHoldToMaturityReturns(data)
    assert gs10.df.loc['2005-05', 'gs10_returns'][0] - 0.020622 < 0.00001

    inflation = returns.Inflation(data)
    assert inflation.df.loc['2005-05', 'forward_inflation'][0] - 0.020358 < 0.00001

    cape_estimator = analysis.CapeNeighborsEstimator(cape)
    cape_predictor = cape_estimator.fit(stock_returns.df, 'gross_returns')
    predict_df = cape_predictor.predict([5, 20], stock_returns.period_utils.annualized_returns, 'returns')
    assert abs(predict_df.loc['2017-05', (5, 'min')][0] - -0.001264) < 0.00001
    assert abs(predict_df.loc['2017-05', (5, 'ci_min')][0] - -0.004987) < 0.00001
    assert abs(predict_df.loc['2017-05', (5, 'returns')][0] - 0.028511) < 0.00001
    assert abs(predict_df.loc['2017-05', (5, 'ci_max')][0] - 0.054371) < 0.00001
    assert abs(predict_df.loc['2017-05', (5, 'max')][0] - 0.051764) < 0.00001

    assert abs(predict_df.loc['2017-05', (20, 'min')][0] - -0.011518) < 0.00001

    # If we only provide on number of neighbors, then we get a single-level column index
    predict_df = cape_predictor.predict(5, stock_returns.period_utils.annualized_returns, 'returns')
    assert abs(predict_df.loc['2017-05', 'min'][0] - -0.001264) < 0.00001
    assert abs(predict_df.loc['2017-05', 'returns'][0] - 0.028511) < 0.00001
    assert abs(predict_df.loc['2017-05', 'max'][0] - 0.051764) < 0.00001


def test_export(tmpdir, shiller_excel_data_path):
    data = reader.read_ie_data(shiller_excel_data_path)
    ui.UiData(data).write(str(tmpdir.join("test.json")))
