"""Visualizers for MICOM results."""

from micom.workflows import GrowthResults
import micom.viz as viz
from os.path import join
import pandas as pd
from qiime2 import MetadataColumn


def plot_growth(output_dir: str, results: GrowthResults) -> None:
    """Plot the taxa growth rates."""
    viz.plot_growth(
        results,
        join(output_dir, "index.html"),
    )


def exchanges_per_sample(
    output_dir: str,
    results: GrowthResults,
    direction: str = "import",
    cluster: bool = True,
) -> None:
    """Plot the exchange fluxes."""
    viz.plot_exchanges_per_sample(
        results, join(output_dir, "index.html"), direction, cluster
    )


def exchanges_per_taxon(
    output_dir: str,
    results: GrowthResults,
    direction: str = "import",
    perplexity: int = 20,
) -> None:
    """Plot the exchange fluxes."""
    viz.plot_exchanges_per_taxon(
        results,
        join(output_dir, "index.html"),
        direction,
        perplexity=perplexity,
    )


def plot_tradeoff(output_dir: str, results: pd.DataFrame) -> None:
    """Plot the taxa growth rates."""
    viz.plot_tradeoff(results, join(output_dir, "index.html"))


def association(
    output_dir: str,
    results: GrowthResults,
    metadata: MetadataColumn,
    variable_type: str = "binary",
    flux_type: str = "production",
    fdr_threshold: float = 0.1,
):
    """Test for differential metabolite production."""
    meta = metadata.to_series()
    viz.plot_association(
        results,
        meta,
        variable_type,
        meta.name,
        join(output_dir, "index.html"),
        flux_type,
        fdr_threshold,
        atol=1e-6,
    )
