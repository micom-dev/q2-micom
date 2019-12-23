"""Build a database of organism metabolic models."""

import os
from os import path
from shutil import copyfile
from qiime2 import Metadata
from q2_micom._formats_and_types import SBMLDirectory, REQ_FIELDS


def make_db(meta: Metadata, folder: str) -> SBMLDirectory:
    """Create a model database from a set of SBML files."""
    meta = meta.to_dataframe()
    meta.columns = meta.columns.str.lower()
    if not REQ_FIELDS.isin(meta.columns).all():
        raise ValueError("Metadata File needs to have the following "
                         "columns %." % ", ".join(REQ_FIELDS))
    meta["id"] = meta.index
    files = os.listdir(folder)
    model_files = meta.id + ".xml"
    bad = model_files.apply(lambda x: x not in files)
    if any(bad):
        raise ValueError("The following models are in the Metadata but not "
                         "in the folder: %s" % model_files[bad])

    sbml_dir = SBMLDirectory()
    for mod_id in meta.id:
        new_path = sbml_dir.sbml_files.path_maker(model_id=mod_id)
        copyfile(path.join(folder, mod_id + ".xml"), new_path)
    meta.to_csv(sbml_dir.manifest.path_maker(), index=False)

    return sbml_dir
