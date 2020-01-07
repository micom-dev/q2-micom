<img src="docs/logo.png" width="50%">

A Qiime 2 plugin for MICOM.


## Installation

*This will become easier soon.*

### Setup Qiime 2

You will need a Qiime 2 development environment ([how to get that](https://dev.qiime2.org/latest/quickstart/#install-qiime-2-within-a-conda-environment)). Activate the environment:

```bash
conda activate qiime2-dev
```

Install dependencies for `q2-micom`:

```bash
conda install -c bioconda -c conda-forge cobra umap-learn jinja2 pyarrow
```

Install `q2-micom` (this will install `MICOM` as well).

```bash
pip install git+https://github.com/micom-dev/q2-micom
```

### Install a QP solver

Finally, `MICOM` requires a quadratic programming solver. We currently support [CPLEX](https://www.ibm.com/analytics/cplex-optimizer) or [Gurobi](https://www.gurobi.com/) which both have free academic licenses but will require you to sign up for them.

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

Here is an overview of the analysis paths you can take with `q2-micom`.

<img src="docs/overview.png" width="100%">

