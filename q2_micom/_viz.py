"""Visualizers for MICOM results."""

from fastcluster import linkage
from scipy.cluster.hierarchy import leaves_list
from jinja2 import Environment, PackageLoader, select_autoescape
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
        data=rates.to_json(orient="records"), width=1200, height=720
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
        values="flux", index="reaction", columns="sample_id"
    )
    sample_order = leaves_list(linkage(mat.values.T, method="average"))
    reaction_order = leaves_list(linkage(mat.values, method="average"))
    mat = mat.iloc[reaction_order, sample_order]
    mat["reaction"] = mat.index
    data = mat.melt(
        id_vars="reaction", var_name="sample_id", value_name="flux"
    )
    data.to_csv(data_loc)
    w = min(1200, mat.shape[1] * 32)
    template.stream(
        data=data.to_json(orient="records"),
        width=w,
        height=w * mat.shape[0] / mat.shape[1],
    ).dump(path.join(output_dir, "index.html"))


def exchanges_per_taxon(
    output_dir: str, results: MicomResultsDirectory, direction: str = "import"
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
    umapped = UMAP().fit_transform(mat.values)
    umapped = pd.DataFrame(
        umapped, index=mat.index, columns=["UMAP 1", "UMAP 2"]
    ).reset_index()
    umapped.to_csv(data_loc)
    template.stream(
        data=umapped.to_json(orient="records"), width=1200, height=800
    ).dump(path.join(output_dir, "index.html"))
