"""Package for analyzing stock returns using the CAPE framework from Robert Shiller."""

from .reader import read_ie_data
from .returns import BondHoldToMaturityReturns, Inflation, StockReturns, WaitingReturns
from .analysis import Cape, CapeNeighborsEstimator, WarrantedReturns
from .ui import UiData

__author__ = 'Chandrasekhar Ramakrishnan <ciyer@illposed.com>'
__version__ = '0.9.1'
