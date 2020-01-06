"""Build a database of organism metabolic models."""

from cobra.io import read_sbml_model, save_json_model
from micom.util import join_models
import os
from os import path
from tqdm import tqdm
from qiime2 import Metadata
from q2_micom._formats_and_types import JSONDirectory, REQ_FIELDS


def reduce_group(df):
    new = df.iloc[0, :]
    new["file"] = "|".join(df.file.astype(str))
    return new


def db(meta: Metadata, folder: str, rank: str = "genus") -> JSONDirectory:
    """Create a model database from a set of SBML files."""
    meta = meta.to_dataframe()
    meta.columns = meta.columns.str.lower()
    if not REQ_FIELDS.isin(meta.columns).all():
        raise ValueError("Metadata File needs to have the following "
                         "columns %s." % ", ".join(REQ_FIELDS))
    meta["id"] = meta.index
    files = os.listdir(folder)
    meta["file"] = meta.id + ".xml"
    bad = meta.file.apply(lambda x: x not in files)
    if any(bad):
        raise ValueError("The following models are in the Metadata but not "
                         "in the folder: %s" % meta.file[bad])

    meta = (
        meta.groupby(rank).apply(reduce_group).reset_index(drop=True)
    )
    meta.index = meta[rank]

    json_dir = JSONDirectory()
    for tid, row in tqdm(meta.iterrows(), unit="taxa", total=meta.shape[0]):
        new_path = str(json_dir.sbml_files.path_maker(model_id=tid))
        files = [path.join(folder, r) for r in row["file"].split("|")]
        if len(files) > 1:
            mod = join_models(files, id=tid)
            save_json_model(mod, new_path)
        else:
            mod = read_sbml_model(path.join(folder, row["file"]))
        save_json_model(mod, new_path)
    meta["file"] = meta.index + ".json"
    meta["id"] = meta.index
    meta.to_csv(json_dir.manifest.path_maker(), index=False)

    return json_dir
