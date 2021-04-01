"""Constructs a minimal medium for a set of community models."""

import micom.workflows as mw
import pandas as pd
from q2_micom._formats_and_types import CommunityModelDirectory


def minimal_medium(
    models: CommunityModelDirectory, min_growth: float = 0.1, threads: int = 1
) -> pd.DataFrame:
    """Calculate the minimal medium for a set of community models."""
    manifest = models.manifest.view(pd.DataFrame)
    model_folder = str(models.model_files.path_maker(model_id="blub")).replace(
        "blub.pickle", ""
    )
    medium = mw.minimal_media(manifest, model_folder, True, min_growth, threads)
    return medium
