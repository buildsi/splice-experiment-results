# Spliced Experiment Results

![https://avatars.githubusercontent.com/u/85255731?s=200&v=4](https://avatars.githubusercontent.com/u/85255731?s=200&v=4)

This is a repository of spliced experiment results generated from the experiment defined in [spliced-experiment](https://github.com/buildsi/spliced-experiment). 
In total, there were about ~3400 jobs (give or take) each running a spliced experiment, which corresponds to a particular version of a package
and one dependency (across versions) to splice.

## Retrieving Results

To retrieve results, you'll want to get each of the results and logs separately and
name according to the run.

```bash
$ scp -r sochat1@borax.llnl.gov:/p/vast1/build/spliced-experiment/results .
$ mv results run1
$ scp -r sochat1@borax.llnl.gov:/p/vast1/build/spliced-experiment/logs .
$ mkdir log
$ mv logs log/run1
```

## Runs

 - [run1](run1): was a first shot running libabigail, symbolator, and a limited number of spack tests (a subset that were working). Logs are in [log/run1](log/run1) so we can determine errors / issues with running (that would have missing results)

## Organization 

Each directory is a different run, and there is a nested struture that captures the package name, version, and at the
lowest level the results from an experiment, `experiment.json`. As a small expample, here is the aml experiment:

```
results/aml/
├── 0.1.0
│   └── numactl
│       └── experiment.json
└── master
    └── numactl
        └── experiment.json
```

The above shows that we tested two versions of aml, both master and 0.1.0, and for each spliced
some number of versions of numactl (the results are in each of those files).

## Analysis

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
