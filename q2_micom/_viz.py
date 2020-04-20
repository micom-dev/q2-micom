"""Visualizers for MICOM results."""

from fastcluster import linkage
from scipy.cluster.hierarchy import leaves_list
from jinja2 import Environment, PackageLoader, select_autoescape
import json
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from os import path
from q2_micom._formats_and_types import MicomResultsDirectory
from qiime2 import MetadataColumn
from sklearn.model_selection import (
    cross_val_predict,
    cross_val_score,
    LeaveOneOut,
)
from sklearn.linear_model import (
    LogisticRegressionCV,
    LassoCV,
    LogisticRegression,
    Lasso,
)
from sklearn.preprocessing import StandardScaler
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
    min_dist: float = 0.1,
) -> None:
    """Plot the exchange fluxes."""
    template = env.get_template("umap.html")
    data_loc = path.join(output_dir, "umap.csv")
    exchanges = results.exchange_fluxes.view(pd.DataFrame)
    exchanges = exchanges[
        (exchanges.taxon != "medium") & (exchanges.direction == direction)
    ]
    exchanges["flux"] = exchanges.flux.abs() * exchanges.abundance
    mat = exchanges.pivot_table(
        values="flux",
        index=["sample_id", "taxon"],
        columns="reaction",
        fill_value=0,
    )
    umapped = UMAP(min_dist=min_dist, n_neighbors=n_neighbors).fit_transform(
        mat.values
    )
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
    tradeoff = (
        growth.groupby(["tradeoff", "sample_id"])
        .apply(
            lambda df: pd.Series(
                {
                    "n_taxa": df.shape[0],
                    "n_growing": df[df.growth_rate > 1e-6].shape[0],
                    "fraction_growing": (
                        df[df.growth_rate > 1e-6].shape[0] / df.shape[0]
                    ),
                }
            )
        )
        .reset_index()
    )
    template.stream(
        growth=growth.to_json(orient="records"),
        tradeoff=tradeoff.to_json(orient="records"),
        extent=[growth.log_growth_rate.min(), growth.log_growth_rate.max()],
        width=400,
        height=300,
    ).dump(path.join(output_dir, "index.html"))


def fit_phenotype(
    output_dir: str,
    results: MicomResultsDirectory,
    metadata: MetadataColumn,
    variable_type: str = "binary",
    flux_type: str = "production",
    min_coef: float = 0.01,
):
    """Test for differential metabolite production."""
    template = env.get_template("tests.html")
    exchanges = results.exchange_fluxes.view(pd.DataFrame)

    if flux_type == "import":
        exchanges = exchanges[
            (exchanges.taxon == "medium") & (exchanges.direction == "import")
        ]
        exchanges["flux"] = exchanges.flux.abs()
    else:
        exchanges = exchanges[
            (exchanges.taxon != "medium") & (exchanges.direction == "export")
        ]
        exchanges = (
            exchanges.groupby(["reaction", "metabolite", "sample_id"])
            .apply(
                lambda df: pd.Series(
                    {"flux": sum(df.abundance * df.flux.abs())}
                )
            )
            .reset_index()
        )
    exchanges.to_csv(path.join(output_dir, "fluxes.csv"))
    exchanges.loc[exchanges.flux < 1e-6, "flux"] = 1e-6
    meta = metadata.to_dataframe()
    variable = meta.columns[0]
    if variable_type == "binary" and meta[variable].nunique() != 2:
        raise ValueError(
            "Binary variables must have exactly two unique values, yours "
            "has: %s." % ", ".join(meta[variable].unique())
        )
    elif variable_type == "continuous" and not is_numeric_dtype(
        meta[variable]
    ):
        raise ValueError(
            "Continuous variables must have a numeric type, but yours is"
            " of type `%s`." % meta[variable].dtype
        )

    fluxes = exchanges.pivot_table(
        index="sample_id", columns="metabolite", values="flux", fill_value=1e-6
    )
    fluxes = fluxes.applymap(np.log)
    meta = meta.loc[fluxes.index]
    scaled = StandardScaler().fit_transform(fluxes)
    if variable_type == "binary":
        model = LogisticRegressionCV(
            penalty="l1",
            scoring="accuracy",
            solver="liblinear",
            Cs=np.power(10.0, np.arange(-6, 4, 0.5)),
            max_iter=10000,
        )
        fit = model.fit(scaled, meta[variable])
        model = LogisticRegression(
            penalty="l1", solver="liblinear", C=fit.C_[0], max_iter=10000,
        )
    else:
        model = LassoCV()
        fit = model.fit(scaled, meta[variable])
        model = Lasso(alpha=fit.alpha_[0])
    fit = model.fit(scaled, meta[variable])
    score = cross_val_score(
        model, X=scaled, y=meta[variable], cv=LeaveOneOut()
    )
    score = [np.mean(score), np.std(score)]
    score.append(model.score(scaled, meta[variable]))

    coefs = pd.DataFrame(
        {"coef": fit.coef_[0, :], "metabolite": fluxes.columns}
    )

    if all(coefs.coef.abs() < min_coef):
        raise RuntimeError(
            "Unfortunately no metabolite flux was predictive for the "
            "chosen phenotype and a cutoff of %g :(" % min_coef
        )

    coefs.to_csv(path.join(output_dir, "coefficients.csv"))
    coefs = coefs[coefs.coef.abs() > min_coef].sort_values(by="coef")
    predicted = cross_val_predict(
        model, scaled, meta[variable], cv=LeaveOneOut()
    )
    fitted = pd.DataFrame(
        {"real": meta[variable], "predicted": predicted}, index=meta.index
    )

    exchanges = exchanges.loc[
        exchanges.metabolite.isin(coefs.metabolite.values)
    ]
    exchanges["meta"] = meta.loc[exchanges.sample_id, variable].values
    var_type = "nominal" if variable_type == "binary" else "quantitative"

    template.stream(
        fitted=fitted.to_json(orient="records"),
        coefs=coefs.to_json(orient="records"),
        exchanges=exchanges.to_json(orient="records"),
        metabolites=json.dumps(coefs.metabolite.tolist()),
        variable=variable,
        type=var_type,
        score=score,
        width=400,
        height=300,
        cheight=2 * coefs.shape[0],
        cwidth=8 * coefs.shape[0],
    ).dump(path.join(output_dir, "index.html"))
