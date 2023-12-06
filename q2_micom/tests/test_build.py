"""Test if DB construction works."""

import biom
import micom
import os.path as path
import pandas as pd
import qiime2 as q2
import q2_micom as q2m
from q2_micom._formats_and_types import CommunityModels, Pickle, CommunityModelDirectory

this_dir = q2m.tests.this_dir

table = q2.Artifact.load(path.join(this_dir, "data", "table.qza")).view(biom.Table)
taxa = q2.Artifact.load(path.join(this_dir, "data", "taxa.qza")).view(pd.Series)
models = q2.Artifact.load(path.join(this_dir, "data", "species_models.qza"))


def test_build():
    d = q2m.build(
        table, taxa, models.view(q2m._formats_and_types.JSONDirectory), 1, 0.01, True
    )
    manifest = d.manifest.view(pd.DataFrame)
    assert manifest.shape[0] == 3
    for sa in manifest.sample_id.unique():
        com = micom.load_pickle(d.model_files.path_maker(model_id=sa))
        assert isinstance(com, micom.Community)
        assert len(com.reactions) > 3 * 95
        assert len(com.abundances) == 3


def test_solvers():
    for solver in ["cplex", "hybrid", "auto"]:
        d = q2m.build(
            table,
            taxa,
            models.view(q2m._formats_and_types.JSONDirectory),
            1,
            0.01,
            False,
            solver,
        )
        manifest = d.manifest.view(pd.DataFrame)
        assert manifest.shape[0] == 3
        for sa in manifest.sample_id.unique():
            com = micom.load_pickle(d.model_files.path_maker(model_id=sa))
            assert isinstance(com, micom.Community)
            assert len(com.reactions) > 3 * 95
            assert len(com.abundances) == 3


def test_artifact(tmpdir):
    d = q2m.build(
        table, taxa, models.view(q2m._formats_and_types.JSONDirectory), 1, 0.01, False
    )
    out = str(tmpdir.join("models.qza"))
    art = q2.Artifact.import_data("CommunityModels[Pickle]", d)
    art.save(out)
    assert path.exists(out)
    art = q2.Artifact.load(out)
    assert art.type == CommunityModels[Pickle]
    manifest = art.view(CommunityModelDirectory).manifest.view(pd.DataFrame)
    assert isinstance(manifest, pd.DataFrame)
    assert "sample_id" in manifest.columns
