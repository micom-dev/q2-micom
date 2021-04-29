"""Test if tradeoff analysis works."""

import numpy as np
import os.path as path
import pandas as pd
import pytest
import qiime2 as q2
import q2_micom as q2m

this_dir = q2m.tests.this_dir

medium = q2.Artifact.load(path.join(this_dir, "data", "medium.qza")).view(pd.DataFrame)
models = q2.Artifact.load(path.join(this_dir, "data", "build.qza"))

res = q2m.tradeoff(models.view(q2m._formats_and_types.CommunityModelDirectory), medium)


def test_tradeoff_values():
    assert np.allclose(res.tradeoff.min(), 0.1)
    assert np.allclose(res.tradeoff.max(), 1.0)
    assert res.tradeoff.nunique() == 10


def test_growth_rates():
    low = res.growth_rate[res.tradeoff == 0.1]
    high = res.growth_rate[res.tradeoff == 1.0]
    assert low.sum() < high.sum()


def test_sane_tradeoff():
    with pytest.raises(ValueError):
        q2m.tradeoff(
            models.view(q2m._formats_and_types.CommunityModelDirectory),
            medium,
            tradeoff_min=0.5,
            tradeoff_max=0.4,
        )


def test_artifact(tmpdir):
    out = str(tmpdir.join("tradeoff.qza"))
    art = q2.Artifact.import_data("TradeoffResults", res)
    art.save(out)
    assert path.exists(out)
    art = q2.Artifact.load(out)
    assert art.type == q2m._formats_and_types.TradeoffResults
    results = art.view(pd.DataFrame)
    assert isinstance(results, pd.DataFrame)
    assert "sample_id" in results.columns
