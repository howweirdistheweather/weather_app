# HWITW: How Weird is the Weather?

- Project: How Weird is the Weather?
- Development website: https://hwitw-dev.arcticdata.io
- Github repo: https://github.com/howweirdistheweather/weather_app

This is the general repository for managing files from How Weird is the Weather. It includes 
tools for downloading ERA5 reanalysis data from the Copernicus Data Service, and tools for 
statistical summarization of that data through a deployable web application.

The web application runs as a flask application, and is packaged in a docker image which can 
be deployed on Kubernetes, or run locally.

## Downloading CDS data

Download data from the Copernicus Climate Data Service (CDS)

This is a simple python utility for downloading data from Copernicus using their CDS API via the python client.

Dependencies include:

- cdsapi
- NetCDF4

CDS ERA5 data are broken into two products:

- 1950-1978: ERA 5 Back extension (28 years, at about 156GB per year, totalling around 4,368 GB)
- 1979-2021: ERA 5 (42 years, at about 136GB per year, totlling aroung 5,712 GB)

## Checksums

I also generated checksums for all downloaded files usinfg openssl and recorded those in 
`cds-checksums.csv` using a command like this:

```sh
fn="cds_era5_backext/1953/global-1953-2m_dewpoint_temperature.nc" openssl dgst -sha256 $fn | awk -F'[()=]' '{print $2 ",",  $1 "," $4}' >> cds-checksums.csv
```

## Helm deployment

First you must create a secret with the CDS API key in the proper configuration file. First get your key from CDS, then format the config file such as (replace the key with your real key value):

```
url: https://cds.climate.copernicus.eu/api/v2
key: 827815:710bb811-1cc7-51fc-4c41-ea6652529bc9
verify: 0
```

Create the secret with kubectl, giving it a name that is prefixed with your planned release name (here we'll use `hwitw` as the release name):

```
k8 create secret -n hwitw generic hwitw-cdsapirc-secret --from-file=cdsapirc
```

Then install from helm with:

```
helm install -n hwitw hwitw ./helm
```

## Docker image builds and publication to GHCR

An open source versions of the docker commandline tool is `nerdctl`, which works pretty much as
a dropin replacement, and can be used to generate images that can be executed with the `containerd` 
runtime.

- build the image

```
nerdctl build -t ghcr.io/nceas/hwitw:0.7.0 -f helm/Dockerfile ./src
```

- Tag it to be recognized in the GHCR (if it wasn't already tagged this way)

```
nerdctl -n k8s.io tag hwitw:0.7.0 ghcr.io/nceas/hwitw:0.7.0
```

- login to GHCR (requires a PAT from GITHUB with repository write permissions)

```
echo $GITHUB_PAT | nerdctl login ghcr.io -u mbjones --password-stdin
```

- And push the image to ghcr.io:

```
nerdctl -n k8s.io push ghcr.io/nceas/hwitw:0.7.0
```
