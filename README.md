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
$ python get_artifacts.py 2864059558  # main results
$ python get_artifacts.py 2974827036  # fedora results 0-300
$ python get_artifacts.py 2982073376  # fedora results 300-350
$ python get_artifacts.py 2980356396  # fedora results 400-500
$ python get_artifacts.py 2981362335  # fedora results 500-600
$ python get_artifacts.py 2982425794  # fedora results 600-700
$ python get_artifacts.py 2982656162  # fedora results 700-800
$ python get_artifacts.py 2984776434  # fedora results 800-850
$ python get_artifacts.py 2983082759  # fedora results 900-1000
$ python get_artifacts.py 2985397046  # fedora results 1000-1050

$ python get_artifacts.py 2986143383  # fedora results 1100-1200
```

- [350-400 always killed runner](https://github.com/buildsi/splice-experiment-runs/actions/runs/2982075984)
- [850-900 had a binary too big](https://github.com/buildsi/splice-experiment-runs/actions/runs/2984982990/workflow)

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

