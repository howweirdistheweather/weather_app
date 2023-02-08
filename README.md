# How Weird is the Weather (HWITW)


## Helm deployment

```
helm install -n hwitw hwitw ./helm
```

## Docker image builds and publication to GHCR

```
echo $GITHUB_PAT | nerdctl login ghcr.io -u mbjones --password-stdin
```

- Tag it to be recognized in the GHCR

```
nerdctl -n k8s.io tag hwitw:0.5.0 ghcr.io/nceas/hwitw:0.5.0
```

- And push it to ghcr.io:

```
nerdctl -n k8s.io push ghcr.io/nceas/hwitw:0.5.0
```
