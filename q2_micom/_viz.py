"""Visualizers for MICOM results."""

from fastcluster import linkage
from scipy.cluster.hierarchy import leaves_list
from jinja2 import Environment, PackageLoader, select_autoescape
import json
import numpy as np
import pandas as pd
from os import path
from q2_micom._formats_and_types import MicomResultsDirectory
from qiime2 import CategoricalMetadataColumn
from scipy.stats import mannwhitneyu
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
    exchanges["flux"] = exchanges.flux.abs() * exchanges.abundance
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
    growth.loc[growth.tradeoff == "nan", "tradeoff"] = "none"
    growth.loc[growth.growth_rate < 1e-6, "growth_rate"] = 1e-6
    growth.loc[:, "log_growth_rate"] = np.log10(growth.growth_rate)
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


def augment(df, rxns):
    df = df.copy()[["reaction", "metabolite", "flux"]]
    add = pd.DataFrame({
        "reaction": rxns[~rxns.isin(df.reaction)],
        "metabolite": rxns[~rxns.isin(df.reaction)].str.replace("EX_", ""),
        "flux": 1e-6})
    return pd.concat([df, add])

def test_single(df, v, ref):
    if df.flux.mean() < 1e-4:
        res = [float("nan"), float("nan")]
    else:
        res = mannwhitneyu(
            df.flux[df[v] == ref],
            df.flux[df[v] != ref]
        )
    res = list(res)
    res.append(df.shape[0])
    return pd.Series(res, index=["U", "pval", "n"])


def fdr(p):
    """Benjamini-Hochberg p-value correction for multiple hypothesis testing."""
    p = np.asfarray(p)
    by_descend = p.argsort()[::-1]
    by_orig = by_descend.argsort()
    steps = float(len(p)) / np.arange(len(p), 0, -1)
    q = np.minimum(1, np.minimum.accumulate(steps * p[by_descend]))
    return q[by_orig]


def test_production(output_dir: str,
                    results: MicomResultsDirectory,
                    metadata: CategoricalMetadataColumn):
    """Test for differential metabolite production."""
    template = env.get_template("tests.html")
    exchanges = results.exchange_fluxes.view(pd.DataFrame)
    exchanges = exchanges[
        (exchanges.taxon != "medium")
        & (exchanges.direction == "export")
    ]
    rxns = pd.Series(exchanges.reaction.unique())
    fluxes = exchanges.groupby(["sample_id", "taxon", "abundance"]).apply(
        lambda x: augment(x, rxns)
    ).reset_index()
    meta = metadata.to_dataframe()
    variable = meta.columns[0]
    meta["sample_id"] = meta.index
    tot_flux = fluxes.groupby(["metabolite", "sample_id"]).apply(
        lambda df: sum(df.flux * df.abundance)
    ).reset_index()
    tot_flux.columns = ["metabolite", "sample_id", "flux"]
    tot_flux = pd.merge(tot_flux, meta, on="sample_id")
    ref = tot_flux[variable].unique()[0]
    tests = tot_flux.groupby("metabolite").apply(
        lambda df: test_single(df, variable, ref)
    ).reset_index()
    tests["variable"] = variable
    tests.loc[tests.pval.notnull(), "qval"] = fdr(tests.pval[tests.pval.notnull()])
    tests.sort_values(by="pval", inplace=True)
    data_loc = path.join(output_dir, "tests.csv")
    tests.to_csv(data_loc)
    template.stream(
        fluxes=tot_flux.to_json(orient="records"),
        tests=tests.to_html(classes=["table", "is-hoverable"], border=0),
        metabolites=json.dumps(list(tests.metabolite.unique())),
        variable=variable,
        width=400,
        height=300
    ).dump(path.join(output_dir, "index.html"))


