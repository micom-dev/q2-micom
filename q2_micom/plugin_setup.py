"""Plugin setup."""

from qiime2.plugin import (Plugin, Str, Properties, Choices, Int, Bool, Range,
                           Float, Set, Visualization, Metadata, MetadataColumn,
                           Categorical, Numeric, Citations)

import q2_micom
from q2_micom._formats_and_types import (
    SBMLFormat, SBMLDirectory, CommunityModelFormat,
    CommunityModelDirectory, GrowthRates, ExchangeFluxes,
    MicomResultsDirectory, MicomMediumFile,
    MicomMediumDirectory, MetabolicModels, CommunityModels,
    MicomResults, MicomMedium, TradeoffResults, TradeoffResultsDirectory
)

citations = Citations.load("citations.bib", package="q2_micom")


plugin = Plugin(
    name="micom",
    version=q2_micom.__version__,
    website="https://github.com/micom-dev/q2-micom",
    package="q2_micom",
    description=(""),
    short_description="Plugin for metabolic modeling of "
                      "microbial communities.",
)

plugin.register_formats(SBMLFormat, SBMLDirectory, CommunityModelFormat,
                        CommunityModelDirectory, GrowthRates, ExchangeFluxes,
                        MicomResultsDirectory, MicomMediumFile,
                        MicomMediumDirectory)
plugin.register_semantic_types(MetabolicModels, CommunityModels, MicomResults,
                               MicomMedium)
plugin.register_semantic_type_to_format(MetabolicModels[SBML], SBMLDirectory)
plugin.register_semantic_type_to_format(CommunityModels[Pickle],
                                        CommunityModelDirectory)
plugin.register_semantic_type_to_format(MicomResults, MicomResultsDirectory)
plugin.register_semantic_type_to_format(
    TradeoffResults, TradeoffResultsDirectory)
plugin.register_semantic_type_to_format(MicomMedium, MicomMediumDirectory)

plugin.methods.register_function(
    function=q2_diversity.beta_phylogenetic,
    inputs={"table": FeatureTable[Frequency],
            "phylogeny": Phylogeny[Rooted]},
    parameters={"metric": Str % Choices(beta.phylogenetic_metrics()),
                "n_jobs": Int,
                "variance_adjusted": Bool,
                "alpha": Float % Range(0, 1, inclusive_end=True),
                "bypass_tips": Bool},
    outputs=[("distance_matrix", DistanceMatrix % Properties("phylogenetic"))],
    input_descriptions={
        "table": ("The feature table containing the samples over which beta "
                  "diversity should be computed."),
        "phylogeny": ("Phylogenetic tree containing tip identifiers that "
                      "correspond to the feature identifiers in the table. "
                      "This tree can contain tip ids that are not present in "
                      "the table, but all feature ids in the table must be "
                      "present in this tree.")
    },
    parameter_descriptions={
        "metric": "The beta diversity metric to be computed.",
        "n_jobs": "The number of workers to use.",
        "variance_adjusted": ("Perform variance adjustment based on Chang et "
                              "al. BMC Bioinformatics 2011. Weights distances "
                              "based on the proportion of the relative "
                              "abundance represented between the samples at a"
                              " given node under evaluation."),
        "alpha": ("This parameter is only used when the choice of metric is "
                  "generalized_unifrac. The value of alpha controls importance"
                  " of sample proportions. 1.0 is weighted normalized UniFrac."
                  " 0.0 is close to unweighted UniFrac, but only if the sample"
                  " proportions are dichotomized."),
        "bypass_tips": ("In a bifurcating tree, the tips make up about 50% of "
                        "the nodes in a tree. By ignoring them, specificity "
                        "can be traded for reduced compute time. This has the"
                        " effect of collapsing the phylogeny, and is analogous"
                        " (in concept) to moving from 99% to 97% OTUs")
    },
    output_descriptions={"distance_matrix": "The resulting distance matrix."},
    name="Beta diversity (phylogenetic)",
    description=("Computes a user-specified phylogenetic beta diversity metric"
                 " for all pairs of samples in a feature table."),
    citations=[
        citations["lozupone2005unifrac"],
        citations["lozupone2007quantitative"],
        citations["chang2011variance"],
        citations["chen2012associating"],
        citations["mcdonald2018unifrac"]]
)


plugin.visualizers.register_function(
    function=q2_diversity.adonis,
    inputs={"distance_matrix": DistanceMatrix},
    parameters={"metadata": Metadata,
                "formula": Str,
                "permutations": Int % Range(1, None),
                "n_jobs": Int % Range(1, None)},
    input_descriptions={
        "distance_matrix": "Matrix of distances between pairs of samples."
    },
    parameter_descriptions={
        "metadata": "Sample metadata containing formula terms.",
        "formula": "Model formula containing only independent terms contained "
                   "in the sample metadata. These can be continuous variables "
                   "effects as well as their interaction. Enclose formulae in "
                   "quotes to avoid unpleasant surprises.",
        "permutations": "The number of permutations to be run when computing "
                        "p-values.",
        "n_jobs": "Number of parallel processes to run."
    },
    name="adonis PERMANOVA test for beta group significance",
    description=("Determine whether groups of samples are significantly "
                 "different from one another using the ADONIS permutation-"
                 "based statistical test in vegan-R. The function partitions "
                 "sums of squares of a multivariate data set, and is directly "
                 "analogous to MANOVA (multivariate analysis of variance). "
                 "This action differs from beta_group_significance in that it "
                 "accepts R formulae to perform multi-way ADONIS tests; "
                 "beta_group_signficance only performs one-way tests. For "
                 "more details see http://cc.oulu.fi/~jarioksa/softhelp/vegan/"
                 "html/adonis.html"),
    citations=[citations["anderson2001new"], citations["Oksanen2018"]]
)
