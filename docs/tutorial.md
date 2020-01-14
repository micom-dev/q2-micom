<img src="docs/assets/logo.png" width="50%">

# Community Tutorial

`q2-micom` provides a Qiime 2 plugin for the [MICOM](https://github.com/micom-dev/micom) Python package and allows for functional analysis of
microbial communities with metabolic modeling.

## A primer on MICOM

### Why metabolic modeling

Analysis of function in microbial communities is often performed based solely on sequencing data and reference genomes. This is a good way of
gauging the metabolic *potential* of a microbe, but the mere presence
of a particular gene does not guarantee any metabolic consequence. For instance, *E. coli* can grow aerobically and anaerobically with the exact same genotype. However, it will consume and produce very different
metabolites in those two settings.

Metabolic modeling tries to estimate the activity of metabolic processes by predicting metabolic fluxes, the rate of mass conversions within a cell (usually expressed in mmol per gram dry-weight per hour). It uses
the *genotype* and *environmental conditions* to establish the stoichiometry and flux limits
of all biochemical reactions in the cell and then tries to find sets of fluxes that yield maximum growth under a set of assumptions. This optimization of biomass production under a given stoichiometry is called
[*Flux Balance Analysis (FBA)*](https://www.nature.com/articles/nbt.1614).

### The assumptions we make

MICOM extends the concept of FBA to microbial communities. In particular, it tries to reduce the space of feasible fluxes by imposing a tradeoff between optimization of the community wide biomass production and the individual ("egoistic") maximization of biomass production for each taxon. To do so it makes the following assumptions:

1. The biochemical system is in [*steady state*](https://en.wikipedia.org/wiki/Steady_state) which means that fluxes and growth rates are approximately constant in time (exponential growth).
2. All individual taxa strive to maximize their growth.
3. There are thermodynamic limits to biochemical reactions (reaction fluxes have upper and/or lower limits).
4. The enzymes available to a bacteria in your sample are approximately the same as in the used reference model/genome.

Not all of those assumptions may be fulfilled by the system you are studying. The farther you are to fulfilling them, the less correct predictions by MICOM will be.

## Installation

MICOM models all biochemical reactions in all taxa which means that the optimization problem MICOM solves included hundreds of thousands of variables. There are only few numerical solvers that can sole quadratic programming problems of that scale. Right, now we support [CPLEX](https://www.ibm.com/analytics/cplex-optimizer) or [Gurobi](https://www.gurobi.com/) which both have free academic licenses but will require you to sign up for them. We hope to change that in the future. If you have one of the two solver available you can install `q2-micom` with the
following steps.

### Setup Qiime 2

You will need a Qiime 2 environment ([how to get that](https://dev.qiime2.org/latest/quickstart/#install-qiime-2-within-a-conda-environment)). Activate the environment:

```bash
conda activate qiime2-dev
```

Install dependencies for `q2-micom`:

```bash
conda install -c bioconda -c conda-forge cobra umap-learn jinja2 pyarrow tqdm
```

Install `q2-micom` (this will install `MICOM` as well).

```bash
pip install git+https://github.com/micom-dev/q2-micom
```

### Install a QP solver

**CPLEX**

After registering and downloading the CPLEX studio for your OS unpack it (by running the provided installer) to a directory of your choice (we will assume it's called `ibm`).

Now install the CPLEX python package:

```bash
pip install ibm/cplex/python/3.6/x86-64_linux
```

Substitute `x86-64_linux` with the folder corresponding to your system (there will only be one subfolder in that directory).

**Gurobi**

Gurobi can be installed with conda.

```bash
conda install -c gurobi gurobi
```

You will now have to register the installation using your license key.

```bash
grbgetkey YOUR-LICENSE-KEY
```

### Finish your installation

If you installed `q2-micom` in an already existing Qiime 2 environment update the plugin cache:

```bash
conda activate qiime2-dev  # or whatever you called your environment
qiime dev refresh-cache
```

You are now ready to run `q2-micom`.

## Walkthrough: Analyzing colorectal cancer data with q2-micom

The general analysis outline for `q2-micom` looks like this:

<img src="assets/overview.png" width="100%">

The first artifact you will want to produce are the metabolic community models. Which are sample-specific metabolic models that contain all taxa in the specific sample. To build those you will need the abundances and taxonomy for the taxa in your sample. Luckily, one of the main function of Qiime 2 is to obtain those things from sequencing data, phew.

For our purposes we will provide those premade artifacts for a 16S amplicon sequencing data set from 8 healthy and 8 colorectal cancer stool samples taken from https://doi.org/10.1158/1940-6207.CAPR-14-0129. Those were quantified with DADA2 and the taxonomy was inferred using the SILVA database version 132.

**Downloads**:

- [abundance table](crc_table.qza)
- [taxonomy](crc_taxa.qza)


