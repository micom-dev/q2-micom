"""Test if minimal medium works."""

import biom
import micom
import os.path as path
import pandas as pd
import qiime2 as q2
import q2_micom as q2m

this_dir = q2m.tests.this_dir

models = q2.Artifact.load(path.join(this_dir, "data", "build.qza"))

medium_high = q2m._medium.minimal_medium(
    models.view(q2m._formats_and_types.CommunityModelDirectory), 0.5
)

medium_low = q2m._medium.minimal_medium(
    models.view(q2m._formats_and_types.CommunityModelDirectory), 0.1
)


def test_medium():
    assert "reaction" in medium_high.columns
    assert "flux" in medium_high.columns
    assert all(medium_high.flux > 1e-6)


def test_sane_medium():
    assert medium_high.flux.sum() > medium_low.flux.sum()
