<img src="docs/assets/logo.png" width="75%">

[![Test and deploy](https://github.com/micom-dev/q2-micom/actions/workflows/test_package.yml/badge.svg)](https://github.com/micom-dev/q2-micom/actions/workflows/test_package.yml)
[![codecov](https://codecov.io/gh/micom-dev/q2-micom/branch/master/graph/badge.svg)](https://codecov.io/gh/micom-dev/q2-micom)
[![PyPI version](https://badge.fury.io/py/q2-micom.svg)](https://badge.fury.io/py/q2-micom)


A QIIME 2 plugin for MICOM.

## Installation

You will need an existing QIIME 2 environment. Follow the instructions on ([how to install QIIME 2](https://docs.qiime2.org/2021.2/install/native/#install-qiime-2-within-a-conda-environment))
otherwise. Let's assume that environment was called `qiime2-2021.2` for all further steps.

### Add q2-micom to the QIIME 2 environment

This will be the same step for any supported QIIME 2 version or operating systems.

```bash
wget https://raw.githubusercontent.com/micom-dev/q2-micom/master/q2-micom.yml
conda env update -n qiime2-2021.2 -f q2-micom.yml
# OPTIONAL CLEANUP
rm q2-micom.yml
```

Finally, you activate your environment.

```bash
conda activate qiime2-2021.2
```

### Install a QP solver
### Install a QP solver

**CPLEX (recommended)**

*QIIME 2 is only compatible with CPLEX 12.10 or earlier (later version require at least Python 3.7).*

After registering and downloading the CPLEX studio for your OS unpack it (by running the provided installer) to a directory of your choice (we will assume it's called `ibm`).

Now install the CPLEX python package into your activated environment:

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

Note that Gurobi support is often iffy and might break for periods of time. It will also be *much* slower than CPLEX.

### Finish your installation

If you installed `q2-micom` in an already existing QIIME 2 environment, update the plugin cache:

```bash
conda activate qiime2-2021.2  # or whatever you called your environment
qiime dev refresh-cache
```

You are now ready to run `q2-micom`!

## Usage

Here is a graphical overview of a `q2-micom` analysis.

<img src="docs/assets/overview.png" width="100%">

The best way to get started is to work through the [community tutorial](https://micom-dev.github.io/q2-micom).

## Supported QIIME 2 versions

`q2-micom` is tested against:

1. the current [QIIME 2 version](https://docs.qiime2.org/)
2. the previous version

It should also work with

3. the [development version](https://dev.qiime2.org/latest/)<br>
   However, this may occasionally break. Check [here for the current status](https://github.com/micom-dev/q2-micom/actions/workflows/qiime_dev.yml).


## References

MICOM: Metagenome-Scale Modeling To Infer Metabolic Interactions in the Gut Microbiota <br>
Christian Diener, Sean M. Gibbons, Osbaldo Resendis-Antonio <br>
mSystems 5:e00606-19 <br>
https://doi.org/10.1128/mSystems.00606-19
