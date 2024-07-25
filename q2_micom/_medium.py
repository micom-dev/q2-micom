"""Constructs a minimal medium for a set of community models."""

import micom.workflows as mw
import pandas as pd
from typing import Tuple
from q2_micom._formats_and_types import CommunityModelDirectory


def minimal_medium(
    models: CommunityModelDirectory,
    community_growth : float = 0.1,
    growth: float = 1e-2,
    minimize_components : bool = False,
    weights : str = "flux",
    threads: int = 1
) -> (pd.DataFrame, pd.DataFrame, mw.GrowthResults):
    """Calculate the minimal medium for a set of community models."""
    manifest = models.manifest.view(pd.DataFrame)
    model_folder = str(models.model_files.path_maker(model_id="blub")).replace(
        "blub.pickle", ""
    )
    if weights == "flux":
        weights = None
    sample_media, results = mw.minimal_media(
        manifest=manifest,
        model_folder=model_folder,
        community_growth=community_growth,
        growth=growth,
        minimize_components=minimize_components,
        weights=weights,
        summarize=False,
        threads=threads,
        solution=True
    )
    medium = sample_media.groupby("reaction").flux.max().reset_index()
    medium["metabolite"] = medium.reaction.str.replace("EX_", "")
    return (medium, sample_media, results)
