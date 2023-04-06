# News and release notes for q2-micom

This includes a list of major changes for each minor version starting from 0.10.0. `q2-micom` uses [SemVer 2](https://semver.org/).

For information on how to use `q2-micom` please refer to
[the tutorial](https://micom-dev.github.io/q2-micom).

#### 0.12.4

Avoids updating the base Qiime2 scikit-learn which can break taxonomy classifiers.

#### 0.12.3

Fixes for the PYPI upload.

#### 0.12.2

Add some more citations. Now tests against newer Qiime2 versions.

#### 0.12.1

Now always cast sample IDs to strings avoiding issue with numeric IDs.

### 0.12.0

`build` now accepts the `--p-solver` parameter that allows to specify which solver
to use in case one has several installed.

`grow` now accepts the `--p-strategy` parameter that allows to specify the strategy
to pick a flux solution.

`grow` now defaults to using parsimonious FBA (pFBA) to get fluxes as this has more
empirical evidence in returning the biologically relevant flux distributions. In some
instances this can lead to results that are different from what previous versions
have returned. In particular this will may lead to less secreted molecules.
In this case you can pick the previous strategy by using `--p-strategy="minimal uptake"`.

Fixed a bug in `build` when using the strict option where it would not use the correct
taxonomic rank to merge.

#### 0.11.3

Fixed a bug in the filter functions where the metadata was not correctly transformed
to a DataFrame.

Corrected the filter commands in the docs.

#### 0.11.2

Fixed an error where growth results could not be saved to an artifact.

#### 0.11.1

Fixed building of package and artifacts.

### 0.11.0

Add the actions `filter-models` and `filter-results`.

#### 0.10.1

Fixed an issue with the required MICOM version.

### 0.10.0

This was a maintenance release that added support for newer Qiime2 and MICOM versions.
