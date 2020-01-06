"""Build Community models."""

import biom
from micom import Community
from micom.workflows import workflow
import pandas as pd
from q2_micom._formats_and_types import (
    JSONDirectory,
    CommunityModelDirectory,
)


RANKS = ["kingdom", "phylum", "class", "order", "family", "genus", "species", "strain"]


def reduce_group(df):
    new = df.iloc[0, :]
    new["file"] = "|".join(df.file.astype(str))
    return new


def build_spec(
    abundance: biom.Table,
    taxonomy: pd.Series,
    models: JSONDirectory,
    rank: str,
    cutoff: float,
) -> pd.DataFrame:
    """Build the specification for the community models."""
    taxa = taxonomy.str.replace("\\w__", "")
    taxa = taxa.str.split(";\\s*", expand=True)
    taxa.columns = RANKS[0:taxa.shape[1]]
    taxa["taxid"] = taxonomy.index
    taxa.index == taxa.taxid
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
    model_files = models.manifest.view(pd.DataFrame)
    model_files["file"] = model_files[rank].apply(
        lambda i: str(models.sbml_files.path_maker(model_id=i))
    )

    micom_taxonomy = pd.merge(model_files, abundance, on=rank)
    micom_taxonomy = micom_taxonomy[micom_taxonomy.relative > cutoff]
    print(micom_taxonomy.sample_id.value_counts().describe())
    return micom_taxonomy


def build_and_save(args):
    s, tax, out = args
    com = Community(tax, id=s, progress=False)
    com.to_pickle(out)


def build(
    abundance: biom.Table,
    taxonomy: pd.Series,
    models: JSONDirectory,
    medium: MicomMediumFile,
    rank: str = "genus",
    threads: int = 1,
    cutoff: float = 0.0001,
) -> CommunityModelDirectory:
    """Build the community models."""
    tax = build_spec(abundance, taxonomy, models, rank, cutoff)
    tax["file"] = tax.file.str.split("|")
    models = CommunityModelDirectory()
    samples = tax.sample_id.unique()
    args = [
        [
            s,
            tax[tax.sample_id == s],
            models.model_files.path_maker(model_id=s),
        ]
        for s in samples
    ]
    workflow(build_and_save, args, threads)
    tax.to_csv(models.manifest.path_maker(), index=False)
    return models
