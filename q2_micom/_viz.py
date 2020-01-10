"""Visualizers for MICOM results."""

from fastcluster import linkage
from scipy.cluster.hierarchy import leaves_list
from jinja2 import Environment, PackageLoader, select_autoescape
import numpy as np
import pandas as pd
from os import path
from q2_micom._formats_and_types import MicomResultsDirectory
from umap import UMAP

env = Environment(
    loader=PackageLoader("q2_micom", "assets/templates"),
    autoescape=select_autoescape(["html"]),
)


def plot_growth(output_dir: str, results: MicomResultsDirectory) -> None:
    """Plot the taxa growth rates."""
    template = env.get_template("growth.html")
    data_loc = path.join(output_dir, "growth_rates.csv")
    rates = results.growth_rates.view(pd.DataFrame)
    rates = rates[rates.growth_rate > 1e-6][
        ["taxon", "sample_id", "abundance", "growth_rate"]
    ]
    rates.to_csv(data_loc)
    template.stream(
        data=rates.to_json(orient="records"), width=800, height=400
    ).dump(path.join(output_dir, "index.html"))


def exchanges_per_sample(
    output_dir: str,
    results: MicomResultsDirectory,
    direction: str = "import",
    cluster: bool = True,
) -> None:
    """Plot the exchange fluxes."""
    template = env.get_template("sample_heatmap.html")
    data_loc = path.join(output_dir, "exchange_fluxes.csv")
    exchanges = results.exchange_fluxes.view(pd.DataFrame)
    exchanges = exchanges[
        (exchanges.taxon == "medium")
        & (exchanges.direction == direction)
        & (exchanges.flux.abs() > 1e-6)
    ]
    exchanges.flux = exchanges.flux.abs()
    mat = exchanges.pivot_table(
        values="flux", index="reaction", columns="sample_id", fill_value=1e-6
    )
    sample_order = leaves_list(linkage(mat.values.T, method="average"))
    reaction_order = leaves_list(linkage(mat.values, method="average"))
    mat = mat.iloc[reaction_order, sample_order]

    mat["reaction"] = mat.index
    data = mat.melt(
        id_vars="reaction", var_name="sample_id", value_name="flux"
    )
    data.to_csv(data_loc)
    w = mat.shape[1] * 10
    template.stream(
        data=data.to_json(orient="records"),
        width=w,
        height=w * mat.shape[0] / mat.shape[1],
    ).dump(path.join(output_dir, "index.html"))


def exchanges_per_taxon(
    output_dir: str,
    results: MicomResultsDirectory,
    direction: str = "import",
    n_neighbors: int = 15,
    min_dist: float = 0.1
) -> None:
    """Plot the exchange fluxes."""
    template = env.get_template("umap.html")
    data_loc = path.join(output_dir, "umap.csv")
    exchanges = results.exchange_fluxes.view(pd.DataFrame)
    exchanges = exchanges[
        (exchanges.taxon != "medium")
        & (exchanges.direction == direction)
        & (exchanges.flux.abs() > 1e-6)
    ]
    exchanges.flux = exchanges.flux.abs()
    mat = exchanges.pivot_table(
        values="flux", index=["sample_id", "taxon"], columns="reaction",
        fill_value=0
    )
    umapped = UMAP(
        min_dist=min_dist,
        n_neighbors=n_neighbors).fit_transform(mat.values)
    umapped = pd.DataFrame(
        umapped, index=mat.index, columns=["UMAP 1", "UMAP 2"]
    ).reset_index()
    umapped.to_csv(data_loc)
    template.stream(
        data=umapped.to_json(orient="records"), width=600, height=500
    ).dump(path.join(output_dir, "index.html"))


def plot_tradeoff(output_dir: str, results: pd.DataFrame) -> None:
    """Plot the taxa growth rates."""
    template = env.get_template("tradeoff.html")
    data_loc = path.join(output_dir, "tradeoff.csv")
    results.to_csv(data_loc)
    growth = results[
        ["taxon", "sample_id", "abundance", "tradeoff", "growth_rate"]
    ]
    growth.tradeoff = growth.tradeoff.round(6).astype(str)
    growth.tradeoff[growth.tradeoff == "nan"] = "none"
    growth.growth_rate[growth.growth_rate < 1e-6] = 1e-6
    growth["log_growth_rate"] = np.log10(growth.growth_rate)
    tradeoff = growth.groupby(["tradeoff", "sample_id"]).apply(
        lambda df: pd.Series({
            "n_taxa": df.shape[0],
            "n_growing": df[df.growth_rate > 1e-6].shape[0],
            "fraction_growing": (
                df[df.growth_rate > 1e-6].shape[0] / df.shape[0]
            )
            })
    ).reset_index()
    template.stream(
        growth=growth.to_json(orient="records"),
        tradeoff=tradeoff.to_json(orient="records"),
        extent=[growth.log_growth_rate.min(), growth.log_growth_rate.max()],
        width=400,
        height=300
    ).dump(path.join(output_dir, "index.html"))
