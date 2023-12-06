<img src="https://github.com/micom-dev/q2-micom/raw/main/docs/assets/logo.png" width="75%">

[![Test and deploy](https://github.com/micom-dev/q2-micom/actions/workflows/test_package.yml/badge.svg)](https://github.com/micom-dev/q2-micom/actions/workflows/test_package.yml)
[![codecov](https://codecov.io/gh/micom-dev/q2-micom/branch/main/graph/badge.svg)](https://codecov.io/gh/micom-dev/q2-micom)
[![PyPI version](https://badge.fury.io/py/q2-micom.svg)](https://badge.fury.io/py/q2-micom)


A QIIME 2 plugin for MICOM.

## Installation

You will need an existing QIIME 2 environment. Follow the instructions on ([how to install QIIME 2](https://docs.qiime2.org/2023.9/install/native/#install-qiime-2-within-a-conda-environment)) otherwise. `q2-micom` is compatible with all QIIME 2 distributions.
Let's assume that environment was called `qiime2-2023.9` for all further steps.

### Add q2-micom to the QIIME 2 environment

This will be the same step for any supported QIIME 2 version but will vary depending on your operating system
(similar to the normal QIIME 2 installation).

**Linux**

```bash
wget https://raw.githubusercontent.com/micom-dev/q2-micom/main/q2-micom-linux.yml
conda env update -n qiime2-2023.8 -f q2-micom-linux.yml
# OPTIONAL CLEANUP
rm q2-micom-*.yml
```

**Mac**

```bash
wget https://raw.githubusercontent.com/micom-dev/q2-micom/main/q2-micom-osx.yml
conda env update -n qiime2-2023.9 -f q2-micom-osx.yml
# OPTIONAL CLEANUP
rm q2-micom-*.yml
```

Finally, you activate your environment.

```bash
conda activate qiime2-2023.9
```

`q2-micom` will now install an open source solver that can be used with MICOM. If you use MICOM
regularly we do recommend to obtain an academic license for CPLEX or Gurobi which will be faster.

### Install a faster solver (recommended but optional)

*CPLEX*

*QIIME 2 versions before 2021.4 are only compatible with CPLEX 12.10 or earlier (later version require at least Python 3.7).*

After registering and downloading the CPLEX studio for your OS unpack it (by running the provided installer) to a directory of your choice (we will assume it's called `ibm`).

Now install the CPLEX python package into your activated environment:

```bash
pip install ibm/cplex/python/3.8/x86-64_linux
```

Substitute `3.8` with the Python version in your QIIME 2 environment, `3.6` for QIIME 2 up to 2021.2 and `3.8` for QIIME 2 2021.4 and newer.
Substitute `x86-64_linux` with the folder corresponding to your system (there will only be one subfolder in that directory).

***Gurobi***

Gurobi can be installed with conda.

```bash
conda install -c gurobi gurobi
```

You will now have to register the installation using your license key.

```bash
grbgetkey YOUR-LICENSE-KEY
```

### Finish your installation

If you installed `q2-micom` in an already existing QIIME 2 environment, update the plugin cache:

```bash
conda activate qiime2-2023.9  # or whatever you called your environment
qiime dev refresh-cache
```

You are now ready to run `q2-micom`!

## Usage

Here is a graphical overview of a `q2-micom` analysis.

<img src="https://github.com/micom-dev/q2-micom/raw/main/docs/assets/overview.png" width="100%">

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
