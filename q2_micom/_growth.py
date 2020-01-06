"""Performs a growth simulation."""

from micom import load_pickle
from micom.logger import logger
from micom.media import minimal_medium
from micom.workflows import workflow
import numpy as np
import pandas as pd
from q2_micom._formats_and_types import (
    MicomResultsDirectory,
    CommunityModelDirectory,
    MicomMediumFile,
)
from q2_micom._medium import process_medium

DIRECTION = pd.Series(["import", "export"], index=[0, 1])


def _growth(args):
    p, tradeoff, medium = args
    com = load_pickle(p)
    ex_ids = [r.id for r in com.exchanges]
    logger.info(
        "%d/%d import reactions found in model.",
        medium.index.isin(ex_ids).sum(),
        len(medium),
    )
    com.medium = medium[medium.index.isin(ex_ids)]

    # Get growth rates
    try:
        sol = com.cooperative_tradeoff(fraction=tradeoff)
        rates = sol.members
        rates["taxon"] = rates.index
        rates["tradeoff"] = np.nan
        rates["sample_id"] = com.id
    except Exception:
        logger.warning("Could not solve cooperative tradeoff for %s." % com.id)
        return None

    # Get the minimal medium
    med = minimal_medium(com, 0.95 * sol.growth_rate)

    # Apply medium and reoptimize
    com.medium = med[med > 0]
    sol = com.cooperative_tradeoff(fraction=tradeoff, fluxes=True, pfba=False)
    fluxes = sol.fluxes.loc[:, sol.fluxes.columns.str.startswith("EX_")].copy()
    fluxes["sample_id"] = com.id
    return {"growth": rates, "exchanges": fluxes}


def grow(
    models: CommunityModelDirectory,
    medium: MicomMediumFile,
    tradeoff: float = 0.5,
    threads: int = 1,
) -> MicomResultsDirectory:
    """Simulate growth for a set of community models."""
    out = MicomResultsDirectory()
    samples = models.manifest.view(pd.DataFrame).sample_id.unique()
    paths = {s: models.model_files.path_maker(model_id=s) for s in samples}
    medium = process_medium(medium, samples)
    args = [
        [p, tradeoff, medium.flux[medium.sample_id == s]]
        for s, p in paths.items()
    ]
    results = workflow(_growth, args, threads)
    growth = pd.concat(r["growth"] for r in results)
    growth.to_csv(out.growth_rates.path_maker())
    exchanges = pd.concat(r["exchanges"] for r in results)
    exchanges["taxon"] = exchanges.index
    exchanges = exchanges.melt(
        id_vars=["taxon", "sample_id"], var_name="reaction", value_name="flux"
    )
    exchanges["metabolite"] = exchanges.reaction.str.replace("EX_", "")
    exchanges["direction"] = DIRECTION[
        (exchanges.flux > 0.0).astype(int)
    ].values
    exchanges[pd.notna(exchanges.flux)].to_parquet(
        out.exchange_fluxes.path_maker()
    )
    return out
