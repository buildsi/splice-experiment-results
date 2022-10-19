# Not Used Analyses

Our first early analyses used notebooks, and neither of us particularly like
them so we moved over to regular Python (and associated) scripts.

### 4. Interface Generation

This was originally run from the root, and the interface was provided to visualize
high-fidelity results (that we ultimately didn't use).
The docs directory should already exist. Make sure you have dependencies installed:

```bash
$ pip install -r requirements.txt
```

This small UI is just intended to show the different compiler results "high fidelity tests"
so target that directory:

```bash
$ python analysis.py ./artifacts/tests --outdir ./docs
```

Notice that we provide the input folder run1 and the output directory for the data,
where a subfolder run1 will be created. We are creating in a jekyll structure under docs
anticipating creating some kind of interface to explore results. **Important** I had to minify
the `results-list.json` for openmpi because it was too big. Once we have even bigger results
we will need to refactor the interface to render tables for differen testers or similar.

