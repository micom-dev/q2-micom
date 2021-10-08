"""Test if micom simulation works."""

import os.path as path
import pandas as pd
import qiime2 as q2
import q2_micom as q2m
from micom.workflows.core import GrowthResults
from q2_micom._formats_and_types import MicomResults
from q2_micom.tests import this_dir

this_dir = q2m.tests.this_dir

medium = q2.Artifact.load(path.join(this_dir, "data", "medium.qza")).view(pd.DataFrame)
models = q2.Artifact.load(path.join(this_dir, "data", "build.qza"))

res = q2m.grow(models.view(q2m._formats_and_types.CommunityModelDirectory), medium)


def test_strategies():
    for s in ["minimal uptake", "pFBA", "none"]:
        res = q2m.grow(
            models.view(q2m._formats_and_types.CommunityModelDirectory),
            medium,
            strategy=s,
        )
        gcs = res.growth_rates
        assert "growth_rate" in gcs.columns
        assert "sample_id" in gcs.columns
        assert all(gcs.growth_rate > 1e-6)


def test_growth_rates():
    gcs = res.growth_rates
    assert "growth_rate" in gcs.columns
    assert "sample_id" in gcs.columns
    assert all(gcs.growth_rate > 1e-6)


def test_exchanges():
    ex = res.exchanges
    assert "reaction" in ex.columns
    assert ex.reaction.str.startswith("EX_").all()


def test_feasible_exchanges():
    ex = res.exchanges
    ex = ex[(ex.taxon == "medium") & (ex.direction == "import")]
    ex["bound"] = medium.loc[ex.reaction, "flux"].values
    ex = ex.dropna()
    assert all(ex.flux < ex.bound + 1e-6)


def test_artifact(tmpdir):
    out = str(tmpdir.join("growth.qza"))
    art = q2.Artifact.import_data("MicomResults", res)
    art.save(out)
    assert path.exists(out)
    art = q2.Artifact.load(out)
    assert art.type == MicomResults
    results = art.view(GrowthResults)
    assert isinstance(results, GrowthResults)
