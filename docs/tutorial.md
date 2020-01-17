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

To keep track of what we will do let's provide a coarse overview of a `q2-micom` analysis which looks like this.

<img src="assets/overview.png" width="100%">

So to start we will need taxa abundances and a model database. Let's look at model databases first.

### Metabolic model databases

Too build metabolic community models you will first need taxon-specific metabolic models for as many taxa in your sample as possible. Unfortunately, there is no magic involved here and we will need to provide this. Building high quality metabolic models is in art in itself. It can be done from from a genome alone (for instance using [ModelSEED](http://modelseed.org/) or [CarveME](https://github.com/cdanielmachado/carveme)) but usually requires additional curation. Additionally, MICOM requires those models to be collapsed to the specific rank you want to simulate, for instance on the species or genus level. To facilitate this step we provide pre-built databases based on the [AGORA](https://doi.org/10.1038/nbt.3703) model collection which comprises manually curated metabolic models for 818 bacterial strains. For this tutorial we will use models summarized on the genus level as this is usually the lowest rank with decent accuracy in 16S data.

**Download:**

- [AGORA 1.03 genus model DB](https://zenodo.org/record/3608330/files/agora_genus_103.qza?download=1)

### Building community models

The first artifact you will want to produce are the metabolic community models. Those are sample-specific metabolic models that contain all taxa in the specific sample at the right abundance. To build those you will need the abundances and taxonomy for the taxa in your sample. Luckily, one of the main function of Qiime 2 is to obtain those things from sequencing data, phew.

For our purposes we will provide those pre-built artifacts for a 16S amplicon sequencing data set from 8 healthy and 8 colorectal cancer stool samples taken from https://doi.org/10.1158/1940-6207.CAPR-14-0129. Those were quantified with DADA2 and the taxonomy was inferred using the SILVA database version 132.

**Downloads**:

- [abundance table](crc_table.qza)
- [taxonomy](crc_taxa.qza)

Using our downloaded model database we can now build our community models with `qiime micom build` command. Note that most commands in `q2-micom` take a `--p-threads` parameter that specifies how many CPU cores to use and which will speed up things considerably. Additionally, using the `--verbose` flag will usually show a progress bar. Very low abundance taxa are usually dropped from the models. This controlled by the `--p-cutoff` parameters (0.01%) by default. Okay, let's build our community models now:

```bash
qiime micom build --i-abundance crc_table.qza \
                  --i-taxonomy crc_taxa.qza \
                  --i-models agora_genus_103.qza \
                  --p-cutoff 0.0001 \
                  --p-threads 8 \
                  --o-community-models models.qza \
                  --verbose
```

This will give you something like this:

```
Taxa per sample:
count    16.0000
mean     27.0000
std       5.7038
min      17.0000
25%      22.7500
50%      28.0000
75%      30.0000
max      36.0000
Name: sample_id, dtype: float64

 50%|█████████████████████████████████████                                   | 8/16 [09:39<09:39, 72.48s/sample(s)]
```

The first number indicate the number of genera per sample used to build the models. In average we have 27 (17-36) taxa per sample here. Building the models will take a while but usually has to be done only once for each data set. You can then run many growth simulations on the existing models.

### Running a growth simulation

Now where we have our community models let us simulate growth for them. For this we will need information about the environment since growth rates will depend strongly on the available nutrients. In contrast to classical growth media in the lab, growth conditions in metabolic modeling have to be provided in terms of fluxes and not concentrations. If you have fluxomics or time course metabolomics data you may provide those, but if you don't you may have to estimate them based what is known on the environment. You may also use a minimal medium, but more about that later. For now we can use a set of growth conditions for the human gut under an average Western diet. This was based on European diet data with a manual depletion of metabolites that are absorbed in the small intestine.

**Download**:

- [growth conditions for human gut](https://zenodo.org/record/3608330/files/western_diet_gut.qza?download=1)

Additionally, you will also have to provide a parameter that models
the tradeoff between maximal community growth and individual taxa growth. For now we will set this to 0.3 and have a better look in the next section. So let's dive in and simulate growth.

```bash
qiime micom grow --i-models models.qza \
                 --i-medium western_diet_gut.qza \
                 --p-tradeoff 0.3 \
                 --p-threads 8 \
                 --o-results growth.qza \
                 --verbose
```

You will again see a progress bar and will have the results when everything is done (this took about 7m with 8 threads for me). We can now start to look at growth rates and fluxes in our models, but we will first come back to our tradeoff parameters...

### Picking a tradeoff value

One feature specific to MICOM is the consideration of the tradeoff between community growth and individual taxa growth. Here, MICOM applies "pressure" to the model to allow growth for as many taxa as possible. However, this results in tug-of-war between a high community-level biomass production or allowing more taxa to grow. The balance between the two is dictated by a *tradeoff* value which dictates what percentage of the maximal community growth rate has to be maintained and that ranges from 0 (no growth) to 1 (enforce maximum growth).

The truth usually usually lies in the middle of those extremes and in our study we found that a tradeoff of 0.5 seemed to correspond best to *in vivo* growth rates. However, the best tradeoff may also depend on your samples, environment and used rank. So it is a good idea to run a validation. You will only need the same input as for the previous command. The command will now run the growth simulation with many different tradeoff values and track some key metrics.

```bash
qiime micom tradeoff --i-models models.qza \
                     --i-medium western_diet_gut.qza \
                     --p-threads 8 \
                     --o-results tradeoff.qza \
                     --verbose
```

After the analysis is finished it is a good point to look at our first visualization.

```bash
qiime micom plot-tradeoff --i-results tradeoff.qza \
                          --o-visualization tradeoff.qzv
```

This will give you the following:

<img src="assets/tradeoff.png" width="100%">

Here the distribution of growth rates is shown by the 2D histogram on the left and the fraction of growing taxa with its mean line is shown on the left. You can see that lowering the tradeoff gives you more and more taxa that grow. The elbow is around 0.5 but we might want to pick a value as low as 0.3 here since that is where we observe the largest jump. It is expected that not all taxa can grow since this can be a consequence of an incorrect model, an imperfect set of growth conditions or even a non-viable but present taxon in the original. However, for consistency we would expoect most of the observed taxa to grow.

Okay, no we understood where the tradeoff value comes from we can come back to our growth simulations form before.

### Visualizing growth rates

The `MicomResults` artifact we generated earlier can be visualized in many different ways. The first thing we might want to have a look at are the growth rates themselves.

```bash
qiime micom plot-growth --i-results growth.qza \
                        --o-visualization growth_rates.qzv
```

<img src="assets/growth_rates.png" width="100%">

We can see that growth rates are pretty heterogeneous across samples but it's still hard to se what is going one.

### Visualizing metabolite consumption

Now let's have a look at consumption of metabolites. Depending on the composition we will see preferences for consumption of metabolites and it would be interesting to see how those line up with our phenotype. In general, even for a given growth rate those are not unique. For instance if *E. coli* needs 10 mmol of glucose per hour to grow it may still import 100mmol and just not use the remaining 90, or import 80 and not use the remaining 70, etc. To make those imports more unique MICOM will report the minimal consumption rates that still provide the observed growth rates (so 10 mmol/h for our *E. coli* example).

```bash
qiime micom exchanges-per-sample --i-results growth.qza \
                                 --o-visualization exchanges.qzv
```


<img src="assets/consumption.png" width="80%">

We do see that there is some separation between the healthy and cancer samples. For, instance there are sets of amino acids that get consumed by healthy microbiotas but not as much in the cancer ones. One of them is glutamine. Many cancer cells show glutamine addiction as a consequence of the Warburg effect. So we could hypothesize that this depletes it in cancer samples so the microbiota has adapted to grow without it.

We could also look at produced metabolites by passing the `--p-direction export` parameter but due to the enforced minimum import there is usually very little net production of metabolites. So this is only useful if you want to look at overshoot production.

### Visualizing growth niches

The last visualization gave us a global view of metabolite consumption but we may also be interested in looking at consumption preferences in individual taxa. We will need to lower the complexity of this data though since it is pretty hard to visualize import for each metaboliote, in each taxa and each sample otherwise. One useful summary is to first reduce dimensions on the metabolite axis with UMAP and represent metabolite imports as a single point in a 2D space. Then we can look at taxa in specific samples on that plot. Taxa that are close to each other occupy the same growth niche whereas taxa that are far away from each other compete for less metabolites.

```bash
qiime micom exchanges-per-taxon --i-results growth.qza \
                                --o-visualization niche.qzv
```

<img src="assets/niche.png" width="80%">

Most taxa have a specific growth niche those move around a bit across samples. You can tune the UMAP reduction by using the parameters `--p-n-neighbors` and `--p-min-dist`. You can look at metabolite production with `--p-direction export` where you can observe way less clustering, meaning that there is considerate overlap in metabolite production.

