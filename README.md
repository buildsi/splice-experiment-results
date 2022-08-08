# Spliced Experiment Results

![https://avatars.githubusercontent.com/u/85255731?s=200&v=4](https://avatars.githubusercontent.com/u/85255731?s=200&v=4)

This is a repository of spliced experiment results generated from the experiment defined in [spliced-experiment](https://github.com/buildsi/spliced-experiment), and run on GitHub actions at [spliced-experiment-runs](https://github.com/buildsi/splice-experiment-runs). Each experiment includes one top level package and a dependency, and within each run we select to splice all non-deprecated versions of the dependency. We are running on GitHub actions for reproducibility, and because HPC didn't work due to file-systems issues.

## Retrieving Results

The results are provided via a GitHub submodule, added like this:

```bash
$ git submodule add https://github.com/buildsi/splice-experiment-artifacts results
```

And this means if you clone this fresh you can do:

```
$ git submodule update
```


## Runs

## Organization 

Results have a cache for raw data at `results/artifacts/cache`, and the main result organization at `results/artifacts/results`l. Each directory there is a different run, and there is a nested struture that captures the package name, version, and at the lowest level the results from an experiment, `experiment.json`. As a small example:

```
results/artifacts/results/
└── qthreads
    ├── 1.10
    │   └── hwloc
    │       └── experiment.json
    ├── 1.11
    │   └── hwloc
    │       └── experiment.json
    ├── 1.12
    │   └── hwloc
    │       └── experiment.json
    ├── 1.14
    │   └── hwloc
    │       └── experiment.json
    ├── 1.15
    │   └── hwloc
    │       └── experiment.json
    └── 1.16
        └── hwloc
            └── experiment.json
```

The above shows that we tested five versions of qthreads, and within that version there was one library to splice (hwloc) and within each experiment.json there will be multiple versions of that tested.

## Analysis

### 1. Interface Generation

You'll need some basic dependencies for data frames, etc.

```bash
$ python -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

I will write scripts to summarize results, and if appropriate, to provide an interface to explore. As an example,
here is how to parse results:

```bash
$ mkdir -p ./docs
$ python analysis.py run1 --outdir ./docs
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
