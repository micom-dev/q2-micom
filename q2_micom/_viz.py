"""Visualizers for MICOM results."""

import micom.viz as viz
import pandas as pd
from q2_micom._formats_and_types import MicomResultsDirectory
from qiime2 import MetadataColumn


def plot_growth(output_dir: str, results: MicomResultsDirectory) -> None:
    """Plot the taxa growth rates."""
    viz.plot_growth(
        results.growth_rates.view(pd.DataFrame),
        output_dir
    )


def exchanges_per_sample(
    output_dir: str,
    results: MicomResultsDirectory,
    direction: str = "import",
    cluster: bool = True,
) -> None:
    """Plot the exchange fluxes."""
    viz.plot_exchanges_per_sample(
        results.exchange_fluxes.view(pd.DataFrame),
        output_dir,
        direction,
        cluster
    )


def exchanges_per_taxon(
    output_dir: str,
    results: MicomResultsDirectory,
    direction: str = "import",
    n_neighbors: int = 15,
    min_dist: float = 0.1,
) -> None:
    """Plot the exchange fluxes."""
    viz.plot_exchanges_per_taxon(
        results.exchange_fluxes.view(pd.DataFrame),
        output_dir,
        direction,
        n_neighbors=n_neighbors,
        min_dist=min_dist
    )


def plot_tradeoff(output_dir: str, results: pd.DataFrame) -> None:
    """Plot the taxa growth rates."""
    viz.plot_tradeoff(
        results,
        output_dir
    )


def fit_phenotype(
    output_dir: str,
    results: MicomResultsDirectory,
    metadata: MetadataColumn,
    variable_type: str = "binary",
    flux_type: str = "production",
    min_coef: float = 0.01,
):
    """Test for differential metabolite production."""
    meta = metadata.to_series()
    viz.plot_fit(
        results.exchange_fluxes.view(pd.DataFrame),
        meta,
        variable_type,
        meta.name,
        output_dir,
        flux_type,
        min_coef
    )
