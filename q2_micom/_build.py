"""Build Community models."""

import biom
import os
import micom.workflows as mw
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
) -> pd.DataFrame:
    """Build the specification for the community models."""
    taxa = taxonomy.str.replace("[\\w_]+__", "")
    taxa = taxa.str.split(";\\s*", expand=True)
    taxa.columns = RANKS[0:taxa.shape[1]]
    taxa["taxid"] = taxonomy.index
    taxa.index == taxa.taxid

    model_files = models.manifest.view(pd.DataFrame)
    rank = model_files.summary_rank[0]
    model_files["file"] = model_files[rank].apply(
        lambda i: str(models.json_files.path_maker(model_id=i))
    )

    abundance = (
        abundance.collapse(
            lambda id_, x: taxa.loc[id_, rank], axis="observation"
        )
        .to_dataframe(dense=True)
        .T
    )
    abundance["sample_id"] = abundance.index

    abundance = abundance.melt(
        id_vars="sample_id", var_name=rank, value_name="abundance"
    )
    depth = abundance.groupby("sample_id").abundance.sum()
    abundance["relative"] = (
        abundance.abundance / depth[abundance.sample_id].values
    )

    micom_taxonomy = pd.merge(model_files, abundance, on=rank)
    micom_taxonomy = micom_taxonomy[micom_taxonomy.relative > cutoff]
    print("Taxa per sample:")
    print(micom_taxonomy.sample_id.value_counts().describe(), "\n")
    return micom_taxonomy


def build(
    abundance: biom.Table,
    taxonomy: pd.Series,
    models: JSONDirectory,
    threads: int = 1,
    cutoff: float = 0.0001,
) -> CommunityModelDirectory:
    """Build the community models."""
    tax = build_spec(abundance, taxonomy, models, cutoff)
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
