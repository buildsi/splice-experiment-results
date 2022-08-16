# Spliced Experiment Artifacts

![https://avatars.githubusercontent.com/u/85255731?s=200&v=4](https://avatars.githubusercontent.com/u/85255731?s=200&v=4)

This repository does an automated retrieval of results from [splice-experiment-runs](https://github.com/buildsi/splice-experiment-runs). It used to derive from [build-abi-containers](https://github.com/builsi/build-abi-containers), a (previously written) GitHub pipeline that I wrote, but we didn't use.
Now I'm back to GitHub because HPC never seems to work :) The process of retrieving artifacts works via the [GitHub workflow](.github/workflows/artifacts.yml) that runs the script [get_artifacts.py](get_artifacts.py). Since the data is smaller (a matrix of results across compilers) it can be ru manually:

## Analysis

### 1. Setup

Make a virtual environment and install dependencies:

```bash
$ python -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

### 2. Artifacts and Notebook

```bash
export GITHUB_TOKEN=xxxxxxxxxxx
```
```bash
$ python get_artifacts.py
```

You can also ask for a specific run:

```bash
$ rm -rf artifacts/*
$ python get_artifacts.py 2864059558
```

 - [artifacts/cache](artifacts/cache) has cached results (Smeagle and ABI laboratory report)
 - [artifacts/results](artifacts/results) has the experiment.json results.

And then to open (and run/update the notebook)

```bash
$ jupyter notebook
```

### 1. Interface Generation

The docs directory should already exist.

**under development**

```bash
$ python analysis.py ./artifacts --outdir ./docs
```


