"""Test if filtering works."""

import os.path as path
import pandas as pd
from micom.workflows.core import GrowthResults
import pytest
import qiime2 as q2
import q2_micom as q2m
from q2_micom._formats_and_types import CommunityModelDirectory
from q2_micom.tests import this_dir

this_dir = q2m.tests.this_dir

medium = q2.Artifact.load(path.join(this_dir, "data", "medium.qza")).view(pd.DataFrame)
models = q2.Artifact.load(path.join(this_dir, "data", "build.qza"))
results = q2m.grow(models.view(CommunityModelDirectory), medium)
metadata = pd.DataFrame(
    {"group": ["a", "b", "c"], "value": [1, 2, 3]},
    index=["sample_1", "sample_2", "sample_3"],
)
metadata.index.name = "id"


def has_nsamples(results, n):
    """Check if growth results have expected no samples."""
    n_rates = results.growth_rates.sample_id.nunique()
    n_exchanges = results.exchanges.sample_id.nunique()
    return n_rates == n and n_exchanges == n


def test_filter_models_metadata():
    filtered = q2m.filter_models(
        models.view(CommunityModelDirectory), q2.Metadata(metadata.iloc[0:2])
    )
    assert filtered.manifest.view(pd.DataFrame).shape[0] == 2

    filtered = q2m.filter_models(
        models.view(CommunityModelDirectory),
        q2.Metadata(metadata.iloc[0:2]),
        exclude=True,
    )
    assert filtered.manifest.view(pd.DataFrame).shape[0] == 1

    with pytest.raises(ValueError):
        q2m.filter_models(
            models.view(CommunityModelDirectory), q2.Metadata(metadata), exclude=True
        )


def test_filter_models_query():
    filtered = q2m.filter_models(
        models.view(CommunityModelDirectory),
        q2.Metadata(metadata),
        query="group == 'a'",
    )
    assert filtered.manifest.view(pd.DataFrame).shape[0] == 1

    filtered = q2m.filter_models(
        models.view(CommunityModelDirectory),
        q2.Metadata(metadata.iloc[0:2]),
        query="group == 'a'",
        exclude=True,
    )
    assert filtered.manifest.view(pd.DataFrame).shape[0] == 2

    filtered = q2m.filter_models(
        models.view(CommunityModelDirectory), q2.Metadata(metadata), query="value > 2"
    )
    assert filtered.manifest.view(pd.DataFrame).shape[0] == 1

    filtered = q2m.filter_models(
        models.view(CommunityModelDirectory),
        q2.Metadata(metadata),
        query="value > 2",
        exclude=True,
    )
    assert filtered.manifest.view(pd.DataFrame).shape[0] == 2

    with pytest.raises(ValueError):
        q2m.filter_models(
            models.view(CommunityModelDirectory),
            q2.Metadata(metadata),
            query="value > 3",
        )


def test_filter_results_metadata():
    r = results
    filtered = q2m.filter_results(r, q2.Metadata(metadata.iloc[0:2]))
    assert has_nsamples(filtered, 2)

    filtered = q2m.filter_results(r, q2.Metadata(metadata.iloc[0:2]), exclude=True)
    assert has_nsamples(filtered, 1)

    with pytest.raises(ValueError):
        q2m.filter_results(r, q2.Metadata(metadata), exclude=True)


def test_filter_results_query():
    r = results
    filtered = q2m.filter_results(r, q2.Metadata(metadata), query="group == 'a'")
    assert has_nsamples(filtered, 1)

    filtered = q2m.filter_results(
        r, q2.Metadata(metadata.iloc[0:2]), query="group == 'a'", exclude=True
    )
    assert has_nsamples(filtered, 2)

    filtered = q2m.filter_results(r, q2.Metadata(metadata), query="value > 2")
    assert has_nsamples(filtered, 1)

    filtered = q2m.filter_results(
        r, q2.Metadata(metadata), query="value > 2", exclude=True
    )
    assert has_nsamples(filtered, 2)

    with pytest.raises(ValueError):
        q2m.filter_results(r, q2.Metadata(metadata), query="value > 3")
