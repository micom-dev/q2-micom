"""Constructs a minimal medium for a set of community models."""

from micom import load_pickle
import micom.media as mm
from micom.workflows import workflow
import pandas as pd
from q2_micom._formats_and_types import CommunityModelDirectory


def _medium(args):
    """Get minimal medium for a single model."""
    p, min_growth = args
    com = load_pickle(p)
    medium = mm.minimal_medium(com, 0.0, min_growth=min_growth).to_frame()
    medium.columns = ["flux"]
    medium.index.name = "reaction"
    return medium.reset_index()


def process_medium(medium, samples):
    """Prepare a medium for simulation."""
    medium.index = medium.reaction
    if "sample_id" not in medium.columns:
        meds = []
        for s in samples:
            m = medium.copy()
            m["sample_id"] = s
            meds.append(m)
        medium = pd.concat(meds, axis=0)
    return medium


def minimal_medium(
    models: CommunityModelDirectory, min_growth: float = 0.1, threads: int = 1
) -> pd.DataFrame:
    """Calculate the minimal medium for a set of community models."""
    samples = models.manifest.view(pd.DataFrame).sample_id.unique()
    paths = [models.model_files.path_maker(model_id=s) for s in samples]
    args = [[p, min_growth] for p in paths]
    results = workflow(_medium, args, threads)
    results = pd.concat(results, axis=0)
    medium = results.groupby("reaction").flux.max().reset_index()
    medium["metabolite"] = medium.reaction.str.replace("EX_", "")
    return medium
