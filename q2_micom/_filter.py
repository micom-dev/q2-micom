"""Filter samples from artifacts."""

from q2_micom._formats_and_types import CommunityModelDirectory
from qiime2 import Metadata
from micom.workflows.core import GrowthResults
import pandas as pd
import shutil


def filter_models(
    models: CommunityModelDirectory,
    metadata: Metadata,
    query: str = None,
    exclude: bool = False,
) -> CommunityModelDirectory:
    """Filter samples from a set of community models."""
    manifest = models.manifest.view(pd.DataFrame)
    metadata = metadata.to_dataframe()
    if query is not None:
        metadata = metadata.query(query)
    if exclude:
        filtered_manifest = manifest[~manifest.sample_id.isin(metadata.index)]
    else:
        filtered_manifest = manifest[manifest.sample_id.isin(metadata.index)]
    if filtered_manifest.shape[0] == 0:
        raise ValueError("There are no samples left after filtering :O")
    out = CommunityModelDirectory()
    filtered_manifest.to_csv(out.manifest.path_maker())
    filtered_manifest.sample_id.apply(
        lambda sid: shutil.copy(
            models.model_files.path_maker(model_id=sid),
            out.model_files.path_maker(model_id=sid),
        )
    )
    return out


def filter_results(
    results: GrowthResults,
    metadata: Metadata,
    query: str = None,
    exclude: bool = False,
) -> GrowthResults:
    """Filter samples from the simulation results."""
    sids = results.growth_rates.sample_id
    exchanges = results.exchanges
    rates = results.growth_rates
    metadata = metadata.to_dataframe()
    if query is not None:
        metadata = metadata.query(query)
    if exclude:
        filtered_sids = sids[~sids.isin(metadata.index)]
    else:
        filtered_sids = sids[sids.isin(metadata.index)]
    if len(filtered_sids) == 0:
        raise ValueError("There are no samples left after filtering :O")
    filtered_results = GrowthResults(
        growth_rates=rates[rates.sample_id.isin(filtered_sids)],
        exchanges=exchanges[exchanges.sample_id.isin(filtered_sids)],
        annotations=results.annotations,
    )
    return filtered_results
