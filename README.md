<img src="docs/assets/logo.png" width="75%">

[![Build Status](https://dev.azure.com/chdiener/cdiener/_apis/build/status/micom-dev.q2-micom?branchName=master)](https://dev.azure.com/chdiener/cdiener/_build/latest?definitionId=2&branchName=master)
![Azure DevOps tests](https://img.shields.io/azure-devops/tests/chdiener/cdiener/2)
[![codecov](https://codecov.io/gh/micom-dev/q2-micom/branch/master/graph/badge.svg)](https://codecov.io/gh/micom-dev/q2-micom)


A Qiime 2 plugin for MICOM.


## Installation

*This will become easier soon.*

### Setup Qiime 2

You will need a Qiime 2 development environment ([install Qiime 2](https://dev.qiime2.org/latest/quickstart/#install-qiime-2-within-a-conda-environment)). Once installed, activate the environment:

```bash
conda activate qiime2-dev
```

Install dependencies for `q2-micom`:

```bash
conda install -c conda-forge -c bioconda cobra umap-learn jinja2 pyarrow loguru tqdm
```

Install `q2-micom` (this will install `MICOM` as well).

```bash
pip install git+https://github.com/micom-dev/q2-micom
```

### Install a QP solver

Finally, `MICOM` requires a quadratic programming solver. We currently support [CPLEX](https://www.ibm.com/analytics/cplex-optimizer) or [Gurobi](https://www.gurobi.com/), which both have free academic licenses but will require you to sign up for them. *We currently recommend using CPLEX as Gurobi can be
slow for some models.*

**CPLEX**

After registering and downloading the CPLEX studio for your OS unpack it (by running the provided installer) to a directory of your choice (we will assume it's called `ibm`).

Now install the CPLEX python package:

```bash
pip install ibm/cplex/python/3.6/x86-64_linux
```

Substitute `x86-64_linux` with the folder corresponding to your system.

**Gurobi**

Gurobi can be installed with conda.

```bash
conda install -c gurobi gurobi
```

You will now have to register the installation using your license key.

```bash
grbgetkey YOUR-LICENSE-KEY
```

You are now ready to run `q2-micom`.

## Usage

Here is a graphical overview of a `q2-micom` analysis.

<img src="docs/assets/overview.png" width="100%">

The best way to get started is to work through the [community tutorial](https://github.com/micom-dev/q2-micom/blob/master/docs/README.md).

## References

MICOM: Metagenome-Scale Modeling To Infer Metabolic Interactions in the Gut Microbiota <br>
Christian Diener, Sean M. Gibbons, Osbaldo Resendis-Antonio <br>
mSystems 5:e00606-19 <br>
https://doi.org/10.1128/mSystems.00606-19
