#!/bin/bash

# base:  https://www.ncei.noaa.gov/data/local-climatological-data/access/2005/

# Create historical directory if not exists

[ -d "./historical" ] && echo "Using ./historical directory for data files." || echo "Creating historical directory for first time..." && mkdir -p historical

## Defaults

STATION_ID=25507
START_YEAR=1960
END_YEAR=`date +%Y`

usage() {                                      # Function: Print a help message.
  echo "Usage: $0 [ -i STATION_ID ] [--station STATION_ID ] [ -s YYYY (default: 1960)] [ -e (default: 2020) ] " 1>&2 
}
exit_abnormal() {                              # Function: Exit with error.
  usage
  exit 1
}
while getopts ":ise:" options; do              # Loop: Get the next option;
                                               # use silent error checking;
                                               # options n and t take arguments.
  case "${options}" in                         # 
    i)                                         # If the option is n,
      STATION_ID=${OPTARG}                     # set $STATION_ID to specified value.
      ;;
    s)
      START_YEAR=${OPTARG} 
      ;;
    e)
      END_YEAR=${OPTARG}
      ;; 
    :)                                         # If expected argument omitted:
      echo "Error: -${OPTARG} requires an argument."
      exit_abnormal                            # Exit abnormally.
      ;;
    *)                                         # If unknown (any other) option:
      exit_abnormal                            # Exit abnormally.
      ;;
  esac
done

if [ -z $STATION_ID ]
then
    echo "-----------------------------------------"
    echo "| fetch_historical                      |"
    echo "-----------------------------------------"
    echo "This script will fetch weather from the Local Climatological Data repository via https from 1960-2020."
    echo "Currently this is very untested should be a basis for any project needing to fetch historical data."
    echo ""
    echo "author(s): David Yerrington (david@yerrington.net)"
    echo ""
    usage
fi

# echo "Sending request..."
# page_src=`curl https://www.ncei.noaa.gov/data/local-climatological-data/access/2005/`
# filename=`echo {$page_src} | grep -o -E href=\"\([0-9]{6}25507.csv\) | grep -o -E [0-9]+.csv`
# echo $filename

echo "Fetching historical data for $STATION_ID from $START_YEAR-$END_YEAR"
echo "----------------------------------------------------------------------"
for (( i=$START_YEAR; i<=$END_YEAR; i++ ))
do
    
    base_url="https://www.ncei.noaa.gov/data/local-climatological-data/access/$i/"
    echo "Sending request to $base_url..."
    directory_src=`curl $base_url`
    filename=`echo {$directory_src} | grep -o -E href=\"\([0-9]{6}25507.csv\) | grep -o -E [0-9]+.csv`
    echo "Found file $filename"
    echo "Downloading to historical/$i/$filename..."
    mkdir -p ./historical/$i
    wget -O ./historical/$i/$STATION_ID.csv $base_url/$filename
done