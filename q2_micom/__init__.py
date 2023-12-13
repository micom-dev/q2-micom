"""Global imports for q2-micom."""

from q2_micom._build import build
from q2_micom._db import db
from q2_micom._filter import filter_models, filter_results
from q2_micom._formats_and_types import MicomResultsData
from q2_micom._growth import grow
from q2_micom._medium import minimal_medium
from q2_micom._tradeoff import tradeoff
from q2_micom._viz import (
    plot_growth,
    exchanges_per_sample,
    exchanges_per_taxon,
    plot_tradeoff,
    fit_phenotype,
)

__version__ = "0.13.0"


def read_results(path):
    """Read the results from a MICOM simulation.

    Parameters:
    -----------
    path : str
        The path to a MicomResults artifact.

    Returns:
    --------
    MicomResultsData
        A named tuple with the following attributes:

        growth_rates : pd.DataFrame
        The growth rates for each taxon and sample.

        exchange_fluxes : pd.DataFrame
        The exchange fluxes for each metabolite, sample and taxon. Fluxes
        that denote trasnport from and into the environment are denoted with
        the taxon `medium.
    """
    from qiime2 import Artifact

    art = Artifact.load(path)
    return art.view(MicomResultsData)


__all__ = [
    "db",
    "build",
    "minimal_medium",
    "grow",
    "tradeoff",
    "plot_growth",
    "exchanges_per_sample",
    "exchanges_per_taxon",
    "plot_tradeoff",
    "fit_phenotype",
    "read_results",
    "filter_models",
    "filter_results",
]
