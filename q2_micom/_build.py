"""Build Community models."""

import biom
from loguru import logger
from micom import Community
from micom.workflows import workflow
import pandas as pd
from q2_micom._formats_and_types import (
    SBMLDirectory,
    CommunityModelDirectory,
    MicomMediumFile,
)


RANKS = ["kingdom", "phylum", "class", "order", "family", "genus", "species"]


def reduce_group(df):
    new = df.iloc[0, :]
    new["file"] = "|".join(df.id.apply(lambda id: f"{id}.xml"))
    return new


def build_spec(
    abundance: biom.Table,
    taxonomy: pd.Series,
    models: SBMLDirectory,
    rank: str,
    cutoff: float
) -> pd.DataFrame:
    """Build the specification for the community models."""
    taxa = taxonomy.str.replace("\\w__", "")
    taxa = taxa.str.split(";\\s+", expand=True)
    taxa.columns = RANKS
    taxa["taxid"] = taxonomy.loc[:, 0]
    taxa.index == taxa.taxid
    abundance = abundance.collapse(lambda id_, x: taxa.loc[id_, rank])
    abundance["sample_id"] = abundance.index
    abundance = abundance.to_dataframe().T.melt(
        index_var="sample_id", var_name="taxon", value_name="abundance"
    )
    model_files = models.manifest.view(pd.DataFrame)
    model_files = (
        model_files.groupby(rank).apply(reduce_group).reset_index(drop=True)
    )
    micom_taxonomy = pd.merge(model_files, abundance, on=rank)
    depth = micom_taxonomy.groupby(rank).abundance.sum()
    micom_taxonomy = micom_taxonomy[
        (micom_taxonomy.abundance /
         depth[micom_taxonomy[rank]].values) < cutoff
    ]
    return micom_taxonomy


def build_and_save(args):
    s, tax, out, medium = args
    com = Community(tax, id=s, progress=False)
    ex_ids = [r.id for r in com.exchanges]
    logger.info(
        "%d/%d import reactions found in model.",
        medium.index.isin(ex_ids).sum(),
        len(medium),
    )
    com.medium = medium[medium.index.isin(ex_ids)]
    com.to_pickle(out)


def build_models(
    abundance: biom.Table,
    taxonomy: pd.Series,
    models: SBMLDirectory,
    medium: MicomMediumFile,
    rank: str,
    threads: int,
    cutoff: float,
) -> CommunityModelDirectory:
    """Build the community models."""
    tax = build_spec(abundance, taxonomy, models, rank, cutoff)
    models = CommunityModelDirectory()
    medium = medium.view(pd.DataFrame).flux
    samples = tax.sample_id.unique()
    args = [
        [s, tax[tax.sample_id == s], models.model_files.path_maker(s), medium]
        for s in samples
    ]
    workflow(build_and_save, args, threads)
