"""Visualizers for MICOM results."""

from micom.workflows.core import GrowthResults
import micom.viz as viz
import pandas as pd
from qiime2 import MetadataColumn


def plot_growth(output_dir: str, results: GrowthResults) -> None:
    """Plot the taxa growth rates."""
    viz.plot_growth(
        results,
        output_dir
    )


def exchanges_per_sample(
    output_dir: str,
    results: GrowthResults,
    direction: str = "import",
    cluster: bool = True,
) -> None:
    """Plot the exchange fluxes."""
    viz.plot_exchanges_per_sample(
        results,
        output_dir,
        direction,
        cluster
    )


def exchanges_per_taxon(
    output_dir: str,
    results: GrowthResults,
    direction: str = "import",
    n_neighbors: int = 15,
    min_dist: float = 0.1,
) -> None:
    """Plot the exchange fluxes."""
    viz.plot_exchanges_per_taxon(
        results,
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
    results: GrowthResults,
    metadata: MetadataColumn,
    variable_type: str = "binary",
    flux_type: str = "production",
    min_coef: float = 0.01,
):
    """Test for differential metabolite production."""
    meta = metadata.to_series()
    viz.plot_fit(
        results,
        meta,
        variable_type,
        meta.name,
        output_dir,
        flux_type,
        min_coef
    )
