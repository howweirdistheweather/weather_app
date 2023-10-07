# HWITW: How Weird is the Weather?

- Project: How Weird is the Weather?
- Development website: https://hwitw-dev.arcticdata.io
- Github repo: https://github.com/howweirdistheweather/weather_app

This is the general repository for the web app and managing data from How Weird is the Weather.
It includes tools for downloading ERA5 reanalysis data from the Copernicus Data Service, and tools for
statistical summarization of that data through a deployable web application.

The web application runs as a flask application, and is packaged in a docker image which can
be deployed on Kubernetes, or run locally.

## ERA5 Data

ERA5 data from Hersbach, H. et al. (2018) were downloaded from the Copernicus Climate Change Service (C3S) Climate Data Store.

The results contain modified Copernicus Climate Change Service information 2023. Neither the European Commission nor ECMWF is responsible for any use that may be made of the Copernicus information or data it contains.

> Hersbach, H., Bell, B., Berrisford, P., Biavati, G., Horányi, A., Muñoz Sabater, J., Nicolas, J., Peubey, C., Radu, R., Rozum, I., Schepers, D., Simmons, A., Soci, C., Dee, D., Thépaut, J-N. (2018): ERA5 hourly data on single levels from 1959 to present. Copernicus Climate Change Service (C3S) Climate Data Store (CDS). (Accessed on 2023-02-27), <https://doi.org/10.24381/cds.adbb2d47>

CDS ERA5 data are broken into two products:

- 1950-1978: ERA 5 Back extension (28 years, at about 156GB per year)
- 1979-present: ERA 5 (42 years, at about 136GB per year)

The `cdstool.py` script provides a simple python utility for downloading data from Copernicus using their CDS API via the python client. The `tiletool.py` script provides a python script to reprocess ERA5 data, summarizing it weekly, and outputing that to an efficient data file format for access by the web applicaiton. By running the `hwitw_update.sh` script weekly, the system will keep the data current with the currently non-embargoed data from ERA5.

## Helm deployment

Both the python scripts and flask-based webapp can be built into a docker image, which can in turn be deployed using the included [Helm](https://helm.sh) chart. See the section below on biulding the docker image, and this current section for deploying the helm application.

To deploy, you must create a secret with the [CDS API key](https://cds.climate.copernicus.eu/api-how-to) in a proper configuration file. First get your key by registering with [CDS](https://cds.climate.copernicus.eu/api-how-to), then create a config file named `cdsapirc` with the following contents (replace the key with your real key value):

```sh
url: https://cds.climate.copernicus.eu/api/v2
key: 827815:710bb811-1cc7-51fc-4c41-ea6652529bc9
verify: 1
```

Create the secret in your cluster with kubectl, giving it a name that is prefixed with your planned release name (here we'll use `hwitw` as the release name):

```sh
kubectl create secret -n hwitw generic hwitw-cdsapirc-secret --from-file=cdsapirc
```

Then install the application from helm with:

```sh
helm install -n hwitw hwitw ./helm
```

or, once it is deployed, upgrade it with:

```sh
helm upgrade -n hwitw hwitw ./helm
```

You may want to modify the values passed to the application to set appropriate mount points for persistent storage and other relevant configuration variables. See the `values.yaml` file for details.

To manually start a job from the cronjob to update the CDS data through today, create a job with:

```sh
kubectl create job --from=cronjob.batch/hwitw-cdstool-cronjob cdstool-job
```

## Docker image builds and publication to GHCR

An open source versions of the `docker` commandline tool is `nerdctl`, which works pretty much as
a dropin replacement, and can be used to generate images that can be executed with the `containerd`
runtime.

- build the image, setting the appropriate version tag

```sh
docker build -t ghcr.io/nceas/hwitw:0.9.5 -f helm/Dockerfile ./src
```

- Alternatively, tag it to be recognized in the GHCR (if it wasn't already tagged this way)
  - note that on Rancher Desktop, one also may need to set the k8s.io namespace for kubernetes to see the image

```sh
docker tag hwitw:0.9.5 ghcr.io/nceas/hwitw:0.9.5
```

- login to GHCR (requires a PAT from GITHUB with repository write permissions)

```sh
echo $GITHUB_PAT | docker login ghcr.io -u mbjones --password-stdin
```

- And push the image to ghcr.io:

```sh
docker push ghcr.io/nceas/hwitw:0.9.5
```
