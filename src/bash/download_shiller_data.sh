#!/usr/bin/env bash

pushd .

SCRIPT_DIR=$(dirname "$0")
cd "${SCRIPT_DIR}/../../data"

curl -O http://www.econ.yale.edu/~shiller/data/ie_data.xls

popd