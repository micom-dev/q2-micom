"""Constructs a minimal medium for a set of community models."""

from cobra.util.solver import OptimizationError
from micom import load_pickle
import micom.media as mm
from micom.workflows import workflow
import pandas as pd
from q2_micom._formats_and_types import CommunityModelDirectory


def _medium(args):
    """Get minimal medium for a single model."""
    p, min_growth = args
    com = load_pickle(p)
    # open the bounds
    for ex in com.exchanges:
        ex.bounds = (-1000.0, 1000.0)
    try:
        medium = mm.minimal_medium(com, 0.0, min_growth=min_growth).to_frame()
    except Exception:
        return None
    medium.columns = ["flux"]
    medium.index.name = "reaction"
    return medium[medium.flux.abs() > 1e-6].reset_index()


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
    if any(r is None for r in results):
        raise OptimizationError(
            "Could not find a growth medium that allows the specified "
            "growth rate for all taxa in all samples :("
        )
    results = pd.concat(results, axis=0)
    medium = results.groupby("reaction").flux.max().reset_index()
    medium["metabolite"] = medium.reaction.str.replace("EX_", "")
    return medium
