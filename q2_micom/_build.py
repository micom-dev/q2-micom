"""Build Community models."""

import biom
import os
import micom.workflows as mw
from micom.taxonomy import build_from_qiime
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
    strict: bool
) -> pd.DataFrame:
    """Build the specification for the community models."""
    model_files = models.manifest.view(pd.DataFrame).rename(columns={"id": "model_id"})
    rank = model_files.summary_rank[0]
    rank_index = RANKS.index(rank)
    if strict:
        ranks = RANKS[0:rank_index]
    else:
        ranks = [rank]
    model_files["file"] = model_files[rank].apply(
        lambda i: str(models.json_files.path_maker(model_id=i))
    )

    tax = build_from_qiime(abundance, taxonomy, collapse_on=ranks)
    micom_taxonomy = pd.merge(model_files, tax, on=ranks)
    micom_taxonomy = micom_taxonomy[micom_taxonomy.relative > cutoff]
    stats = micom_taxonomy.sample_id.value_counts().describe()
    print("Merged with the database using ranks: %s" % ", ".join(ranks))
    print(
        "Each community model contains %d-%d taxa (average %d+-%d)." % (
            stats["min"], stats["max"],
            round(stats["mean"]), round(stats["std"]))
    )
    return micom_taxonomy


def build(
    abundance: biom.Table,
    taxonomy: pd.Series,
    models: JSONDirectory,
    threads: int = 1,
    cutoff: float = 0.0001,
    strict: bool = False,
) -> CommunityModelDirectory:
    """Build the community models."""
    tax = build_spec(abundance, taxonomy, models, cutoff, strict)
    out = CommunityModelDirectory()
    out_folder = (
        str(out.model_files.path_maker(model_id="test"))
        .replace("test.pickle", "")
    )
    model_folder = (
        str(models.json_files.path_maker(model_id="test"))
        .replace("test.json", "")
    )
    mw.build(tax, model_folder, out_folder, cutoff, threads)
    os.rename(os.path.join(out_folder, "manifest.csv"),
              out.manifest.path_maker())
    return out
