"""Test if micom simulation works."""

import os.path as path
import pandas as pd
import qiime2 as q2
import q2_micom as q2m
from q2_micom.tests import this_dir

this_dir = q2m.tests.this_dir

medium = q2.Artifact.load(path.join(this_dir, "data", "medium.qza")).view(
    pd.DataFrame
)
models = q2.Artifact.load(path.join(this_dir, "data", "build.qza"))

res = q2m.grow(
    models.view(q2m._formats_and_types.CommunityModelDirectory),
    medium
)


def test_growth_rates():
    gcs = res.growth_rates.view(pd.DataFrame)
    assert "growth_rate" in gcs.columns
    assert "sample_id" in gcs.columns
    assert all(gcs.growth_rate > 1e-6)


def test_exchanges():
    ex = res.exchange_fluxes.view(pd.DataFrame)
    assert "reaction" in ex.columns
    assert ex.reaction.str.startswith("EX_").all()


def test_feasible_exchanges():
    ex = res.exchange_fluxes.view(pd.DataFrame)
    ex = ex[(ex.taxon == "medium") & (ex.direction == "import")]
    ex["bound"] = medium.loc[ex.reaction, "flux"].values
    ex = ex.dropna()
    assert all(ex.flux < ex.bound + 1e-6)
