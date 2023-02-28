#!/bin/bash

# Run this once a week to update 'how weird is the weather' data.

# Set these environment variables to specify where to download and where
# to process data files.
# (some tricky bash to give variable a default value if not set)
: ${CDS_DOWNLOAD_DIR:='.'}
: ${DATA_OUTPUT_DIR:='.'}
: ${CDSTOOL_DIR:=.}

# Start from the current year, or from $CDS_START_YEAR if it is already set
: ${CDS_START_YEAR:=$(date +%Y)}

set -e
# Download the latest Copernicus CDS data from $CDS_START_YEAR forward.
python3 ${CDSTOOL_DIR}/cdstool.py --startyear ${CDS_START_YEAR} --output "$CDS_DOWNLOAD_DIR"

# Process the data into our custom netcdfs and then into the wxdb
python3 ${CDSTOOL_DIR}/tiletool.py --start ${CDS_START_YEAR} --update --input "$CDS_DOWNLOAD_DIR" --output "$DATA_OUTPUT_DIR"
