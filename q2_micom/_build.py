"""Build Community models."""

import biom
import os
import micom.workflows as mw
from micom.taxonomy import build_from_qiime, rank_prefixes
import pandas as pd
from q2_micom._formats_and_types import (
    JSONDirectory,
    CommunityModelDirectory,
)


RANKS = [
    "kingdom",
    "phylum",
    "class",
    "order",
    "family",
    "genus",
    "species",
    "strain",
]


def build_spec(
    abundance: biom.Table,
    taxonomy: pd.Series,
    models: JSONDirectory,
    cutoff: float,
    strict: bool,
) -> pd.DataFrame:
    """Build the specification for the community models."""
    model_files = models.manifest.view(pd.DataFrame).rename(columns={"id": "model_id"})
    rank = model_files.summary_rank[0]
    rank_index = RANKS.index(rank)
    if strict:
        ranks = RANKS[0 : (rank_index + 1)]
    else:
        ranks = [rank]

    no_rank_prefixes = rank_prefixes(model_files).isna().all()
    tax = build_from_qiime(
        abundance, taxonomy, collapse_on=ranks, trim_rank_prefix=no_rank_prefixes
    )
    micom_taxonomy = pd.merge(model_files, tax, on=ranks)
    micom_taxonomy = micom_taxonomy[micom_taxonomy.relative > cutoff]
    del micom_taxonomy["file"]
    stats = micom_taxonomy.sample_id.value_counts().describe()
    print("Merged with the database using ranks: %s" % ", ".join(ranks))
    if stats.count == 1.0:
        stats["std"] = 0.0
    print(
        "Each community model contains %d-%d taxa (average %d+-%d)."
        % (stats["min"], stats["max"], round(stats["mean"]), round(stats["std"]))
    )
    return micom_taxonomy


def build(
    abundance: biom.Table,
    taxonomy: pd.Series,
    models: JSONDirectory,
    threads: int = 1,
    cutoff: float = 0.0001,
    strict: bool = False,
    solver: str = "auto",
) -> CommunityModelDirectory:
    """Build the community models."""
    if solver == "auto":
        solver = None
    tax = build_spec(abundance, taxonomy, models, cutoff, strict)
    out = CommunityModelDirectory()
    out_folder = str(out.model_files.path_maker(model_id="test")).replace(
        "test.pickle", ""
    )
    model_folder = str(models.json_files.path_maker(model_id="test")).replace(
        "test.json", ""
    )
    mw.build(tax, model_folder, out_folder, cutoff, threads, solver)
    os.rename(os.path.join(out_folder, "manifest.csv"), out.manifest.path_maker())
    return out
