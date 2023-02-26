#!/bin/bash

# Run this once a week to update 'how weird is the weather' data.

# Set these environment variables to specify where to download and where
# to process data files.
# (some tricky bash to give variable a default value if not set)
: "${CDS_DOWNLOAD_DIR:='./'}"
: "${DATA_OUTPUT_DIR:='./'}"

set -e
# Download the latest Copernicus CDS data.
# ...It is currently 2023 - so we start from there. What happens in 2024+?
# There is a small overhead as the tool checks that is has downloaded all
# data for 2023, 2024, etc. Say < 1 minute total. It is harmless.
python3 cdstool.py --startyear 2023 --output "$CDS_DOWNLOAD_DIR"

# Process the data into our custom netcdfs and then into the wxdb
# ...Same as above, there is a small overhead in following years as the
# tool checks that it has processed all data for 2023, 2024, etc.
python3 tiletool.py --start 2023 --update --input "$CDS_DOWNLOAD_DIR" --output "$DATA_OUTPUT_DIR"

