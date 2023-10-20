#!/bin/bash

# Run this once a week to update 'how weird is the weather' data.
tool=$1

# Set these environment variables to specify where to download and where
# to process data files.
# (some tricky bash to give variable a default value if not set)
: ${CDS_DOWNLOAD_DIR:='.'}
: ${DATA_OUTPUT_DIR:='.'}
: ${CDS_TOOL_DIR:=.}

# Start from the current year, or from $CDS_START_YEAR if it is already set
: ${CDS_START_YEAR:=$(date +%Y)}
: ${CDS_END_YEAR:=$(date +%Y)}

set -e
if [[ "${tool}" == "cdstool" ]]; then
    # Download the latest Copernicus CDS data from $CDS_START_YEAR forward.
    python3 ${CDS_TOOL_DIR}/cdstool.py --startyear ${CDS_START_YEAR} --output "$CDS_DOWNLOAD_DIR"
elif [[ "${tool}" == "tiletool" ]]; then
    # Process the data into our custom netcdfs and then into the wxdb
    python3 ${CDS_TOOL_DIR}/tiletool.py --start ${CDS_START_YEAR} --end ${CDS_END_YEAR} --update --input "$CDS_DOWNLOAD_DIR" --output "$DATA_OUTPUT_DIR"
else
    echo "Unknown tool chosen. Select 'cdstool' or 'tiletool'."
fi
