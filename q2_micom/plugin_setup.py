"""Plugin setup."""

import importlib
from qiime2.plugin import (
    Plugin,
    Str,
    Choices,
    Int,
    Bool,
    Range,
    Float,
    Metadata,
    MetadataColumn,
    Categorical,
    Numeric,
    Citations,
)

import q2_micom
from q2_micom._formats_and_types import (
    SBML,
    JSON,
    Pickle,
    SBMLFormat,
    SBMLDirectory,
    JSONFormat,
    JSONDirectory,
    CommunityModelFormat,
    CommunityModelManifest,
    CommunityModelDirectory,
    GrowthRates,
    Fluxes,
    MicomResultsDirectory,
    MicomMediumFile,
    MicomMediumDirectory,
    MetabolicModels,
    CommunityModels,
    MicomResults,
    MicomMedium,
    Global,
    PerSample,
    TradeoffResults,
    TradeoffResultsDirectory,
    REQ_FIELDS,
)
from q2_types.feature_data import FeatureData, Taxonomy
from q2_types.feature_table import FeatureTable, RelativeFrequency, Frequency

citations = Citations.load("citations.bib", package="q2_micom")


plugin = Plugin(
    name="micom",
    version=q2_micom.__version__,
    website="https://github.com/micom-dev/q2-micom",
    package="q2_micom",
    description=(""),
    short_description="Plugin for metabolic modeling of microbial communities.",
    citations=[citations["micom"]],
)

plugin.register_formats(
    SBMLFormat,
    SBMLDirectory,
    JSONFormat,
    JSONDirectory,
    CommunityModelFormat,
    CommunityModelManifest,
    CommunityModelDirectory,
    GrowthRates,
    Fluxes,
    MicomResultsDirectory,
    MicomMediumFile,
    MicomMediumDirectory,
    TradeoffResultsDirectory,
)
plugin.register_semantic_types(
    MetabolicModels, CommunityModels, MicomResults, MicomMedium
)
plugin.register_semantic_type_to_format(MetabolicModels[SBML], SBMLDirectory)
plugin.register_semantic_type_to_format(MetabolicModels[JSON], JSONDirectory)
plugin.register_semantic_type_to_format(
    CommunityModels[Pickle], CommunityModelDirectory
)
plugin.register_semantic_type_to_format(MicomResults, MicomResultsDirectory)
plugin.register_semantic_type_to_format(TradeoffResults, TradeoffResultsDirectory)
plugin.register_semantic_type_to_format(MicomMedium[Global], MicomMediumDirectory)
plugin.register_semantic_type_to_format(MicomMedium[PerSample], MicomMediumDirectory)

plugin.methods.register_function(
    function=q2_micom.db,
    inputs={},
    parameters={
        "meta": Metadata,
        "rank": Str % Choices(q2_micom._build.RANKS),
        "threads": Int % Range(1, None),
    },
    outputs=[("metabolic_models", MetabolicModels[JSON])],
    input_descriptions={},
    parameter_descriptions={
        "meta": (
            "Metadata for the individual metabolic models in `folder`. "
            "Must contain the the following columns: %s." % ", ".join(REQ_FIELDS)
        ),
        "rank": "The phylogenetic rank at which to summarize taxa.",
        "threads": "The number of threads to use when constructing models.",
    },
    output_descriptions={"metabolic_models": "The metabolic model DB."},
    name="Build a metabolic model database.",
    description=(
        "Constructs pan-genome models summarized to the specified rank "
        "and bundles the models to be used by MICOM. "
        "The chosen rank has to be the same you want as when building your "
        "community models. "
        "So you may not build genus-level community models with a species "
        "level database. "
        "You will only need to run this function if you want to build a "
        "custom DB. For many use cases downloading the prebuilt AGORA DB "
        "with the the preferred rank should be sufficient."
    ),
    citations=[
        citations["agora"],
        citations["agora_reply"],
        citations["micom"],
    ],
)

plugin.methods.register_function(
    function=q2_micom.build,
    inputs={
        "abundance": FeatureTable[Frequency | RelativeFrequency],
        "taxonomy": FeatureData[Taxonomy],
        "models": MetabolicModels[JSON],
    },
    parameters={
        "threads": Int % Range(1, None),
        "cutoff": Float % Range(0.0, 1.0),
        "strict": Bool,
        "solver": Str % Choices("auto", "cplex", "hybrid", "gurobi"),
    },
    outputs=[("community_models", CommunityModels[Pickle])],
    input_descriptions={
        "abundance": (
            "The feature table containing the samples over which beta "
            "diversity should be computed."
        ),
        "taxonomy": "The taxonomy assignments for the ASVs in the table.",
        "models": "The single taxon model database to use.",
    },
    parameter_descriptions={
        "threads": "The number of threads to use when constructing models.",
        "cutoff": "Taxa with a relative abundance smaller than this will "
        "be dropped.",
        "strict": (
            "If true will collapse and match on all taxa ranks up to the "
            "specified rank (so on all higher ranks as well). If false "
            "(default) will match only on single taxa rank specified before. "
            "If using the strict option make sure ranks are named the same as in "
            "the used database."
        ),
        "solver": (
            "The quadratic and linear programming solver that will be used "
            "in the models. Will pick an appropriate one by default. "
            "`cplex` and `gurobi` are commercial solvers with free academic "
            "licenses and have to be installed manually. See the docs for more info."
        ),
    },
    output_descriptions={"community_models": "The community models."},
    name="Build community models.",
    description=("Builds the metabolic community models for a set of samples."),
    citations=[citations["micom"]],
)

plugin.methods.register_function(
    function=q2_micom.minimal_medium,
    inputs={"models": CommunityModels[Pickle]},
    parameters={
        "min_growth": Float % Range(0.0, None, inclusive_start=False),
        "threads": Int % Range(1, None),
    },
    outputs=[("medium", MicomMedium[Global])],
    input_descriptions={
        "models": (
            "A collection of metabolic community models. "
            "This should contain on model for each sample."
        ),
    },
    parameter_descriptions={
        "min_growth": (
            "The minimum achievable growth rate for each taxon. "
            "The returned growth medium enables all taxa to growth "
            "simultaneously with at least this rate."
        ),
        "threads": "The number of threads to use when simulating.",
    },
    output_descriptions={"medium": "The resulting growth medium."},
    name="Obtain a minimal growth medium for models.",
    description=(
        "Obtains a minimal growth medium for the community models. "
        "Please note that this medium does not have any biological "
        "feasibility. If you have any knowledge about metabolites present "
        "in the environment we recommend you construct the medium by hand."
    ),
    citations=[citations["micom"]],
)

plugin.methods.register_function(
    function=q2_micom.grow,
    inputs={
        "models": CommunityModels[Pickle],
        "medium": MicomMedium[Global | PerSample],
    },
    parameters={
        "tradeoff": Float % Range(0.0, 1.0, inclusive_start=False, inclusive_end=True),
        "strategy": Str % Choices("pFBA", "minimal uptake", "none"),
        "threads": Int % Range(1, None),
    },
    outputs=[("results", MicomResults)],
    input_descriptions={
        "models": (
            "A collection of metabolic community models. "
            "This should contain on model for each sample."
        ),
        "medium": "The growth medium to use.",
    },
    parameter_descriptions={
        "tradeoff": (
            "The tradeoff parameter. This describes the balance "
            "between maximizing biomass production of the entire "
            "community and biomass production of individual taxa "
            '(ergo "egoistic" growth). A value of 1.0 would yield '
            "the best biomass production across the community but "
            "will only allow a few taxa to grow. Smaller values will "
            "allow more taxa to grow but will sacrifice overall "
            "biomass. A value of 0.5 (the default) has been shown to "
            "best reproduce growth rates in the human gut."
        ),
        "strategy": (
            "The strategy used when choosing the solution in the "
            "optimal flux space. `minimal uptake` uses the fluxes "
            "that result in the smallest total uptake from the environment."
            "`pFBA` uses parsimonious Flux Balance Analysis and thus will choose "
            "the fluxes with the lowest enzyme requirement for each taxon. "
            "`none` will return an arbitrary solution from the optimal flux space."
        ),
        "threads": "The number of threads to use when simulating.",
    },
    output_descriptions={
        "results": "The resulting taxa-level growth rates and metabolic "
        "exchange fluxes."
    },
    name="Simulate growth for community models.",
    description=(
        "Simulates growth for a set of samples. Note that those are "
        'sample-specific or "personalized" simulations, so each taxon '
        "may have different growth rates and metabolite usage in each sample."
    ),
    citations=[citations["micom"]],
)

plugin.methods.register_function(
    function=q2_micom.tradeoff,
    inputs={
        "models": CommunityModels[Pickle],
        "medium": MicomMedium[Global | PerSample],
    },
    parameters={
        "tradeoff_min": Float % Range(0.0, 1.0, inclusive_start=False),
        "tradeoff_max": Float % Range(0.0, 1.0, inclusive_end=True),
        "step": Float % Range(0.0, 1.0),
        "threads": Int,
    },
    outputs=[("results", TradeoffResults)],
    input_descriptions={
        "models": (
            "A collection of metabolic community models. "
            "This should contain on model for each sample."
        ),
        "medium": "The growth medium to use.",
    },
    parameter_descriptions={
        "tradeoff_min": "The minimum tradeoff parameter to test. This should "
        "be larger than 0.0 and smaller than 1.0.",
        "tradeoff_max": "The maximum tradeoff parameter to test. This should "
        "be larger than 0.0 and smaller than 1.0 and also be"
        "larger than `tradeoff_min`.",
        "step": "The tradeoff value step size to use.",
        "threads": "The number of threads to use when simulating.",
    },
    output_descriptions={
        "results": "The resulting taxa-level growth rates for varying "
        "tradeoff values."
    },
    name="Test a variety of tradeoff values.",
    description=(
        "Simulates growth for a set of samples while varying the tradeoff "
        "between community and taxon biomass production. "
        "This can be used to characterize a good tradeoff value for a "
        "specific set of samples. Our study suggested that a good tradeoff "
        "value is the largest value that allows the majority of taxa in the "
        "sample to grow."
    ),
    citations=[citations["micom"]],
)

plugin.methods.register_function(
    function=q2_micom.filter_models,
    inputs={"models": CommunityModels[Pickle]},
    parameters={"metadata": Metadata, "query": Str, "exclude": Bool},
    outputs=[("filtered_models", CommunityModels[Pickle])],
    input_descriptions={
        "models": (
            "A collection of metabolic community models. "
            "This should contain on model for each sample."
        )
    },
    parameter_descriptions={
        "metadata": "The metadata for the samples to keep or to query.",
        "query": (
            "A pandas query expression to select samples from the metadata. "
            "This will call `query` on the metadata DataFrame, so you can test "
            "your query by loading our metadata into a pandas DataFrame."
        ),
        "exclude": (
            "If true will use all samples *except* the ones selected "
            "by metadata and query."
        ),
    },
    output_descriptions={"filtered_models": "The filtered community models."},
    name="Filters models for a chosen set of samples.",
    description=(
        "Select a subset of samples and their community models using a list "
        "of samples or a pandas query expression."
    ),
    citations=[citations["micom"]],
)

plugin.methods.register_function(
    function=q2_micom.filter_results,
    inputs={"results": MicomResults},
    parameters={"metadata": Metadata, "query": Str, "exclude": Bool},
    outputs=[("filtered_results", MicomResults)],
    input_descriptions={
        "results": (
            "A set of MICOM analysis results. "
            "Contains predicted groath rates and exchange fluxes."
        )
    },
    parameter_descriptions={
        "metadata": "The metadata for the samples to keep or to query.",
        "query": (
            "A pandas query expression to select samples from the metadata. "
            "This will call `query` on the metadata DataFrame, so you can test "
            "your query by loading our metadata into a pandas DataFrame."
        ),
        "exclude": (
            "If true will use all samples *except* the ones selected "
            "by metadata and query."
        ),
    },
    output_descriptions={"filtered_results": "The filtered simulation models."},
    name="Filters results for a chosen set of samples.",
    description=(
        "Select a subset of samples and their simulation results using a list "
        "of samples or a pandas query expression."
    ),
    citations=[citations["micom"]],
)

plugin.visualizers.register_function(
    function=q2_micom.plot_growth,
    inputs={"results": MicomResults},
    parameters={},
    input_descriptions={
        "results": (
            "A set of MICOM analysis results. "
            "Contains predicted groath rates and exchange fluxes."
        )
    },
    parameter_descriptions={},
    name="Plot taxa growth rates.",
    description=(
        "Plot predicted growth rates for each taxon in each sample. "
        "Only points with growing taxa are shown (growth rate sufficiently "
        "larger than zero)."
    ),
    citations=[citations["micom"]],
)

plugin.visualizers.register_function(
    function=q2_micom.exchanges_per_sample,
    inputs={"results": MicomResults},
    parameters={
        "direction": Str % Choices("import", "export"),
        "cluster": Bool,
    },
    input_descriptions={
        "results": (
            "A set of MICOM analysis results. "
            "Contains predicted groath rates and exchange fluxes."
        )
    },
    parameter_descriptions={
        "direction": "The direction of the flux.",
        "cluster": "Whether to perform clutering on samples and reactions.",
    },
    name="Plot gloabl exchange rates.",
    description=(
        "Plot predicted global exchange fluxes for each sample. "
        "When plotting imports this corresponds to the consumption "
        "fluxes for each metabolite that is available to the community. "
        "When plotting export this corresponds to the production fluxes "
        "for each metabolite."
    ),
    citations=[citations["micom"]],
)


plugin.visualizers.register_function(
    function=q2_micom.exchanges_per_taxon,
    inputs={"results": MicomResults},
    parameters={
        "direction": Str % Choices("import", "export"),
        "perplexity": Int % Range(2, None),
    },
    input_descriptions={
        "results": (
            "A set of MICOM analysis results. "
            "Contains predicted growth rates and exchange fluxes."
        )
    },
    parameter_descriptions={
        "direction": "The direction of the flux.",
        "perplexity": "TSNE parameter. Relates to the number of neighbors used to "
        "calculate distances. Smaller values preserve more local "
        "structure and larger values preserve more global structure.",
    },
    name="Plot niche overlap.",
    description=(
        "Plot growth or production niches. "
        "The entire set of import or export fluxes for each taxon in each "
        "sample is reduced onto a single point on a 2D plane."
        "Taxa that are close to each other either consume similar metabolites "
        " (imports) or produce similar metabolites (exports)."
    ),
    citations=[citations["micom"]],
)

plugin.visualizers.register_function(
    function=q2_micom.plot_tradeoff,
    inputs={"results": TradeoffResults},
    parameters={},
    input_descriptions={
        "results": (
            "A set of MICOM tradeoff analysis results. "
            "Contains predicted growth rates for each tested tradeoff."
        )
    },
    parameter_descriptions={},
    name="Plot tradeoff results.",
    description=(
        "Plot predicted growth rate distributions for each tradeoff as "
        "well as the fraction of growing taxa in each sample and tradeoff "
        "value. For a good tradeoff value one usually tries to find the "
        "largest tradeoff value that still aloows most taxa to grow."
    ),
    citations=[citations["micom"]],
)

plugin.visualizers.register_function(
    function=q2_micom.fit_phenotype,
    inputs={"results": MicomResults},
    parameters={
        "metadata": MetadataColumn[Categorical | Numeric],
        "variable_type": Str % Choices("binary", "continuous"),
        "flux_type": Str % Choices("import", "production"),
        "min_coef": Float % Range(0, None),
    },
    input_descriptions={
        "results": (
            "A set of MICOM analysis results. "
            "Contains predicted growth rates and exchange fluxes."
        ),
    },
    parameter_descriptions={
        "metadata": "The metadata variable to use.",
        "variable_type": "The type of the phenotype variable.",
        "flux_type": "Which fluxes to use.",
        "min_coef": (
            "Only coefficient with absolute values larger than this " "will be shown."
        ),
    },
    name="Test for differential production",
    description=(
        "Test for overall metabolite production differences " "between two groups."
    ),
    citations=[citations["micom"]],
)

importlib.import_module("q2_micom._transform")
