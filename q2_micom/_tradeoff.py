"""Helpers to run cooperative tradeoff with various tradeoff values."""

import micom.workflows as mw
import numpy as np
import pandas as pd
from q2_micom._formats_and_types import (
    CommunityModelDirectory,
)


def tradeoff(
    models: CommunityModelDirectory,
    medium: pd.DataFrame,
    tradeoff_min: float = 0.1,
    tradeoff_max: float = 1.0,
    step: float = 0.1,
    threads: int = 1,
) -> pd.DataFrame:
    """Run tradeoff analysis."""
    manifest = models.manifest.view(pd.DataFrame)
    model_folder = str(models.model_files.path_maker(model_id="blub")).replace(
        "blub.pickle", ""
    )
    if tradeoff_min >= tradeoff_max:
        raise ValueError("`tradeoff_min` must be smaller than `tradeoff_max` :(")
    tradeoffs = np.arange(tradeoff_min, tradeoff_max + 1e-6, step)
    results = mw.tradeoff(manifest, model_folder, medium, tradeoffs, threads)
    return results
