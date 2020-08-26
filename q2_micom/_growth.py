"""Performs a growth simulation."""

import micom.workflows as mw
import pandas as pd
from q2_micom._formats_and_types import (
    MicomResultsDirectory,
    CommunityModelDirectory,
)


def grow(
    models: CommunityModelDirectory,
    medium: pd.DataFrame,
    tradeoff: float = 0.5,
    threads: int = 1,
) -> MicomResultsDirectory:
    """Simulate growth for a set of community models."""
    out = MicomResultsDirectory()
    model_folder = (
        str(models.model_files.path_maker(model_id="blub"))
        .replace("blub.pickle", "")
    )
    manifest = models.manifest.view(pd.DataFrame)
    growth, exchanges, annotations = mw.grow(
        manifest, model_folder, medium, tradeoff, threads)
    growth.to_csv(out.growth_rates.path_maker(), index=False)
    annotations.to_csv(out.annotations.path_maker(), index=False)
    exchanges[pd.notna(exchanges.flux)].to_csv(
        out.exchange_fluxes.path_maker(), index=False
    )
    return out
