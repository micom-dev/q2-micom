"""Plugin setup."""

import importlib
from qiime2.plugin import (Plugin, Str, Properties, Choices, Int, Bool, Range,
                           Float, Set, Visualization, Metadata, MetadataColumn,
                           Categorical, Numeric, Citations)

import q2_micom
from q2_micom._formats_and_types import (
    SBML, Pickle,
    SBMLFormat, SBMLDirectory, CommunityModelFormat,
    CommunityModelDirectory, GrowthRates, ExchangeFluxes,
    MicomResultsDirectory, MicomMediumFile,
    MicomMediumDirectory, MetabolicModels, CommunityModels,
    MicomResults, MicomMedium, TradeoffResults, TradeoffResultsDirectory,
    REQ_FIELDS
)
from q2_types.feature_data import (FeatureData, Taxonomy)
from q2_types.feature_table import (FeatureTable, RelativeFrequency, Frequency)

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
    function=q2_micom.make_db,
    inputs={},
    parameters={"meta": Metadata, "folder": Str},
    outputs=[("metabolic_models", MetabolicModels[SBML])],
    input_descriptions={},
    parameter_descriptions={
        "meta": ("Metadata for the individual metabolic models in `folder`. "
                 "Must contain the the following columns: %s." %
                 ", ".join(REQ_FIELDS)),
        "folder": ("The folder where the SBML models are stored. Model files "
                   "must have filenames in `{ID}.xml` where {ID} is the id "
                   "in the metadata file."),
        },
    output_descriptions={"metabolic_models": "The metabolic model DB."},
    name="Build a metabolic model database.",
    description=(
        "Bundles the metabolic models used by MICOM. "
        "You will only need to run this function if you want to build a "
        "custom DB. For most use cases downloading the prebuilt AGORA DB "
        "should be sufficient."
    ),
    citations=[
        citations["agora"],
        citations["agora_reply"],
        citations["micom"]
    ]
)

plugin.methods.register_function(
    function=q2_micom.build_models,
    inputs={"abundance": FeatureTable[Frequency | RelativeFrequency],
            "taxonomy": FeatureData[Taxonomy],
            "models": MetabolicModels[SBML],
            "medium": MicomMedium
            },
    parameters={"rank": Str % Choices(q2_micom._build.RANKS),
                "threads": Int % Range(1, None),
                "cutoff": Float % Range(0.0, 1.0)
                },
    outputs=[("community_models", CommunityModels[Pickle])],
    input_descriptions={
        "abundance": ("The feature table containing the samples over which beta "
                  "diversity should be computed."),
        "taxonomy": "The taxonomy assignments for the ASVs in the table.",
        "models": "The single taxon model database to use.",
        "medium": "The growth medium to use."
    },
    parameter_descriptions={
        "rank": "The phylogenetic rank at which to summarize taxa.",
        "threads": "The number of threads to use when constructing models.",
        },
    output_descriptions={"community_models": "The community models."},
    name="Build community models.",
    description=("Builds the metabolic community models for a "
                 "set of samples."),
    citations=[
        citations["micom"]
    ]
)

importlib.import_module('q2_micom._transform')
