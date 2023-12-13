"""Performs a growth simulation."""

import micom.workflows as mw
import pandas as pd
from q2_micom._formats_and_types import CommunityModelDirectory


def grow(
    models: CommunityModelDirectory,
    medium: pd.DataFrame,
    tradeoff: float = 0.5,
    threads: int = 1,
    strategy: str = "minimal uptake",
) -> mw.core.GrowthResults:
    """Simulate growth for a set of community models."""
    if strategy == "minimal uptake":
        strategy = "minimal imports"
    model_folder = str(models.model_files.path_maker(model_id="blub")).replace(
        "blub.pickle", ""
    )
    manifest = models.manifest.view(pd.DataFrame)
    results = mw.grow(
        manifest, model_folder, medium, tradeoff, threads, strategy=strategy
    )

    return results
