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

You can also ask for a specific run. Here are results for:

```bash
```

```bash
$ rm -rf artifacts/*
$ python get_artifacts.py 2864059558  # main results

$ python get_artifacts.py 3017137349  # fedora results 0-50
$ python get_artifacts.py 3017172931  # fedora results 50-100
$ python get_artifacts.py 3017684511  # fedora results 100-150
$ python get_artifacts.py 3018521212  # fedora results 150-250
$ python get_artifacts.py 3019031567  # fedora results 250-350
$ python get_artifacts.py 3019032895  # fedora results 350-450
$ python get_artifacts.py 3023207569  # fedora results 450-500
$ python get_artifacts.py 3019727038  # fedora results 550-650
$ python get_artifacts.py 3019728826  # fedora results 650-750
$ python get_artifacts.py 3020343625  # fedora results 750-850
$ python get_artifacts.py 3027789022  # fedora results 850-900

$ python get_artifacts.py 3023223782  # fedora results 950-1000 (34 vs all others had runner issues)
$ python get_artifacts.py 3023226112  # fedora results 1000-1050 (36 vs 37 runner had issues)
$ python get_artifacts.py 3025057440  # fedora results 1050-1100
$ python get_artifacts.py 3026209175  # fedora results 1100-1150
$ python get_artifacts.py 3026210109  # fedora results 1150-1200
$ python get_artifacts.py 3027040794  # fedora results 1200-1250 
$ python get_artifacts.py 3027334558  # fedora results 1300-1350 # this is where results start to peter out
$ python get_artifacts.py 3027336141  # fedora results 1350-1400
$ python get_artifacts.py 3027772125  # fedora results 1400-1450
$ python get_artifacts.py 3027773113  # fedora results 1450-1500
```
And then to open (and run/update the notebook)

```bash
$ jupyter notebook
```

### 1. Interface Generation

The docs directory should already exist.

```bash
$ python analysis.py ./artifacts --outdir ./docs
```

Notice that we provide the input folder run1 and the output directory for the data,
where a subfolder run1 will be created. We are creating in a jekyll structure under docs
anticipating creating some kind of interface to explore results. **Important** I had to minify
the `results-list.json` for openmpi because it was too big. Once we have even bigger results
we will need to refactor the interface to render tables for differen testers or similar.

### 2. Graph Generation

Ben had an idea to generate a graph, so you can do that:

```bash
$ mkdir docs/graph
$ python graph.py run1 --outdir docs/graph
```

It will generate `docs/graph/cypher.graph` that you can copy paste into a neo4j interface,
usually a [sandbox](https://neo4j.com/sandbox/) will work. To then see ALL the graph:

```cypher
MATCH p=()-->() RETURN p
```

