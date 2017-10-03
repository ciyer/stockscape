#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
conftest.py

Code that supports tests that use the serialized search results as a fixture.

Created by Chandrasekhar Ramakrishnan on 2016-08-31.
Copyright (c) 2016 Chandrasekhar Ramakrishnan. All rights reserved.
"""

import os

import pytest


@pytest.fixture(scope="session")
def test_data_folder_path():
    module_path = os.path.dirname(__file__)
    return os.path.join(os.path.dirname(module_path), "..", "..", "..", "data")


# noinspection PyShadowingNames
@pytest.fixture(scope="session")
def shiller_excel_data_path(test_data_folder_path):
    return os.path.join(test_data_folder_path, "ie_data.xls")
