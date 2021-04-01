"""Test if DB construction works."""

import micom
import numpy as np
import os.path as path
import pandas as pd
import qiime2 as q2
import q2_micom as q2m

this_dir = q2m.tests.this_dir

meta = pd.read_csv(path.join(this_dir, "data", "test_models.tsv"), sep="\t")
meta.file = [path.join(this_dir, "data", f) for f in meta.file]
meta.set_index("id", inplace=True)
meta = q2.Metadata(meta)


def test_species():
    models = q2m.db(meta, "species", 1)
    files = models.manifest.view(pd.DataFrame)
    assert files.shape[0] == 3
    assert files.file[0] == "Escherichia_coli_1.json"
    cobra_model = micom.util.load_model(
        str(models.json_files.path_maker(model_id=files.id[0]))
    )
    assert len(cobra_model.reactions) == 95
    assert np.allclose(
        cobra_model.optimize().objective_value, 0.874, rtol=1e-3, atol=1e-3
    )


def test_genus():
    models = q2m.db(meta, "genus", 1)
    files = models.manifest.view(pd.DataFrame)
    assert files.shape[0] == 1
    assert files.file[0] == "Escherichia.json"
    cobra_model = micom.util.load_model(
        str(models.json_files.path_maker(model_id=files.id[0]))
    )
    # one additional reaction due to averaged biomass
    assert len(cobra_model.reactions) == 96
    assert np.allclose(
        cobra_model.optimize().objective_value, 0.874, rtol=1e-3, atol=1e-3
    )
