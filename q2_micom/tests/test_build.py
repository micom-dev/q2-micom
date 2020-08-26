"""Test if DB construction works."""

import biom
import micom
import os.path as path
import pandas as pd
import qiime2 as q2
import q2_micom as q2m

this_dir = q2m.tests.this_dir

table = q2.Artifact.load(path.join(this_dir, "data", "table.qza")).view(
    biom.Table
)
taxa = q2.Artifact.load(path.join(this_dir, "data", "taxa.qza")).view(
    pd.Series
)
models = q2.Artifact.load(path.join(this_dir, "data", "species_models.qza"))


def test_build():
    d = q2m.build(
        table,
        taxa,
        models.view(q2m._formats_and_types.JSONDirectory),
        1,
        0.01,
        False
    )
    manifest = d.manifest.view(pd.DataFrame)
    print(manifest.T)
    assert manifest.shape[0] == 3
    for sa in manifest.sample_id.unique():
        com = micom.load_pickle(d.model_files.path_maker(model_id=sa))
        assert isinstance(com, micom.Community)
        assert len(com.reactions) > 3 * 95
        assert len(com.abundances) == 3
