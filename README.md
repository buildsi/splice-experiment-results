# Spliced Experiment Artifacts

![https://avatars.githubusercontent.com/u/85255731?s=200&v=4](https://avatars.githubusercontent.com/u/85255731?s=200&v=4)

This repository does an automated retrieval of results from [splice-experiment-runs](https://github.com/buildsi/splice-experiment-runs). It used to derive from [build-abi-containers](https://github.com/builsi/build-abi-containers), a (previously written) GitHub pipeline that I wrote, but we didn't use.
Now I'm back to GitHub because HPC never seems to work :) The process of retrieving artifacts works via the [GitHub workflow](.github/workflows/artifacts.yml) that runs the script [get_artifacts.py](get_artifacts.py). Since the data is smaller (a matrix of results across compilers) it can be ru manually:

```bash
export GITHUB_TOKEN=xxxxxxxxxxx
export INPUT_REPOSITORY=buildsi/splice-experiment-runs
```
```bash
$ python get_artifacts.py
```

 - [artifacts/cache](artifacts/cache) has cached results (Smeagle and ABI laboratory report)
 - [artifacts/results](artifacts/results) has the experiment.json results.

**important** when we have actual results (have moved out of development) we will want to delete
all the data here and start fresh with a limit on the number of days we go back (to only get the final result).
