"""Test if visualizations work."""

from micom.workflows import GrowthResults
import os.path as path
import pandas as pd
import qiime2 as q2
import q2_micom as q2m
from tempfile import TemporaryDirectory

this_dir = q2m.tests.this_dir

results = q2.Artifact.load(path.join(this_dir, "data", "growth.qza"))


def test_growth_plots():
    r = results.view(GrowthResults)
    mcol = q2.Metadata.load(path.join(this_dir, "data", "metadata.tsv")).get_column(
        "status"
    )
    with TemporaryDirectory(prefix="q2-micom-") as d:
        q2m.plot_growth(str(d), r)
        assert q2m.tests.check_viz(str(d))
        q2m.plot_growth(str(d), r, metadata=mcol)
        assert q2m.tests.check_viz(str(d))


def test_exchanges_per_sample():
    r = results.view(GrowthResults)
    with TemporaryDirectory(prefix="q2-micom-") as d:
        q2m.exchanges_per_sample(str(d), r)
        assert q2m.tests.check_viz(str(d))


def test_exchanges_per_taxon():
    r = results.view(GrowthResults)
    mcol = q2.Metadata.load(path.join(this_dir, "data", "metadata.tsv")).get_column(
        "status"
    )
    with TemporaryDirectory(prefix="q2-micom-") as d:
        q2m.exchanges_per_taxon(str(d), r)
        assert q2m.tests.check_viz(str(d))
        q2m.exchanges_per_taxon(str(d), r, metadata=mcol)
        assert q2m.tests.check_viz(str(d))


def test_plot_tradeoff():
    tradeoff = q2.Artifact.load(path.join(this_dir, "data", "tradeoff.qza"))
    t = tradeoff.view(pd.DataFrame)
    with TemporaryDirectory(prefix="q2-micom-") as d:
        q2m.plot_tradeoff(str(d), t)
        assert q2m.tests.check_viz(str(d))


def test_association():
    large = q2.Artifact.load(path.join(this_dir, "data", "growth.qza"))
    r = large.view(GrowthResults)
    mcol = q2.Metadata.load(path.join(this_dir, "data", "metadata.tsv")).get_column(
        "status"
    )
    with TemporaryDirectory(prefix="q2-micom-") as d:
        q2m.association(str(d), r, mcol, fdr_threshold=0.1)
        assert q2m.tests.check_viz(str(d))
    with TemporaryDirectory(prefix="q2-micom-") as d:
        q2m.association(str(d), r, mcol, flux_type="import", fdr_threshold=0.3)
        assert q2m.tests.check_viz(str(d))
