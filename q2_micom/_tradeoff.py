"""Helpers to run cooperative tradeoff with various tradeoff values."""

from cobra.util.solver import OptimizationError
from micom import load_pickle
from micom.logger import logger
from micom.workflows import workflow
import numpy as np
import pandas as pd
from q2_micom._formats_and_types import (
    CommunityModelDirectory,
)
from q2_micom._medium import process_medium


def _tradeoff(args):
    p, tradeoffs, medium = args
    com = load_pickle(p)
    ex_ids = [r.id for r in com.exchanges]
    logger.info(
        "%d/%d import reactions found in model.",
        medium.index.isin(ex_ids).sum(),
        len(medium),
    )
    com.medium = medium[medium.index.isin(ex_ids)]
    try:
        sol = com.optimize()
    except Exception:
        logger.warning(
            "Sample %s could not be optimized (%s)." %
            (com.id, com.solver.status),
        )
        return None
    rates = sol.members
    rates["taxon"] = rates.index
    rates["tradeoff"] = np.nan
    rates["sample_id"] = com.id
    df = [rates]

    # Get growth rates
    try:
        sol = com.cooperative_tradeoff(fraction=tradeoffs)
    except Exception:
        logger.warning(
            "Sample %s could not be optimized (%s)." %
            (com.id, com.solver.status),
        )
        return None
    for i, s in enumerate(sol.solution):
        rates = s.members
        rates["taxon"] = rates.index
        rates["tradeoff"] = sol.tradeoff[i]
        rates["sample_id"] = com.id
        df.append(rates)
    df = pd.concat(df)
    return df[df.taxon != "medium"]


def tradeoff(
    models: CommunityModelDirectory,
    medium: pd.DataFrame,
    tradeoff_min: float = 0.1,
    tradeoff_max: float = 1.0,
    step: float = 0.1,
    threads: int = 1,
) -> pd.DataFrame:
    """Run tradeoff analysis."""
    samples = models.manifest.view(pd.DataFrame).sample_id.unique()
    paths = {s: models.model_files.path_maker(model_id=s) for s in samples}
    if tradeoff_min >= tradeoff_max:
        raise ValueError(
            "`tradeoff_min` must be smaller than `tradeoff_max` :("
        )
    tradeoffs = np.arange(tradeoff_min, tradeoff_max + 1e-6, step)
    medium = process_medium(medium, samples)
    args = [
        [p, tradeoffs, medium.flux[medium.sample_id == s]]
        for s, p in paths.items()
    ]
    results = workflow(_tradeoff, args, threads)
    if all(r is None for r in results):
        raise OptimizationError(
            "All numerical optimizations failed. This indicates a problem "
            "with the solver or numerical instabilities. Check that you have "
            "CPLEX or Gurobi installed. You may also increase the abundance "
            "cutoff in `qiime micom build` to create simpler models."
        )
    results = pd.concat(results)
    return results
